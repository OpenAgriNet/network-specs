#!/usr/bin/env python3
"""Validate directional contracts and supplied fixtures; never call providers."""
import copy
import json
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
checks = 0
directories = sorted((ROOT/'api/external').glob('*/*/v0.1'))
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
    old = yaml.safe_load((ROOT/'api-specs'/pack/'v0.1/openapi.yaml').read_text())
    assert not old['paths'], 'Compatibility file must not advertise duplicate operations'
    for name, schema in old['components']['schemas'].items():
        if name in {operation + direction for operation in operation_ids for direction in ('Request', 'Response')}:
            assert '/api/external/' in schema['$ref'], name
            checks += 1
print(f'{checks} API separation checks passed. No provider integration was tested.')
