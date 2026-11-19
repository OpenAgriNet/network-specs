#!/usr/bin/env python3
"""Validate directional contracts and supplied fixtures; never call providers."""
import copy
import json
import subprocess
from urllib.parse import unquote
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
checks = 0
# These fixture assertions cover the original seven OAN integration operations.
# Native upstream contracts may use GET, GraphQL, or inline response schemas.
directories = [ROOT/'api/external'/service/'v0.2' for service in
               ('pm-kisan/application', 'pm-kisan/grievance', 'pmfby/grievance')]
operation_ids = set()
for api in directories:
    document = yaml.safe_load((api/'openapi.yaml').read_text())
    components = document['components']['schemas']
    schemas = {name: value for name, value in components.items() if name.endswith(('Request', 'Response'))}
    validators = {}
    for name, schema in schemas.items():
        Draft202012Validator.check_schema(schema)
        validators[name] = Draft202012Validator(schema, format_checker=FormatChecker())
    for example in (api/'examples').glob('*.json'):
        data = json.loads(example.read_text())
        accepted = [name for name, validator in validators.items() if validator.is_valid(data)]
        assert accepted, (example.name, 'accepted by no directional contract')
        checks += 1
        # Request-only secrets/contact fields must not fit any response schema.
        if 'applicantMobile' in data or 'response' in data.get('challenge', {}):
            assert not any(name.endswith('Response') for name in accepted), (example.name, accepted)
            checks += 1
    for name, validator in validators.items():
        assert not validator.is_valid({}), name
        checks += 1
    if 'PMKISANApplicationStatusResponse' in validators:
        empty = json.loads((api/'examples/PMKISANApplicationStatus-response.json').read_text())
        empty['application'] = {}
        assert not validators['PMKISANApplicationStatusResponse'].is_valid(empty)
        checks += 1
    for operation in document['paths'].values():
        operation = operation['post']
        assert operation['operationId'] not in operation_ids
        operation_ids.add(operation['operationId'])
        for schema in [operation['requestBody']['content']['application/json']['schema'],
                       operation['responses']['200']['content']['application/json']['schema']]:
            assert schema['$ref'].rsplit('/', 1)[-1] in schemas
            checks += 1
assert len(operation_ids) == 7, operation_ids

# Check all native contracts, not only the first three providers. Query/path
# parameters are the request contract of a GET; never add a fictitious body.
def resolve(doc, reference):
    target = doc
    assert reference.startswith('#/')
    for part in reference[2:].split('/'):
        target = target[part.replace('~1', '/').replace('~0', '~')]
    return target


def validate_examples(media, registry, uri, direction):
    schema = media['schema']
    assert set(schema) == {'$ref'}, (direction, schema)
    validator = Draft202012Validator({'$ref': uri+schema['$ref']}, registry=registry,
                                     format_checker=FormatChecker())
    examples = ([media['example']] if 'example' in media else
                [item['value'] for item in media.get('examples', {}).values()])
    assert examples, (uri, direction, 'missing example')
    for value in examples:
        validator.validate(value)
    assert not validator.is_valid({}), (uri, direction, 'untyped empty object accepted')
    assert not validator.is_valid('not an envelope'), (uri, direction)
    return len(examples)+2


for file in sorted([*(ROOT/'api/external').glob('*/*/v0.2/openapi.yaml'),
                    *(ROOT/'api/examples').glob('*/v0.2/openapi.yaml')]):
    if file.parent in directories:
        continue
    doc = yaml.safe_load(file.read_text())
    registry = Registry().with_resource(file.as_uri(), Resource.from_contents(doc, default_specification=DRAFT202012))
    for path, item in doc['paths'].items():
        for method, op in item.items():
            if method not in ('post', 'get'):
                continue
            assert op['operationId'] not in operation_ids
            operation_ids.add(op['operationId'])
            if method == 'post':
                checks += validate_examples(op['requestBody']['content']['application/json'],
                                            registry, file.as_uri(), 'request')
            else:
                assert 'requestBody' not in op
                for param in item.get('parameters', []) + op.get('parameters', []):
                    param = resolve(doc, param['$ref']) if '$ref' in param else param
                    assert param['in'] in ('path', 'query', 'header') and 'schema' in param
                    if param['in'] == 'path':
                        assert param['required'] and '{'+param['name']+'}' in path
                    if 'example' in param:
                        # A referenced parameter schema resolves inside its OpenAPI
                        # document, not relative to an isolated schema fragment.
                        schema = param['schema']
                        if '$ref' in schema:
                            schema = {'$ref': file.as_uri()+schema['$ref']}
                        Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()).validate(param['example'])
                        checks += 1
                    checks += 1
            for code, outcome in op['responses'].items():
                for link in outcome.get('links', {}).values():
                    target_ids = {entry['operationId'] for path_item in doc['paths'].values()
                                  for verb, entry in path_item.items() if verb in ('post', 'get')}
                    assert link['operationId'] in target_ids and link.get('description'), link
                    checks += 1
                if 'content' not in outcome:
                    assert code != '200' and outcome.get('description')
                    continue
                checks += validate_examples(outcome['content']['application/json'], registry, file.as_uri(), 'response')

