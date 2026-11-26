import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from scripts.import_archives import stage

class ImportTests(unittest.TestCase):
    def test_exact_bytes_and_idempotence(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); source=root/'source';source.mkdir()
            z=source/'round.zip'
            with ZipFile(z,'w') as f:f.writestr('a.py','print(42)\n')
            m=root/'manifest';m.write_text(hashlib.sha256(z.read_bytes()).hexdigest()+'  round.zip\n')
            dst=root/'out'
            rows=stage(source,m,dst)
            self.assertEqual(len(rows),1)
            self.assertEqual(z.read_bytes(),(dst/'round.zip').read_bytes())
            self.assertEqual(rows,stage(source,m,dst))
            (dst/'round.zip').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'overwrite'):stage(source,m,dst)
    def test_unsafe_member(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);z=root/'round.zip'
            with ZipFile(z,'w') as f:f.writestr('../a.py','bad')
            m=root/'manifest';m.write_text(hashlib.sha256(z.read_bytes()).hexdigest()+'  round.zip\n')
            with self.assertRaisesRegex(ValueError,'unsafe'):stage(root,m,root/'out')
            self.assertFalse((root/'out').exists())
