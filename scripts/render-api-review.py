#!/usr/bin/env python3
"""Render operation contracts and synthetic minimum outcomes for branch review."""
import json
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def sample(schema):
    if 'oneOf' in schema:
        return sample(schema['oneOf'][0])
    if 'const' in schema:
        return schema['const']
    if 'enum' in schema:
        return schema['enum'][0]
    if schema.get('type') == 'object':
        names = list(schema.get('required', []))
        if not names and schema.get('minProperties', 0):
            names = ['registeredOn'] if 'registeredOn' in schema['properties'] else list(schema['properties'])[:schema['minProperties']]
        return {name: sample(schema['properties'][name]) for name in names}
    if schema.get('type') == 'array':
        return [sample(schema['items']) for _ in range(schema.get('minItems', 0))]
    if schema.get('type') in ('integer', 'number'):
        return schema.get('minimum', 1)
    if schema.get('type') == 'boolean':
        return False
    if schema.get('format') == 'date-time':
        return '2026-11-18T06:05:00Z'
    if schema.get('format') == 'date':
        return '2026-11-18'
    if schema.get('pattern') == '^[0-9]+$':
        return '123456789'
    return 'EXAMPLE'


for directory in sorted((ROOT/'api/external').glob('*/*/v0.1')):
    spec = yaml.safe_load((directory/'openapi.yaml').read_text())
    schemas = spec['components']['schemas']
    title = spec['info']['title']
    lines = ['---', 'layout: default', f'title: {title}', '---',
             f'# {title}', '',
             '[All external APIs](../../../) · [OpenAPI document](openapi.yaml)', '',
             spec['info']['description'], '']
    for path, value in spec['paths'].items():
        operation = value['post']
        name = operation['operationId']
        lines += [f'## {name}', '', f'`POST {path}`', '']
        for direction in ('Request', 'Response'):
            schema = schemas[name+direction]
            validator = Draft202012Validator(schema, format_checker=FormatChecker())
            if direction == 'Response':
                data = sample(schema)
                validator.validate(data)
                (directory/'examples'/f'{name}-response.json').write_text(json.dumps(data, indent=2)+'\n')
            examples = []
            for example in sorted((directory/'examples').glob('*.json')):
                data = json.loads(example.read_text())
                if validator.is_valid(data):
                    examples.append((example.name, data))
            assert examples, (name, direction)
            lines += [f'### {direction}', '',
                      f'[Schema component](openapi.yaml#/components/schemas/{name}{direction})', '',
                      '| Field | Required | Meaning |', '|---|---|---|']
            for field, definition in schema['properties'].items():
                description = definition.get('description', '').replace('\n', ' ').replace('|', '\\|')
                lines.append(f'| `{field}` | {"Yes" if field in schema.get("required", []) else "Optional"} | {description} |')
            lines += ['', 'Nested requirements and conditional identifier choices are defined in the linked schema.', '']
            for filename, data in examples:
                lines += [f'Example: [{filename}](examples/{filename})', '', '```json', json.dumps(data, indent=2), '```', '']
    (directory/'index.md').write_text('\n'.join(lines))
print('Rendered provider API pages with validated synthetic outcomes.')

# Earlier URLs remain useful entry points, but no longer duplicate the full pages.
for pack, links in {
    'Grievance': [('PMFBY grievance', 'pmfby/grievance'), ('PM-KISAN grievance', 'pm-kisan/grievance')],
    'SchemeApplication': [('PM-KISAN application status', 'pm-kisan/application')],
}.items():
    lines = ['---', 'layout: default', f'title: {pack} API specifications', '---',
             f'# {pack} API specifications', '', 'Contracts are grouped by provider.', '']
    lines += [f'- [{label}](../../../api/external/{path}/v0.1/)' for label, path in links]
    lines += ['', '[Earlier schema component references](openapi.yaml) remain available for compatibility.', '']
    (ROOT/'api-specs'/pack/'v0.1/index.md').write_text('\n'.join(lines))