# These listings have similar-looking neighbours with different inputs or
# results. Keep the chosen operation explicit even when both links resolve.
linked_reads = {
    'agmarknet-market-prices': ('agmarknet', 'agmarknet/market-prices', {
        'getSelectedMarketMandiPrices': {'statecode','districtcode','commoditycode','from_date','to_date'},
    }),
    'pmfby-insurance': ('pmfby', 'pmfby/insurance', {
        'listPmfbyInsurancePolicies': {'listType','farmerID','sssyID'},
        'listPmfbyInsuranceClaims': {'searchType','farmerID','season','year'},
    }),
}
for code, (publisher, service, expected) in linked_reads.items():
    file = ROOT/'api/external'/service/'v0.2/openapi.yaml'
    catalog = json.loads((ROOT/f'schema/examples/providers/v0.2/publish/{publisher}.json').read_text())
    descriptor, = [r['descriptor'] for c in catalog['message']['catalogs'] for r in c['resources']
                   if r['descriptor']['code'] == code]
    assert any(d['url'] == 'https://openagrinet.github.io/network-specs/'+file.relative_to(ROOT).as_posix()
               for d in descriptor['docs']), code
    doc = yaml.safe_load(file.read_text())
    actual = {}
    for item in doc['paths'].values():
        op = item['get']
        params = [resolve(doc,p['$ref']) if '$ref' in p else p for p in op['parameters']]
        actual[op['operationId']] = {p['name'] for p in params if p.get('required')}
    assert actual == expected, (code, actual)
    checks += 2

# Follow every local reference, including the old compatibility URLs.
def refs(node):
    if isinstance(node, dict):
        if '$ref' in node:
            yield node['$ref']
        for value in node.values():
            yield from refs(value)
    elif isinstance(node, list):
        for value in node:
            yield from refs(value)

for path in list((ROOT/'api').rglob('*.yaml')) + list((ROOT/'schema').glob('*/v0.2/attributes.yaml')):
    document = yaml.safe_load(path.read_text())
    for ref in refs(document):
        if ref.startswith(('http:', 'https:')):
            continue
        file, _, fragment = ref.partition('#')
        target = yaml.safe_load((path.parent/file).read_text()) if file else document
        for part in fragment.lstrip('/').split('/') if fragment else []:
            target = target[part.replace('~1', '/').replace('~0', '~')]
        checks += 1

origin = 'https://openagrinet.github.io/network-specs/'

def local_document(url):
    assert url.startswith(origin), url
    path, _, fragment = url[len(origin):].partition('#')
    file = ROOT/path
    document = yaml.safe_load(file.read_text())
    target = document
    for part in unquote(fragment).lstrip('/').split('/') if fragment else []:
        target = target[part.replace('~1', '/').replace('~0', '~')]
    return file, document, target

# Validate every inventory resource against the real versioned pack, plus the
# Beckn Descriptor and Document schemas referenced by these examples. Dependency
# snapshots are test-only; the published contracts continue to point upstream.
catalog_registry = Registry()
for pack_file in sorted((ROOT/'schema').glob('*/v0.2/attributes.yaml')):
    catalog_registry = catalog_registry.with_resource(
        origin+pack_file.relative_to(ROOT).as_posix(),
        Resource.from_contents(yaml.safe_load(pack_file.read_text()), default_specification=DRAFT202012))
