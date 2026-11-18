#!/usr/bin/env python3
"""One-time, reproducible migration of the reviewed mixed contracts.

Uses the frozen source revision, never live provider responses. Rerunning refuses
to overwrite edited API contracts. Future contract changes belong in the outputs.
"""
import copy
import json
from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE_REVISION = '2b5803476bda6a82b405e15099c7028208641b37'
URL = 'https://openagrinet.github.io/network-specs'


def merge(a, b):
    result = copy.deepcopy(a)
    for key, value in b.items():
        if key == 'required':
            result[key] = list(dict.fromkeys(result.get(key, []) + value))
        elif isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def expand(node, components):
    if isinstance(node, list):
        return [expand(value, components) for value in node]
    if not isinstance(node, dict):
        return node
    result = {}
    if '$ref' in node:
        ref = node['$ref']
        if not ref.startswith('#/components/schemas/'):
            return copy.deepcopy(node)
        result = expand(components[ref.rsplit('/', 1)[-1]], components)
    for member in node.get('allOf', []):
        result = merge(result, expand(member, components))
    return merge(result, {key: expand(value, components) for key, value in node.items()
                          if key not in ('$ref', 'allOf', 'x-oan-fields')})


def project(node, paths, required):
    """Project explicit field paths. Preserve constraints within selected values."""
    result = {key: copy.deepcopy(value) for key, value in node.items()
              if key not in ('properties', 'required', 'oneOf', 'anyOf', 'not')}
    result.update(type='object', additionalProperties=False, properties={})
    heads = sorted({path.split('.')[0] for path in paths})
    for head in heads:
        child = node['properties'][head]
        tails = [path[len(head)+1:] for path in paths if path.startswith(head+'.')]
        child_required = [path[len(head)+1:] for path in required if path.startswith(head+'.')]
        result['properties'][head] = copy.deepcopy(child) if head in paths else project(child, tails, child_required)
    mandatory = [head for head in heads if any(p == head or p.startswith(head+'.') for p in required)]
    if mandatory:
        result['required'] = mandatory
    return result


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=True))


