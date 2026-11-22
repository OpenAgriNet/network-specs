import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('pages', Path(__file__).with_name('build-pages.py'))
pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pages)


class PreviewTests(unittest.TestCase):
    def test_branch_paths_are_stable_and_distinct(self):
        self.assertEqual(pages.slug('a/b'), pages.slug('a/b'))
        self.assertNotEqual(pages.slug('a/b'), pages.slug('a-b'))
        self.assertEqual(pages.slug('a/b'), 'a/b')
        self.assertEqual(pages.slug('schema-packs-api-driven'), 'schema-packs-api-driven')
        self.assertEqual(pages.legacy_slug('schema-packs-api-driven'), 'schema-packs-api-driven-dd73de2c')
        for name in ('../escape', '/absolute', 'a/../b', 'a//b', 'a\\b'):
            with self.assertRaises(ValueError):
                pages.slug(name)

    def test_rewrite_preserves_vocabulary(self):
        prefix = pages.ORIGIN + pages.BASE
        text = prefix + '/schema/A/attributes.yaml ' + prefix + '/vocab#Thing ' + prefix + '/api/external/pmfby/openapi.yaml'
        result = pages.rewrite_artifact_urls(text, '/network-specs/previews/test')
        self.assertIn('/previews/test/schema/A/attributes.yaml', result)
        self.assertIn(prefix + '/vocab#Thing', result)
        self.assertIn('/previews/test/api/external/pmfby/openapi.yaml', result)

    def test_only_data_is_extracted(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w') as tar:
            for name in ['schema/A/profile.json', 'api/external/pmfby/openapi.yaml', 'mappings/sample/select.yaml', 'mappings/ignored.rb', '_plugins/evil.rb', 'scripts/evil.py']:
                info = tarfile.TarInfo(name)
                info.size = 2
                tar.addfile(info, io.BytesIO(b'{}'))
        with tempfile.TemporaryDirectory() as directory:
            pages.extract_data(buffer.getvalue(), Path(directory))
            self.assertTrue((Path(directory) / 'schema/A/profile.json').exists())
            self.assertTrue((Path(directory) / 'api/external/pmfby/openapi.yaml').exists())
            self.assertTrue((Path(directory) / 'mappings/sample/select.yaml').is_file())
            self.assertFalse((Path(directory) / 'mappings/ignored.rb').exists())
            self.assertFalse((Path(directory) / '_plugins').exists())
            self.assertFalse((Path(directory) / 'scripts').exists())

    def test_traversal_rejected(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w') as tar:
            info = tarfile.TarInfo('schema/../../escape.json')
            tar.addfile(info, io.BytesIO())
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                pages.extract_data(buffer.getvalue(), Path(directory))


if __name__ == '__main__':
    unittest.main()
