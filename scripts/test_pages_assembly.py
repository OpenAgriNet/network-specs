import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('assembly', Path(__file__).with_name('assemble-pages.py'))
assembly = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assembly)


class AssemblyTests(unittest.TestCase):
    def test_branch_paths(self):
        self.assertEqual(assembly.branch_path('fix/a'), 'fix/a')
        for branch in ('../a', '/a', 'a//b', 'a\\b', 'index.html', 'manifest.json/a'):
            with self.assertRaises(ValueError):
                assembly.branch_path(branch)

    def test_branch_layout_preserved_and_root_isolated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entries = []
            for branch, artifact, path in [('main', 'main-site', ''), ('feature', 'branch-site', 'previews/feature')]:
                source = root / artifact / 'schema'
                source.mkdir(parents=True)
                (source / 'index.html').write_text('<html><head></head><body class="site">' + branch + '</body></html>')
                entries.append(dict(branch=branch, artifact=artifact, path=path, sha='a'*40, base='/network-specs/' + path))
            assembly.assemble({'include': entries}, root, root/'output')
            self.assertNotIn('Preview:', (root/'output/schema/index.html').read_text())
            preview = (root/'output/previews/feature/schema/index.html').read_text()
            self.assertIn('Preview: feature', preview)
            self.assertIn('class="site"', preview)
            self.assertIn('feature</body>', preview)
            self.assertEqual(json.loads((root/'output/previews/manifest.json').read_text())['previews'][0]['branch'], 'feature')

    def test_links_and_nested_previews_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root/'source'
            (source/'schema').mkdir(parents=True)
            (source/'schema/index.html').write_text('test')
            (source/'bad').symlink_to('/etc/passwd')
            with self.assertRaises(ValueError):
                assembly.copy_static(source, root/'output')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'source/schema').mkdir(parents=True)
            (root/'source/schema/index.html').write_text('test')
            (root/'source/previews').mkdir()
            with self.assertRaises(ValueError):
                assembly.copy_static(root/'source', root/'output')
