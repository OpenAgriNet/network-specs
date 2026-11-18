#!/usr/bin/env python3
"""Plan immutable builds and assemble static outputs without running branch code."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import quote

BASE = '/network-specs'
ORIGIN = 'https://openagrinet.github.io'
TEXT = {'.html', '.json', '.jsonld', '.yaml', '.yml', '.md', '.txt'}


def branch_path(branch):
    parts = branch.split('/')
    if any(part in ('', '.', '..') for part in parts) or '\\' in branch:
        raise ValueError('Unsafe branch path')
    if parts[0] in ('index.html', 'manifest.json'):
        raise ValueError('Reserved preview path')
    return branch


def plan():
    refs = subprocess.check_output(['git', 'for-each-ref',
        '--format=%(refname:strip=3) %(objectname)', 'refs/remotes/origin'], text=True)
    entries = []
    for line in refs.splitlines():
        branch, sha = line.split(' ', 1)
        if branch in ('HEAD', 'gh-pages'):
            continue
        files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', sha, '--', 'schema'], text=True)
        if not any(name.endswith('/profile.json') for name in files.splitlines()):
            continue
        path = '' if branch == 'main' else 'previews/' + branch_path(branch)
        entries.append({'branch': branch, 'sha': sha, 'path': path,
            'base': BASE + ('/' + quote(path, safe='/-._') if path else ''),
            'artifact': 'site-' + hashlib.sha256(branch.encode()).hexdigest()})
    if not any(entry['branch'] == 'main' for entry in entries):
        raise ValueError('Missing production build')
    return {'include': entries}


def copy_static(source, destination):
    if not (source / 'schema/index.html').is_file():
        raise ValueError('Missing schema index')
    for path in source.rglob('*'):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ValueError('Only regular files and directories may be published')
        relative = path.relative_to(source)
        if relative.parts[0] == 'previews' or any(part.startswith('.') for part in relative.parts):
            raise ValueError('Nested previews and hidden files may not be published')
        if path.is_file():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)


def assemble(matrix, artifacts, output):
    if output.exists():
        raise ValueError('Output must be a fresh directory')
    entries = matrix['include']
    manifest = {'production': next(e['sha'] for e in entries if e['branch'] == 'main'), 'previews': []}
    for entry in sorted(entries, key=lambda e: e['branch'] != 'main'):
        destination = output / entry['path']
        copy_static(artifacts / entry['artifact'], destination)
        if entry['branch'] == 'main':
            continue
        base = entry['base']
        banner = (f'<aside class="preview-banner" style="padding:12px;background:#fff3cd;color:#222">'
            f'Preview: {html.escape(entry["branch"])} · {entry["sha"][:12]} · '
            f'<a href="{BASE}/">Production</a> · <a href="{BASE}/previews/">All previews</a></aside>')
        for path in destination.rglob('*'):
            if path.is_file() and path.suffix.lower() in TEXT:
                text = path.read_text()
                for directory in ('schema', 'api', 'api-schemas', 'api-specs'):
                    text = text.replace(f'{ORIGIN}{BASE}/{directory}/', f'{ORIGIN}{base}/{directory}/')
                if path.suffix == '.html':
                    text = re.sub(r'(<body\b[^>]*>)', lambda m: m[0] + banner, text, count=1)
                    text = text.replace('</head>', '<meta name="robots" content="noindex,nofollow"></head>', 1)
                path.write_text(text)
        manifest['previews'].append({'branch': entry['branch'], 'commit': entry['sha'], 'url': base + '/'})
    previews = output / 'previews'
    previews.mkdir(exist_ok=True)
    for entry in manifest['previews']:
        old = re.sub(r'[^a-zA-Z0-9_-]+', '-', entry['branch']).strip('-')[:60] or 'branch'
        old += '-' + hashlib.sha256(entry['branch'].encode()).hexdigest()[:8]
        if any(e['branch'].split('/')[0] == old for e in entries):
            continue
        target = html.escape(entry['url'], quote=True)
        (previews / old).mkdir(exist_ok=True)
        (previews / old / 'index.html').write_text(f'<!doctype html><meta http-equiv="refresh" content="0;url={target}"><a href="{target}">Open preview</a>')
    links = ''.join(f'<li><a href="{html.escape(e["url"], quote=True)}">{html.escape(e["branch"])}</a> <code>{e["commit"][:12]}</code></li>' for e in manifest['previews'])
    (previews / 'index.html').write_text('<!doctype html><title>Branch previews</title><meta name="robots" content="noindex,nofollow"><h1>Branch previews</h1><p>Each preview uses its branch’s layouts and contracts.</p><ul>' + links + '</ul>')
    (previews / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['plan', 'assemble'])
    parser.add_argument('--matrix')
    parser.add_argument('--artifacts', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.command == 'plan':
        print(json.dumps(plan(), separators=(',', ':')))
    else:
        assemble(json.loads(args.matrix), args.artifacts, args.output)
