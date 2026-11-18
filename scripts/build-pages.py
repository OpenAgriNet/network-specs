#!/usr/bin/env python3
"""Build main plus data-only branch previews into one Pages artifact.

Branch scripts, templates, configuration and dependencies are never executed.
"""

import argparse
import hashlib
import html
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import tempfile
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
BASE = '/network-specs'
ORIGIN = 'https://openagrinet.github.io'
DATA_ROOTS = ('schema', 'api-schemas', 'api-specs', 'api')
TEXT_SUFFIXES = {'.json', '.jsonld', '.yaml', '.yml', '.md', '.html', '.txt'}


def run(*args, cwd=ROOT, **kwargs):
    return subprocess.run(args, cwd=cwd, check=True, **kwargs)


def git(*args):
    return run('git', *args, capture_output=True, text=True).stdout.strip()


def slug(branch):
    if not branch or branch.startswith('/') or '\\' in branch or any(part in ('', '.', '..') for part in branch.split('/')):
        raise ValueError('Unsafe preview branch path')
    return branch


def legacy_slug(branch):
    readable = re.sub(r'[^a-zA-Z0-9_-]+', '-', branch).strip('-')[:60] or 'branch'
    return readable + '-' + hashlib.sha256(branch.encode()).hexdigest()[:8]


def extract_data(archive, destination):
    """Extract only ordinary domain files. No links, traversal or site code."""
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar:
            path = PurePosixPath(member.name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('Unsafe archive path')
            if not path.parts or path.parts[0] not in DATA_ROOTS:
                continue
            if not member.isfile():
                if member.isdir():
                    continue
                raise ValueError('Links are not allowed in preview data')
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            target = destination.joinpath(*path.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())


def rewrite_artifact_urls(text, base):
    # Preserve semantic vocab identifiers. Only artifact retrieval URLs change.
    for directory in DATA_ROOTS:
        text = text.replace(f'{ORIGIN}{BASE}/{directory}/',
                            f'{ORIGIN}{base}/{directory}/')
    return text


def build(branch, revision, destination, preview):
    with tempfile.TemporaryDirectory(prefix='oan-pages-') as staging:
        source = Path(staging) / 'source'
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(
            '.git', '_site', '.bundle', 'vendor', '.jekyll-cache', 'docs'))
        if preview:
            # Navigation is renderer code, not branch data. Keep it paired with
            # the trusted includes so a new branch include cannot break production.
            trusted_index = (source / 'schema/index.md').read_bytes()
            for directory in DATA_ROOTS:
                path = source / directory
                if path.exists():
                    shutil.rmtree(path)  # Only disposable generated staging.
            archive = run('git', 'archive', revision, capture_output=True).stdout
            extract_data(archive, source)
            (source / 'schema/index.md').write_bytes(trusted_index)
        base = f'{BASE}/previews/{quote(slug(branch), safe="/-._")}' if preview else BASE
        run('ruby', str(source / 'scripts/generate-schema-pages.rb'), cwd=source)
        env = dict(os.environ, BUNDLE_GEMFILE=str(ROOT / 'Gemfile'))
        run('bundle', 'exec', 'jekyll', 'build', '--safe', '--source', str(source),
            '--destination', str(destination), '--baseurl', base, cwd=source, env=env)
        if not (destination / 'schema/index.html').is_file():
            raise RuntimeError(f'Missing schema index for {branch}')
        if preview:
            api_link = (f' · <a href="{base}/api/">API specifications</a>'
                        if (destination / 'api/index.html').is_file() else '')
            banner = (f'<aside style="padding:12px;background:#fff3cd;color:#222">'
                      f'Preview: {html.escape(branch)} · {revision[:12]} · '
                      f'<a href="{BASE}/">Production</a> · '
                      f'<a href="{BASE}/previews/">All previews</a>{api_link}</aside>')
            for path in destination.rglob('*'):
                if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                    text = rewrite_artifact_urls(path.read_text(), base)
                    if path.suffix == '.html':
                        text = text.replace('<body>', '<body>' + banner, 1)
                        text = text.replace('</head>', '<meta name="robots" content="noindex,nofollow"></head>', 1)
                    path.write_text(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--test-revision', action='store_true',
                        help='Validate an unmerged renderer locally/CI; never deploy this output')
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if output.exists():
        raise SystemExit('Output must not exist; use a fresh build directory')
    current = git('rev-parse', 'HEAD')
    if not args.test_revision and current != git('rev-parse', 'refs/remotes/origin/main'):
        raise SystemExit('Build from the fetched main revision only')
    build('main', current, output, False)
    previews = output / 'previews'
    previews.mkdir(exist_ok=True)
    manifest = {'production': current, 'previews': []}
    refs = git('for-each-ref', '--format=%(refname:strip=3) %(objectname)',
               'refs/remotes/origin').splitlines()
    for ref in refs:
        branch, revision = ref.split(' ', 1)
        if branch in ('main', 'HEAD', 'gh-pages'):
            continue
        files = git('ls-tree', '-r', '--name-only', revision, '--', 'schema')
        if not any(name.endswith('/profile.json') for name in files.splitlines()):
            continue
        print(f'Building preview {branch} at {revision}', flush=True)
        build(branch, revision, previews / slug(branch), True)
        manifest['previews'].append({'branch': branch, 'commit': revision,
                                     'url': f'{BASE}/previews/{quote(slug(branch), safe="/-._")}/'})
        # Preserve old bookmarked preview entry points without duplicating artifacts.
        old_path = previews / legacy_slug(branch)
        if any(other.split(' ', 1)[0].split('/')[0] == old_path.name for other in refs):
            continue  # A real branch owns this URL; never overwrite it with a redirect.
        old_path.mkdir(parents=True, exist_ok=True)
        target = html.escape(manifest['previews'][-1]['url'], quote=True)
        (old_path / 'index.html').write_text(
            '<!doctype html><html><head><meta charset="utf-8">'
            f'<meta http-equiv="refresh" content="0;url={target}">'
            '<meta name="robots" content="noindex,nofollow"><title>Preview moved</title>'
            f'</head><body><a href="{target}">Open branch preview</a></body></html>')
    items = ''.join(f'<li><a href="{entry["url"]}">{html.escape(entry["branch"])}</a> '
                    f'<code>{entry["commit"][:12]}</code></li>' for entry in manifest['previews'])
    (previews / 'index.html').write_text(
        '<!doctype html><html><head><meta charset="utf-8"><title>Schema previews</title>'
        '<meta name="robots" content="noindex,nofollow"></head><body>'
        f'<h1>Schema branch previews</h1><p><a href="{BASE}/">Production</a></p>'
        '<p>Experimental contracts. Rendered using main’s site templates.</p>'
        f'<ul>{items}</ul></body></html>')
    (previews / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
