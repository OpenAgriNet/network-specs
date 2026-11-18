#!/usr/bin/env python3
"""One-time provider grouping of the existing adapter contracts, without changing payloads."""
import copy
import json
import os
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
GROUPS = (
    ('Grievance', 'pmfby', 'grievance', 'PMFBY'),
    ('Grievance', 'pm-kisan', 'grievance', 'PMKISAN'),
    ('SchemeApplication', 'pm-kisan', 'application', 'PMKISANApplication'),
)


def main():
    documents = {}
    for pack, provider, service, prefix in GROUPS:
        source = ROOT / 'api-specs' / pack / 'v0.1'
        document = documents.setdefault(pack, yaml.safe_load((source / 'openapi.yaml').read_text()))
        target = ROOT / 'api/external' / provider / service / 'v0.1'
        if target.exists():
            raise SystemExit(f'Refusing to overwrite {target}')
    for pack, provider, service, prefix in GROUPS:
        source = ROOT / 'api-specs' / pack / 'v0.1'
        document = documents[pack]
        target = ROOT / 'api/external' / provider / service / 'v0.1'
        (target / 'examples').mkdir(parents=True)
        spec = copy.deepcopy(document)
        spec['info']['title'] = f'{provider.upper()} {service} integration contract'
        spec['info']['description'] = ('Proposed OAN adapter payloads for this external service. '
            'Not an official provider API specification. Paths are illustrative; authentication, '
            'errors and Beckn wire bindings are not defined. Examples are synthetic.')
        spec['paths'] = {path: operation for path, operation in spec['paths'].items()
                         if operation['post']['operationId'].startswith(prefix)}
        names = {op['post']['operationId'] + direction for op in spec['paths'].values()
                 for direction in ('Request', 'Response')}
        spec['components']['schemas'] = {name: value for name, value in document['components']['schemas'].items()
                                         if name in names}
        # Directional contracts are already expanded, so no unrelated provider definitions are copied.
        assert '$ref' not in json.dumps(spec['components']['schemas'])
        (target / 'openapi.yaml').write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True))
        validators = [Draft202012Validator(value) for value in spec['components']['schemas'].values()]
        for example in (source / 'examples').glob('*.json'):
            if any(v.is_valid(json.loads(example.read_text())) for v in validators):
                (target / 'examples' / example.name).write_text(example.read_text())
        for name in names:
            relative = os.path.relpath(target / 'openapi.yaml', source)
            document['components']['schemas'][name] = {'$ref': f'{relative}#/components/schemas/{name}'}
    # Keep old component URLs working. Legacy mixed shapes remain only for compatibility.
    for pack, document in documents.items():
        document['paths'] = {}
        document['info']['description'] = 'Compatibility components. Use the provider-grouped integration contracts under api/external/.'
        (ROOT / 'api-specs' / pack / 'v0.1/openapi.yaml').write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True))


if __name__ == '__main__':
    main()