def migrate(pack):
    public = ROOT / 'schema' / pack / 'v0.1'
    api = ROOT / 'api-specs' / pack / 'v0.1'
    if (api / 'openapi.yaml').exists():
        raise SystemExit(f'{pack}: already migrated; edit canonical API files directly')
    original = yaml.safe_load(subprocess.check_output(
        ['git', 'show', f'{BASE_REVISION}:schema/{pack}/v0.1/attributes.yaml'], cwd=ROOT))
    components = original['components']['schemas']
    catalogs = [name for name, value in components.items()
                if name.endswith('Catalog') and 'x-oan-fields' in value]
    leaves = {name: value for name, value in components.items()
              if 'x-oan-fields' in value and name not in catalogs}
    api_schemas = {}
    paths = {}
    identity = ['@context', '@type', 'informationMode', 'scheme.code']
    for name, leaf in leaves.items():
        fields = leaf['x-oan-fields']
        flat = expand(leaf, components)
        request_paths = list(dict.fromkeys(identity + fields.get('mustSend', []) + fields.get('maySend', []) + fields.get('oneOf', [])))
        request = project(flat, request_paths, identity + fields.get('mustSend', []))
        if fields.get('oneOf'):
            request['oneOf'] = [{'required': [path.split('.')[0]]} for path in fields['oneOf']]
        response_paths = list(dict.fromkeys(identity + fields['comesBack']))
        # Presence of a documented output does not establish universal requiredness.
        # Require only identity and an explicit operation outcome below.
        response_required = identity.copy()
        if name.endswith('Init'):
            response_required += ['challenge.issued.method', 'challenge.issued.channel',
                                  'challenge.issued.length', 'challenge.issued.valueType',
                                  'challenge.issued.expiresAt']
        elif name.endswith('Support'):
            response_required += ['case.ticketNo']
        elif 'Application' not in name:
            response_required += ['case.status.code']
        else:
            response_required += ['application']
        response = project(flat, response_paths, response_required)
        api_schemas[name+'Request'] = request
        api_schemas[name+'Response'] = response
        action = next(action for action in ('Init', 'Status', 'Support') if name.endswith(action))
        path = '/'+name.removesuffix(action).lower()+'/'+action.lower()
        paths[path] = {'post': {
            'operationId': name,
            'summary': name+' attributes exchange',
            'description': 'Proposed adapter-facing synchronous operation for consumer review. '
                           'Not a deployed provider URL or a complete Beckn wire envelope. '
                           'Authentication and the final Beckn binding require consumer agreement.',
            'requestBody': {'required': True, 'content': {'application/json': {'schema': {'$ref': '#/components/schemas/'+name+'Request'}}}},
            'responses': {'200': {'description': 'Successful operation outcome, not a transport ACK.',
                                  'content': {'application/json': {'schema': {'$ref': '#/components/schemas/'+name+'Response'}}}},
                          'default': {'description': 'Error contract is not yet agreed. Do not return raw upstream errors or personal data.'}}
        }}
    # Retain old payload definitions at explicit legacy names for compatibility.
    for name, value in components.items():
        copied = copy.deepcopy(value)
        copied.pop('x-oan-fields', None)
        api_schemas[name] = copied
    specification = {'openapi': '3.1.1', 'info': {'title': pack+' operation contracts', 'version': '0.1.0',
        'description': 'Consumer-review proposal. Separate directional attributes contracts. Legacy components are compatibility-only. '
                       'No live server is advertised. Authentication, errors and Beckn wire bindings are pending.'},
        'servers': [{'url': 'https://adapter.example.invalid', 'description': 'Non-operational review placeholder'}],
        'paths': paths, 'components': {'schemas': api_schemas}}
    write(api/'openapi.yaml', specification)
    # Public root validates catalog resources only. Historical names remain aliases.
    public_components = {pack: {'description': 'Public discovery metadata only. Private operations are defined in api-specs.',
        'x-beckn-container': 'resourceAttributes', 'x-jsonld': components[pack]['x-jsonld'],
        'oneOf': [{'$ref': '#/components/schemas/'+name} for name in catalogs]}}
    for name in catalogs:
        public_components[name] = expand(components[name], components)
    for name in components:
        if name not in public_components:
            public_components[name] = {'$ref': f'../../../api-specs/{pack}/v0.1/openapi.yaml#/components/schemas/{name}',
                                       'deprecated': True, 'description': 'Compatibility alias. Use directional operation schemas in api-specs.'}
    public_components[pack]['description'] += f' See {URL}/api-specs/{pack}/v0.1/.'
    write(public/'attributes.yaml', {'openapi': '3.1.1', 'info': {'title': pack+' catalog attributes',
        'version': '0.1.0', 'description': public_components[pack]['description']}, 'components': {'schemas': public_components}})
    profile = json.loads((public/'profile.json').read_text())
    profile['name'] = pack+' catalog attributes'
    profile['semantic_model'] = 'resource'
    for key in ('indexable_paths', 'filterable_paths', 'sortable_paths'):
        profile[key] = [p for p in profile.get(key, []) if p.startswith('beckn:resourceAttributes.')]
    profile['result_fields'] = profile['discovery_fields']
    (public/'profile.json').write_text(json.dumps(profile, indent=2)+'\n')
    # Preserve every original example, now collocated with operation contracts.
    for example in (public/'examples').glob('*.json'):
        value = json.loads(example.read_text())
        if 'actions' not in value:
            target = api/'examples'/example.name
            target.parent.mkdir(parents=True, exist_ok=True)
            example.rename(target)
    print(f'{pack}: {len(catalogs)} public catalog variants, {len(paths)} operations')


if __name__ == '__main__':
    for name in ('Grievance', 'SchemeApplication'):
        migrate(name)
