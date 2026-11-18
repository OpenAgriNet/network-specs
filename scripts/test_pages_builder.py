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
    def test_slug_is_stable_and_collision_resistant(self):
        self.assertEqual(pages.slug('a/b'), pages.slug('a/b'))
        self.assertNotEqual(pages.slug('a/b'), pages.slug('a-b'))
        self.assertNotIn('/', pages.slug('a/b'))

    def test_rewrite_preserves_vocabulary(self):
        prefix = pages.ORIGIN + pages.BASE
        text = prefix + '/schema/A/attributes.yaml ' + prefix + '/vocab#Thing'
        result = pages.rewrite_artifact_urls(text, '/network-specs/previews/test')
        self.assertIn('/previews/test/schema/A/attributes.yaml', result)
        self.assertIn(prefix + '/vocab#Thing', result)

    def test_only_data_is_extracted(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w') as tar:
            for name in ['schema/A/profile.json', '_plugins/evil.rb', 'scripts/evil.py']:
                info = tarfile.TarInfo(name)
                info.size = 2
                tar.addfile(info, io.BytesIO(b'{}'))
        with tempfile.TemporaryDirectory() as directory:
            pages.extract_data(buffer.getvalue(), Path(directory))
            self.assertTrue((Path(directory) / 'schema/A/profile.json').exists())
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
