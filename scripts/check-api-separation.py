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

# Packs are served from the site; contracts are served from the branch until
# v0.2 is published. A URL resolves locally through whichever base it carries.
origin = 'https://openagrinet.github.io/network-specs/'
BASES = (
    'https://raw.githubusercontent.com/OpenAgriNet/network-specs/bv-migration/',
    'https://openagrinet.github.io/network-specs/',
)


def published(path):
    """The URL a catalog carries for a repo-relative path."""
    return ('https://raw.githubusercontent.com/OpenAgriNet/network-specs/bv-migration/'
            if path.startswith('api/') else
            'https://openagrinet.github.io/network-specs/') + path


def local_path(url):
    """The repo path a published URL names."""
    for base in BASES:
        if url.startswith(base):
            return url[len(base):]
    raise AssertionError(url)

checks = 0
external = ROOT/'api/external'
inventory = json.loads((external/'mappings-index.json').read_text())
mapping_paths = {(external/m['path']).resolve() for m in inventory['mappings']}
assert mapping_paths == {p.resolve() for p in external.glob('*/*/*/mappings/**/*.yaml')}
catalog_files = sorted(external.glob('*/catalog.json'))
assert catalog_files
for provider in (p for p in external.iterdir() if p.is_dir()):
    contracts = list(provider.glob('*/v*/openapi.yaml'))
    assert bool(contracts) == (provider/'catalog.json').is_file(), provider
    versions = list(provider.glob('*/v*'))
    if not contracts:
        placeholder = json.loads((provider/'catalog-placeholder.json').read_text())
        assert placeholder['status'] == 'placeholder' and placeholder['provider'] == provider.name
        assert 'message' not in placeholder and {provider/c['draft'] for c in placeholder['capabilities']} == {
            v/'openapi-draft.yaml' for v in versions}, provider
    else:
        assert not (provider/'catalog-placeholder.json').exists(), provider
    for version in versions:
        draft_path = version/'openapi-draft.yaml'
        assert draft_path.exists() != (version/'openapi.yaml').exists(), version
        if draft_path.exists():
            doc = yaml.safe_load(draft_path.read_text())
            assert doc['openapi'] == '3.1.1' and doc['x-draft']['needsConfirmation'], version
            traced = [m for m in inventory['mappings'] if (external/m['path']).is_relative_to(version) and m['status'] == 'source-traced']
            # A mapping can be deployed before its provider contract is verified.
            deployed = [m for m in inventory['mappings'] if (external/m['path']).is_relative_to(version) and m['status'] == 'existing']
            assert bool(doc['paths']) == bool(traced or deployed), version
            linked = set()
            draft_registry = Registry().with_resource(draft_path.as_uri(), Resource.from_contents(doc, default_specification=DRAFT202012))
            for path, methods in doc['paths'].items():
                for verb, operation in methods.items():
                    for body in [operation.get('requestBody', {}), *operation['responses'].values()]:
                        for media in body.get('content', {}).values():
                            validator = Draft202012Validator({'$ref': draft_path.as_uri()+media['schema']['$ref']}, registry=draft_registry)
                            assert media['examples'], (version, path)
                            for example in media['examples'].values():
                                validator.validate(example['value'])
                    for rel in operation['x-mappings']:
                        mapping_file = version/rel
                        mapping = yaml.safe_load(mapping_file.read_text())
                        if 'deployable' in mapping:
                            assert mapping['deployable'] is False and mapping['native']['method'].lower() == verb
                            assert mapping['native']['path'] == path and mapping['source'].startswith('https://github.com/OpenAgriNet/')
                        else:
                            # Promoted: the deployed mapping carries no trace metadata.
                            assert mapping_file.resolve() in {(external/m['path']).resolve() for m in deployed}, mapping_file
                        linked.add(mapping_file.resolve())
                    assert operation['responses'] and operation['operationId']
            # Every trace must be linked; a deployed mapping need not be documented here.
            assert {(external/m['path']).resolve() for m in traced} <= linked, version
            assert linked <= {(external/m['path']).resolve() for m in traced + deployed}, version
            if traced or deployed:
                candidate = doc['x-draft']['catalogCandidate']
                assert candidate['informationMode'] == 'OnDemand' and candidate['publicationStatus'] == 'inactive-proposal'
                public = {(version/b['mapping']).resolve() for b in candidate['actions']}
                assert {(external/m['path']).resolve() for m in traced if m['action'] != 'internal'} <= public, version
                assert public <= {(external/m['path']).resolve() for m in traced + deployed if m['action'] != 'internal'}, version
                for binding in candidate['actions']:
                    mapping = yaml.safe_load((version/binding['mapping']).read_text())
                    if 'native' in mapping:
                        native = mapping['native']
                        pointer = native['path'].replace('~', '~0').replace('/', '~1')
                        assert binding['operationRef'] == '#/paths/'+pointer+'/'+native['method'].lower()
                    else:
                        # A promoted mapping carries no native block, so the pointer is
                        # checked against the draft's own paths rather than skipped.
                        document, _, rest = binding['operationRef'].partition('#/paths/')
                        assert document == '' and rest, binding['operationRef']
                        pointer, _, verb = rest.rpartition('/')
                        path = pointer.replace('~1', '/').replace('~0', '~')
                        assert verb in doc['paths'].get(path, {}), (version, binding['operationRef'])
                        checks += 1
                    assert binding['action'] == mapping['action']
            assert set(doc['x-draft']['proposedActions']) == {
                m['action'] for m in inventory['mappings'] if (external/m['path']).is_relative_to(version) and m['action'] != 'internal'}, version
        if (version/'openapi.yaml').is_file():
            continue
        drafts = [m for m in inventory['mappings'] if (external/m['path']).is_relative_to(version)]
        assert drafts and all(m['status'] in ('draft-handler', 'source-traced', 'existing') for m in drafts), version
