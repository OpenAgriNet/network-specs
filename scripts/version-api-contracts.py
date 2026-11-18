#!/usr/bin/env python3
"""One-time migration of the API experiment to v0.2; preserve published v0.1."""
import copy
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '2b5803476bda6a82b405e15099c7028208641b37'
PACKS = ('Grievance', 'SchemeApplication')


def rewrite(text):
    for pack in PACKS:
        text = text.replace(f'schema/{pack}/v0.1', f'schema/{pack}/v0.2')
        text = text.replace(f'api-specs/{pack}/v0.1', f'api-specs/{pack}/v0.2')
    for service in ('pmfby/grievance', 'pm-kisan/grievance', 'pm-kisan/application'):
        text = text.replace(f'api/external/{service}/v0.1', f'api/external/{service}/v0.2')
    return text


def common_schema(schemas):
    result = {}
    for key in schemas[0]:
        if not all(key in schema for schema in schemas) or key in ('additionalProperties', 'externalDocs'):
            continue
        values = [schema[key] for schema in schemas]
        if key == 'properties':
            result[key] = {name: common_schema([value[name] for value in values])
                           for name in values[0] if all(name in value for value in values)}
        elif key == 'required':
            result[key] = [name for name in values[0] if all(name in value for value in values)]
        elif all(value == values[0] for value in values):
            result[key] = copy.deepcopy(values[0])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', type=Path, help='Existing backup from an interrupted migration')
    args = parser.parse_args()
    if not args.resume and any((ROOT/'schema'/pack/'v0.2').exists() for pack in PACKS):
        raise SystemExit('v0.2 already exists; refusing to overwrite review work.')
    backup = args.resume or Path(tempfile.mkdtemp(prefix='oan-v02-before-', dir='/private/tmp'))
    for directory in ('schema', 'api', 'api-specs'):
        if args.resume:
            assert (backup/directory).is_dir(), 'Missing migration backup'
        else:
            shutil.copytree(ROOT/directory, backup/directory)
    print(f'Pre-migration files retained at {backup}')
    for pack in PACKS:
        if not (ROOT/'schema'/pack/'v0.2').exists():
            shutil.copytree(ROOT/'schema'/pack/'v0.1', ROOT/'schema'/pack/'v0.2')
    for source in (ROOT/'api/external').glob('*/*/v0.1'):
        source.rename(source.with_name('v0.2'))
    for pack in PACKS:
        source = ROOT/'api-specs'/pack/'v0.1'
        if source.exists():
            source.rename(source.with_name('v0.2'))
    targets = [ROOT/'schema'/pack/'v0.2' for pack in PACKS] + [ROOT/'api', ROOT/'api-specs']
    for directory in targets:
        for file in directory.rglob('*'):
            if file.is_file():
                text = rewrite(file.read_text()).replace('0.1.0', '0.2.0')
                text = text.replace('/v0.1/', '/v0.2/') if directory in (ROOT/'api', ROOT/'api-specs') else text
                # Relative links in provider index pages.
                text = text.replace('grievance/v0.1/', 'grievance/v0.2/').replace('application/v0.1/', 'application/v0.2/')
                file.write_text(text)
    for file in [ROOT/'README.md', ROOT/'schema/index.md', *list((ROOT/'schema/examples').glob('*-api-resource.json'))]:
        file.write_text(rewrite(file.read_text()))
    for pack in PACKS:
        file = ROOT/'schema'/pack/'v0.2/attributes.yaml'
        document = yaml.safe_load(file.read_text())
        schemas = document['components']['schemas']
        root = schemas[pack]
        choices = root.pop('oneOf')
        catalogs = []
        for choice in choices:
            relative, fragment = choice['$ref'].split('#')
            external = yaml.safe_load((file.parent/relative).read_text())
            catalogs.append(external['components']['schemas'][fragment.split('/')[-1]])
        fields_name = pack+'Fields'
        fields = common_schema(catalogs)
        fields['description'] = f'Shared public {pack} catalog fields. Provider-specific restrictions are applied by the selected external catalog definition.'
        schemas[fields_name] = fields
        root['allOf'] = [{'$ref': '#/components/schemas/'+fields_name}, {'oneOf': choices}]
        file.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True))
        # Restore the exact published files only after preserving all edits in v0.2 and backup.
        prefix = f'schema/{pack}/v0.1/'
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASELINE, '--', prefix], cwd=ROOT, text=True).splitlines()
        for name in paths:
            target = ROOT/name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(subprocess.check_output(['git', 'show', f'{BASELINE}:{name}'], cwd=ROOT))
    print('Created v0.2 compositions and restored published v0.1 files.')


if __name__ == '__main__':
    main()
