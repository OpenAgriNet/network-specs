#!/usr/bin/env python3
"""Validate directional contracts and supplied fixtures; never call providers."""
import copy
import json
import subprocess
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
checks = 0
directories = sorted((ROOT/'api/external').glob('*/*/v0.2'))
assert len(directories) == 3, 'Expected three provider/service contracts'
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

for path in list((ROOT/'api').rglob('*.yaml')) + list((ROOT/'api-specs').rglob('*.yaml')):
    document = yaml.safe_load(path.read_text())
    for ref in refs(document):
        if ref.startswith(('http:', 'https:')):
            continue
        file, _, fragment = ref.partition('#')
        target = yaml.safe_load((path.parent/file).read_text()) if file else document
        for part in fragment.lstrip('/').split('/') if fragment else []:
            target = target[part.replace('~1', '/').replace('~0', '~')]
        checks += 1

for pack in ('Grievance', 'SchemeApplication'):
    old = yaml.safe_load((ROOT/'api-specs'/pack/'v0.2/openapi.yaml').read_text())
    assert not old['paths'], 'Compatibility file must not advertise duplicate operations'
    for name, schema in old['components']['schemas'].items():
        if name in {operation + direction for operation in operation_ids for direction in ('Request', 'Response')}:
            assert '/api/external/' in schema['$ref'], name
            checks += 1
origin = 'https://openagrinet.github.io/network-specs/'

def local_document(url):
    assert url.startswith(origin), url
    path, _, fragment = url[len(origin):].partition('#')
    file = ROOT/path
    document = yaml.safe_load(file.read_text())
    target = document
    for part in fragment.lstrip('/').split('/') if fragment else []:
        target = target[part.replace('~1', '/').replace('~0', '~')]
    return file, document, target

generated = json.loads((ROOT/'_data/schema_packs.json').read_text())
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
        legacy = copy.deepcopy(example)
        for action in legacy['actions']:
            name = action['schema'].rsplit('/', 1)[-1].removesuffix('Request')
            action['schema'] = f'{origin}schema/{pack}/v0.2/attributes.yaml#/components/schemas/{name}'
        assert validator.is_valid(legacy), 'Earlier catalog references must remain valid'
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