assert not list((ROOT/'schema').glob('*/v0.2/examples/network'))
assert not list(external.rglob('catalog-schema.yaml'))
for mapping in inventory['mappings']:
    if 'fixture' in mapping:
        assert ROOT/mapping['fixture'] in catalog_files, mapping['path']
    if mapping.get('status') == 'draft-native' and 'operationRef' in mapping:
        draft_file = external/mapping['path']
        draft = yaml.safe_load(draft_file.read_text())
        assert draft['deployable'] is False and draft['operationRef'] == mapping['operationRef']
        assert draft['action'] == mapping['action'] and draft['request']['jsonata'] and draft['response']['jsonata']
        resources = [r for c in json.loads((ROOT/mapping['fixture']).read_text())['message']['catalogs']
                     for r in c['resources'] if r['descriptor']['code'] in mapping['descriptor_codes']]
        assert resources and all(any(a['action'] == draft['action'] and a['operationRef'] == draft['operationRef']
                                     for a in r['resourceAttributes']['actions']) for r in resources)
        api_url, fragment = draft['operationRef'].split('#')
        spec = ROOT/local_path(api_url)
        operation = yaml.safe_load(spec.read_text())
        for token in unquote(fragment)[1:].split('/'):
            operation = operation[token.replace('~1', '/').replace('~0', '~')]
        assert (spec.parent/operation['x-oan-mapping']['href']).resolve() == draft_file.resolve()
    if mapping.get('advertised') is False:
        draft = yaml.safe_load((external/mapping['path']).read_text())
        assert draft['deployable'] is False and draft['missing'] and 'operationRef' not in draft
        provider = json.loads((external/mapping['provider']/'catalog.json').read_text())
        assert not any(a['action'] == mapping['action'] for c in provider['message']['catalogs']
                       for r in c['resources'] if r['descriptor']['code'] in mapping['descriptor_codes']
                       for a in r['resourceAttributes'].get('actions', []))
nearby = yaml.safe_load((external/'agmarknet/nearby-prices/v0.2/mappings/select.yaml').read_text())
assert nearby['status'] == 'incomplete' and nearby['deployable'] is False and nearby['missing']
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
operation_ids = set()

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
    # The named schema must constrain the payload's own type. Probing every JSON type
    # keeps that honest for a provider whose native result is a bare scalar, which a
    # string probe alone would reject.
    assert any(not validator.is_valid(probe) for probe in (None, True, 1, 'not an envelope', [], {})), (uri, direction)
    return len(examples)+2


for file in sorted(external.glob('*/*/v0.2/openapi.yaml')):
    doc = yaml.safe_load(file.read_text())
    assert doc['info']['x-contract-role'] == 'provider-native', file
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
    catalog_file = external/publisher/'catalog.json'
    catalog = json.loads(catalog_file.read_text())
    descriptor, = [r['descriptor'] for c in catalog['message']['catalogs'] for r in c['resources']
                   if r['descriptor']['code'] == code]
    assert any(d['url'] == published(file.relative_to(ROOT).as_posix())
               for d in descriptor['docs']), code
    doc = yaml.safe_load(file.read_text())
    actual = {}
    for item in doc['paths'].values():
        if 'get' not in item:  # This check covers linked reads, not OTP POSTs.
            continue
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

def local_document(url):
    path, _, fragment = local_path(url).partition('#')
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

search_examples = external/'knowledge/search/v0.2/examples'
search_request, exchange, callback = [json.loads((search_examples/f'{name}.json').read_text())
                                       for name in ('discover', 'search-exchange', 'on_discover')]