for dependency, version, host in [('Descriptor','2.1','schema.beckn.io'), ('Document','2.0','schema.nfh.global')]:
    fixture = ROOT/'scripts/fixtures/beckn'/f'{dependency}-v{version}.yaml'
    catalog_registry = catalog_registry.with_resource(
        f'https://{host}/{dependency}/v{version}/attributes.yaml',
        Resource.from_contents(yaml.safe_load(fixture.read_text()), default_specification=DRAFT202012))

def validate_uri(uri, instance):
    Draft202012Validator({'$ref':uri}, registry=catalog_registry, format_checker=FormatChecker()).validate(instance)

example_dir = ROOT/'schema/examples/providers/v0.2'
codes = set()
published_examples = {}
for file in sorted((example_dir/'publish').glob('*.json')):
    publish = json.loads(file.read_text())
    assert publish['context']['action'] == 'catalog/publish'
    catalogs = publish['message']['catalogs']
    assert {d['catalogId'] for d in publish['message']['publishDirectives']} == {c['id'] for c in catalogs}
    for catalog in catalogs:
        for resource in catalog['resources']:
            attrs, desc = resource['resourceAttributes'], resource['descriptor']
            pack = attrs['@type'].removeprefix('openagrinet:')
            pack_url = origin+f'schema/{pack}/v0.2/'
            assert attrs['@context'] == pack_url+'context.jsonld', resource['id']
            validate_uri(pack_url+'attributes.yaml#/components/schemas/'+pack, attrs)
            validate_uri('https://schema.beckn.io/Descriptor/v2.1/attributes.yaml#/components/schemas/Descriptor', desc)
            code = desc['code']
            assert code not in codes, code
            codes.add(code)
            published_examples[resource['id']] = (catalog, resource)
            query = json.loads((example_dir/'discover'/f'{code}.json').read_text())
            assert query['context']['action'] == 'discover'
            expr = query['message']['intent']['filters']['expression']
            assert query['context']['schemaContext'] == [attrs['@context']+'#'+attrs['@type']]
            assert '@.resourceAttributes."@type" == '+json.dumps(attrs['@type']) in expr
            assert 'textSearch' not in query['message']['intent'] and 'descriptor.code' not in expr
            if attrs.get('subjectCategories'):
                assert '@.resourceAttributes.subjectCategories[*] == '+json.dumps(attrs['subjectCategories'][0]) in expr
            docs = {d['url'] for d in desc.get('docs', [])}
            for url in docs:
                _, spec, _ = local_document(url)
                assert spec['openapi'] == '3.1.1' and spec['paths']
            if attrs['informationMode'] == 'OnDemand':
                assert attrs.get('actions'), code
                for invalid_actions in (None, [], [{'action': 'select'}], [{'action': 'select', 'operationRef': origin+'api/openapi.yaml'}]):
                    invalid_attrs = {**attrs, 'actions': invalid_actions}
                    if invalid_actions is None:
                        del invalid_attrs['actions']
                    validator = Draft202012Validator({'$ref': pack_url+'attributes.yaml#/components/schemas/'+pack}, registry=catalog_registry)
                    assert not validator.is_valid(invalid_attrs), (code, invalid_actions)
                    checks += 1
            for action in attrs.get('actions', []):
                ref = action['operationRef']
                assert ref.partition('#')[0] in docs and '#/paths/' in ref, (code, ref)
                _, _, operation = local_document(ref)
                assert operation['operationId'] and operation['responses'], (code, ref)
                if 'schema' not in action:
                    continue
                url, component = action['schema'].split('#')
                assert ref.partition('#')[0] == url
                assert operation['requestBody']['content']['application/json']['schema']['$ref'] == '#'+component
                assert url in docs, action
                _, spec, _ = local_document(action['schema'])
                # The named request must be used by one operation in the
                # advertised document, not merely exist in components.schemas.
                ops = [operation for item in spec['paths'].values() for verb, operation in item.items()
                       if verb == 'post' and operation['requestBody']['content']['application/json']['schema'].get('$ref') == '#'+component]
                assert len(ops) == 1 and ops[0]['responses']['200']['content']['application/json']['schema']['$ref'], action
            checks += 5+len(docs)+len(attrs.get('actions', []))
