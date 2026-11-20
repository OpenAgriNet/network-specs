#!/usr/bin/env python3
"""Validate directional contracts and supplied fixtures; never call providers."""
import copy
import html
import json
import subprocess
from urllib.parse import unquote, quote
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
checks = 0
external = ROOT/'api/external'
inventory = json.loads((external/'mappings-index.json').read_text())
mapping_paths = {(external/m['path']).resolve() for m in inventory['mappings']}
assert mapping_paths == {p.resolve() for p in external.glob('*/*/*/mappings/**/*.yaml')}
for spec_file in (ROOT/'api').rglob('openapi.yaml'):
    spec = yaml.safe_load(spec_file.read_text())
    def check_ref(schema):
        assert set(schema) == {'$ref'}, (spec_file, schema)
        prefix = '#/components/schemas/'
        assert schema['$ref'].startswith(prefix) and schema['$ref'][len(prefix):] in spec['components']['schemas']
    for item in spec['paths'].values():
        for method, op in item.items():
            if method not in ('get','post','put','patch','delete','options','head','trace'):
                continue
            if 'x-oan-mapping' in op:
                mapping = (spec_file.parent/op['x-oan-mapping']['href']).resolve()
                assert mapping in mapping_paths and mapping.is_file(), mapping
            for p in item.get('parameters', []) + op.get('parameters', []):
                if '$ref' in p:
                    p = spec['components']['parameters'][p['$ref'].split('/')[-1]]
                check_ref(p['schema'])
            for body in [op.get('requestBody', {})] + list(op['responses'].values()):
                for media in body.get('content', {}).values():
                    check_ref(media['schema'])
# These fixture assertions cover the original seven OAN integration operations.
# Native upstream contracts may use GET, GraphQL, or inline response schemas.
directories = [ROOT/'api/adapter'/service/'v0.2' for service in
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


def validate_examples(media, registry, uri, direction, schema_pointer, unknown_result=False):
    schema = media['schema']
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator({'$ref': uri+'#'+quote(schema_pointer, safe='/~')}, registry=registry,
                                     format_checker=FormatChecker())
    examples = ([media['example']] if 'example' in media else
                [item['value'] for item in media.get('examples', {}).values()])
    assert examples or unknown_result, (uri, direction, 'missing example')
    for value in examples:
        validator.validate(value)
    assert set(schema) == {'$ref'} and schema['$ref'].startswith('#/components/schemas/'), (uri, direction)
    assert not validator.is_valid('not an envelope'), (uri, direction)
    return len(examples)+2


for file in sorted([*(ROOT/'api/external').glob('*/*/v0.2/openapi.yaml'),
                    *(ROOT/'api/adapter').glob('*/v0.2/openapi.yaml')]):
    if file.parent in directories:
        continue
    doc = yaml.safe_load(file.read_text())
    native = file.is_relative_to(ROOT/'api/external')
    assert doc['info'].get('x-contract-role') == ('provider-native' if native else 'adapter-proposal'), file
    registry = Registry().with_resource(file.as_uri(), Resource.from_contents(doc, default_specification=DRAFT202012))
    for path, item in doc['paths'].items():
        for method, op in item.items():
            if method not in ('post', 'get'):
                continue
            assert op['operationId'] not in operation_ids
            operation_ids.add(op['operationId'])
            ptr = '/paths/'+path.replace('~','~0').replace('/','~1')+'/'+method
            for key in ('x-plaintext-request', 'x-plaintext-response'):
                if key in op:
                    Draft202012Validator.check_schema(op[key])
                    for value in op[key].get('examples', []):
                        Draft202012Validator(op[key]).validate(value)
                        checks += 1
            if method == 'post':
                for mime, media in op['requestBody']['content'].items():
                    checks += validate_examples(media, registry, file.as_uri(), 'request',
                                                ptr+'/requestBody/content/'+mime.replace('/','~1')+'/schema')
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
                for mime, media in outcome['content'].items():
                    checks += validate_examples(media, registry, file.as_uri(), 'response',
                                                ptr+'/responses/'+code+'/content/'+mime.replace('/','~1')+'/schema',
                                                unknown_result=op['operationId']=='analyzeNpssCropImage' and code=='200')

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
    catalog_file, = ROOT.glob(f'schema/*/v0.2/examples/{publisher}/catalog.json')
    catalog = json.loads(catalog_file.read_text())
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

example_dir = ROOT/'schema'
assert not list(example_dir.glob('*/v*/examples/*/*/index.html'))
for fixture in example_dir.glob('*/v0.2/examples/*.json'):
    for action in json.loads(fixture.read_text()).get('actions', []):
        assert '~1retrieveExample' not in action['operationRef'], fixture
        _, _, operation = local_document(action['operationRef'])
        assert operation['operationId'], fixture
codes = set()
requests = {}
published_examples = {}
for file in sorted(example_dir.glob('*/v0.2/examples/*/catalog.json')):
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
            overview = (ROOT/'schema/provider-walkthrough.html').read_text()
            section = overview.split(f'id="cap-{code}"', 1)[1].split('</article>', 1)[0]
            block = section.split('<summary>Structured discovery request</summary><pre><code>', 1)[1]
            query = requests[code] = json.loads(html.unescape(block.split('</code></pre>', 1)[0]))
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
template = example_dir/'Grievance/v0.2/examples/pmfby/pmfby-grievances/discover-request.json'
assert codes and requests['pmfby-grievances'] == json.loads(template.read_text())
for response_file in sorted(example_dir.glob('*/v0.2/examples/*/*/on-discover.json')):
    request = requests[response_file.parent.name]
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
    assert response_file.parent.name in returned_codes
    checks += 3

generated = json.loads((ROOT/'_data/schema_packs.json').read_text())
for service in ('cropregistry', 'soilhealthcard', 'seedavailability', 'ffs-booking'):
    example = json.loads((example_dir/'AgricultureResource/v0.2/examples/network'/f'{service}-api-resource.json').read_text())
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
               if name.endswith('Catalog') and '/api/adapter/' in value.get('$ref', '')]
    for member in choices:
        path, fragment = member['$ref'].split('#')
        assert path.startswith('../../../api/adapter/'), member
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
    wrapper = json.loads((example_dir/pack/'v0.2/examples/network'/f'{pack.lower()}-api-resource.json').read_text())
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
    assert {doc['url'] for doc in page['api_docs'] if '/api/adapter/' in doc['url']} == set(api_by_scheme.values())
    assert {url.replace('/api/adapter/', '/api/external/') for url in api_by_scheme.values()} <= {doc['url'] for doc in page['api_docs']}
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