assert exchange['nativeRequest'] == {'query': search_request['message']['intent']['textSearch']}
assert callback['context']['action'] == 'on_discover'
for key in ('transactionId', 'messageId'):
    assert callback['context'][key] == search_request['context'][key]
rows = callback['message']['catalogs'][0]['resources']
assert len(rows) == len(exchange['nativeResponse']['hits']) > 0
for row, hit in zip(rows, exchange['nativeResponse']['hits']):
    attrs = row['resourceAttributes']
    validate_uri(origin+'schema/KnowledgeResource/v0.2/attributes.yaml#/components/schemas/KnowledgeResource', attrs)
    assert attrs['informationMode'] == 'Direct' and 'actions' not in attrs
    assert attrs['content'][0]['inlineContent'] == hit['text']

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
for file in catalog_files:
    publish = json.loads(file.read_text())
    assert publish['context']['action'] == 'catalog/publish'
    catalogs = publish['message']['catalogs']
    ids = [c['id'] for c in catalogs]
    directives = [d['catalogId'] for d in publish['message']['publishDirectives']]
    assert ids and len(set(ids)) == len(ids) and sorted(ids) == sorted(directives), file
    for catalog in catalogs:
        resource_ids = [r['id'] for r in catalog['resources']]
        assert len(resource_ids) == len(set(resource_ids)), catalog['id']
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
            overview = (ROOT/'api/providers/index.html').read_text()
            section = overview.split(f'id="cap-{code}"', 1)[1].split('</article>', 1)[0]
            block = section.split('<summary>Structured discovery request</summary><pre><code>', 1)[1]
            query = requests[code] = json.loads(html.unescape(block.split('</code></pre>', 1)[0]))
            assert query['context']['action'] == 'discover'
            expr = query['message']['intent']['filters']['expression']
            assert query['context']['schemaContext'] == [attrs['@context']+'#'+attrs['@type']]
            assert '@.resourceAttributes."@type" == '+json.dumps(attrs['@type']) in expr
            if code == 'knowledge-search':
                assert query['message']['intent']['textSearch'].strip()
            else:
                assert 'textSearch' not in query['message']['intent']
            assert 'descriptor.code' not in expr
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
template = ROOT/'api/external/pmfby/grievance/v0.2/examples/discover-request.json'
assert requests['pmfby-grievances'] == json.loads(template.read_text())
generated = json.loads((ROOT/'_data/schema_packs.json').read_text())
for pack in ('Grievance', 'SchemeApplication'):
    directory = ROOT/'schema'/pack/'v0.2'
    document = yaml.safe_load((directory/'attributes.yaml').read_text())
    root = document['components']['schemas'][pack]
    variants = []
    resources = [( (directory/'attributes.yaml').as_uri(), Resource.from_contents(document, default_specification=DRAFT202012))]
    assert root['allOf'][0]['$ref'] == f'#/components/schemas/{pack}Fields'
    assert len(root['allOf']) == 1 and root['unevaluatedProperties'] is False
    for name, member in document['components']['schemas'].items():
        if not name.endswith('Catalog'):
            continue
        variants.append(member)
    registry = Registry().with_resources(resources)
    validator = Draft202012Validator({'$ref': (directory/'attributes.yaml').as_uri()+f'#/components/schemas/{pack}'}, registry=registry, format_checker=FormatChecker())
    api_by_scheme = {}
    for variant in variants:
        code = variant['properties']['scheme']['properties']['code']['const']
        api_by_scheme[code] = variant['externalDocs']['url']
        local_document(api_by_scheme[code])
        checks += 1
    examples = [json.loads(path.read_text()) for path in (directory/'examples').glob('*.json')]
    for _, resource in published_examples.values():
        attrs = resource['resourceAttributes']
        if attrs['@type'] == 'openagrinet:'+pack and attrs['scheme']['code'] in api_by_scheme:
            examples.append(attrs)
            assert any(d['url'] == api_by_scheme[attrs['scheme']['code']] for d in resource['descriptor']['docs'])
    for example in examples:
        errors = list(validator.iter_errors(example))
        assert not errors, f'{pack}: catalog example does not validate'
        checks += 1
        for action in example['actions']:
            url = action['operationRef']
            assert url.startswith(api_by_scheme[example['scheme']['code']]+'#/paths/')
            assert local_document(url)[2]['operationId']
            checks += 1
    # Provider fixtures remain constrained by their own API catalogs, not the generic root.
    provider_only = Draft202012Validator({'oneOf': variants}, format_checker=FormatChecker())
    for example in examples:
        assert provider_only.is_valid(example)
        wrong_response = copy.deepcopy(example)
        wrong_response['actions'][0]['operationRef'] += 'Invalid'
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
    assert set(api_by_scheme.values()) <= {doc['url'] for doc in page['api_docs']}
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