assert codes and codes == {f.stem for f in (example_dir/'discover').glob('*.json')}
for response_file in sorted((example_dir/'on-discover').glob('*.json')):
    request = json.loads((example_dir/'discover'/response_file.name).read_text())
    response = json.loads(response_file.read_text())
    assert response['context']['action'] == 'on_discover'
    assert request['context']['transactionId'] == response['context']['transactionId']
    returned_codes = []
    for catalog in response['message']['catalogs']:
        for resource in catalog['resources']:
            published, original = published_examples[resource['id']]
            assert all(catalog[k] == published[k] for k in ('id', 'provider', 'bppId', 'bppUri'))
            assert resource == original, resource['id']
            returned_codes.append(resource['descriptor']['code'])
    assert response_file.stem in returned_codes
    checks += 3

generated = json.loads((ROOT/'_data/schema_packs.json').read_text())
for service in ('cropregistry', 'soilhealthcard', 'seedavailability', 'ffs-booking'):
    example = json.loads((ROOT/'schema/examples'/f'{service}-api-resource.json').read_text())
    attributes = example['resourceAttributes']
    assert attributes['@type'] == 'openagrinet:AgricultureResource'
    assert attributes['informationMode'] == 'OnDemand'
    assert set(attributes) <= {'@type', '@context', 'informationMode', 'subjectCategories', 'languages', 'actions'}
    file, document, _ = local_document(origin+'schema/AgricultureResource/v0.2/attributes.yaml')
    reg = Registry().with_resource(file.as_uri(), Resource.from_contents(document, default_specification=DRAFT202012))
    Draft202012Validator({'$ref':file.as_uri()+'#/components/schemas/AgricultureResource'}, registry=reg).validate(attributes)
    for link in example['descriptor']['docs']:
        _, contract, _ = local_document(link['url'])
        assert contract['paths'], service
    checks += 1
