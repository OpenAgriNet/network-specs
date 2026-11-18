#!/usr/bin/env python3
"""Validate directional contracts and supplied fixtures; never call providers."""
import copy
import json
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
checks = 0
for pack in ('Grievance', 'SchemeApplication'):
    api = ROOT/'api-specs'/pack/'v0.1'
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
    for operation in document['paths'].values():
        operation = operation['post']
        for schema in [operation['requestBody']['content']['application/json']['schema'],
                       operation['responses']['200']['content']['application/json']['schema']]:
            assert schema['$ref'].rsplit('/', 1)[-1] in schemas
            checks += 1
print(f'{checks} API separation checks passed. No provider integration was tested.')