for pack in ('Grievance', 'SchemeApplication'):
    directory = ROOT/'schema'/pack/'v0.2'
    document = yaml.safe_load((directory/'attributes.yaml').read_text())
    root = document['components']['schemas'][pack]
    variants = []
    resources = [( (directory/'attributes.yaml').as_uri(), Resource.from_contents(document, default_specification=DRAFT202012))]
    assert root['allOf'][0]['$ref'] == f'#/components/schemas/{pack}Fields'
    assert len(root['allOf']) == 1 and root['unevaluatedProperties'] is False
    choices = [value for name, value in document['components']['schemas'].items()
               if name.endswith('Catalog') and '/api/external/' in value.get('$ref', '')]
    for member in choices:
        path, fragment = member['$ref'].split('#')
        assert path.startswith('../../../api/external/'), member
        target_path = (directory/path).resolve()
        api = yaml.safe_load(target_path.read_text())
        resources.append((target_path.as_uri(), Resource.from_contents(api, default_specification=DRAFT202012)))
        variant = api['components']['schemas'][fragment.split('/')[-1]]
        variants.append(variant)
        assert document['components']['schemas'][fragment.split('/')[-1]]['$ref'] == member['$ref']
        checks += 1
    registry = Registry().with_resources(resources)
    validator = Draft202012Validator({'$ref': (directory/'attributes.yaml').as_uri()+f'#/components/schemas/{pack}'}, registry=registry, format_checker=FormatChecker())
    api_by_scheme = {}
    for variant in variants:
        code = variant['properties']['scheme']['properties']['code']['const']
        api_by_scheme[code] = variant['externalDocs']['url']
        local_document(api_by_scheme[code])
        checks += 1
    examples = [json.loads(path.read_text()) for path in (directory/'examples').glob('*.json')]
    wrapper = json.loads((ROOT/'schema/examples'/f'{pack.lower()}-api-resource.json').read_text())
    examples.append(wrapper['resourceAttributes'])
    assert wrapper['descriptor']['docs'][0]['url'] == api_by_scheme[wrapper['resourceAttributes']['scheme']['code']]
    checks += 1
    for example in examples:
        errors = list(validator.iter_errors(example))
        assert not errors, f'{pack}: catalog example does not validate'
        checks += 1
        for action in example['actions']:
            url = action['schema']
            assert url.startswith(api_by_scheme[example['scheme']['code']] + '#'), url
            assert url.endswith('Request'), url
            _, api_document, request = local_document(url)
            request_name = url.rsplit('/', 1)[-1]
            response_name = request_name[:-len('Request')] + 'Response'
            assert response_name in api_document['components']['schemas']
            assert any(operation['post']['requestBody']['content']['application/json']['schema']['$ref'].endswith('/'+request_name)
                       for operation in api_document['paths'].values())
            Draft202012Validator.check_schema(request)
            checks += 1
    # Provider fixtures remain constrained by their own API catalogs, not the generic root.
    provider_only = Draft202012Validator({'oneOf': variants}, format_checker=FormatChecker())
    for example in examples:
        assert provider_only.is_valid(example)
        wrong_response = copy.deepcopy(example)
        wrong_response['actions'][0]['schema'] = wrong_response['actions'][0]['schema'].removesuffix('Request') + 'Response'
        assert not provider_only.is_valid(wrong_response), 'Provider catalog must reject response URIs as requests'
        checks += 2
    new_provider = copy.deepcopy(examples[0])
    new_provider['scheme'] = {'code': 'NEW-SCHEME', 'name': 'Illustrative new scheme'}
    new_provider['actions'] = [{'action': 'status', 'description': 'Read a case', 'schema': 'https://api.example.org/openapi.yaml#/components/schemas/ReadCaseRequest', 'attributesAt': '$.message.contract.commitments[0].commitmentAttributes'}]
    new_provider['actions'][0]['operationRef'] = 'https://api.example.org/openapi.yaml#/paths/~1cases/post'
    new_provider.pop('challenge', None)
    if pack == 'Grievance':
        new_provider['grievanceOptions'] = {'categories': [{'code': 'LOCAL-NEW-42', 'name': 'New category'}]}
    assert validator.is_valid(new_provider), 'New Provider codes and API URLs must need no root schema edit'
    assert not provider_only.is_valid(new_provider), 'Generic acceptance must not imply Provider API acceptance'
    for required in document['components']['schemas'][pack+'Fields']['required']:
        invalid = {k: v for k, v in new_provider.items() if k != required}
        assert not validator.is_valid(invalid), required
        checks += 1
    invalid_values = [
        {**new_provider, 'scheme': {'code': '', 'name': 'Empty code'}},
        {**new_provider, 'actions': []},
        {**new_provider, 'actions': [42]},
        {**new_provider, 'challenge': {'response': {'value': 'example-secret'}}},
        {**new_provider, 'applicantMobile': 'private-data'},
    ]
    for invalid in invalid_values:
        assert not validator.is_valid(invalid)
        checks += 1
    new_provider['challenge'] = {'methods': [{'method': 'OTP', 'channel': 'EMAIL', 'length': 6, 'valueType': 'ALPHANUMERIC'}]}
    assert validator.is_valid(new_provider)
    if pack == 'Grievance':
        new_provider['grievanceOptions']['categories'][0]['code'] = ''
        assert not validator.is_valid(new_provider)
    checks += 4
    page = generated[f'{pack}-v0.2']
    assert page['has_directional_fields'] is False
    assert {doc['url'] for doc in page['api_docs']} == set(api_by_scheme.values())
    assert 'leaves' not in page and page['generic_catalog']
    assert page['pack_fields'] and page['fields']
    if pack == 'Grievance':
        code_rows = [field for field in page['fields'] if field['path'] == 'scheme.code']
        assert len(code_rows) == 1 and not code_rows[0].get('applicability')
        assert len([field for field in page['fields'] if field['path'] == 'actions']) == 1
    checks += 1

# v0.1 published artifacts remain byte-identical to the baseline, including examples.
baseline = '2b5803476bda6a82b405e15099c7028208641b37'
for pack in ('Grievance', 'SchemeApplication'):
    prefix = f'schema/{pack}/v0.1/'
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', baseline, '--', prefix], cwd=ROOT, text=True).splitlines()
    actual = {str(path.relative_to(ROOT)) for path in (ROOT/prefix).rglob('*') if path.is_file()}
    assert actual == set(names), 'Published version file list changed'
    for name in names:
        assert (ROOT/name).read_bytes() == subprocess.check_output(['git', 'show', f'{baseline}:{name}'], cwd=ROOT), name
        checks += 1
print(f'{checks} API separation checks passed. No provider integration was tested.')
