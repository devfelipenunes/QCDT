import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from scripts.replay_history import replay

class ReplayTests(unittest.TestCase):
    def test_success_and_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            name='quantum_research_bundle.zip'
            with ZipFile(p/name,'w') as z:
                z.writestr('qcdt.py',"from pathlib import Path\nPath('output.json').write_text('{}')\nprint('ok')\n")
            digest=hashlib.sha256((p/name).read_bytes()).hexdigest()
            m=p/'manifest'
            m.write_text(f'{digest}  {name}\n')
            report=replay(p,m,p/'out',10,1,(('bundle','qcdt.py'),))
            self.assertEqual(report['rows'][0]['status'],'pass')
            self.assertEqual((p/'out/bundle_qcdt.py.log').read_text().strip(),'ok')
            self.assertFalse((p/'output.json').exists())
            self.assertEqual(json.loads((p/'out/replay.json').read_text()),report)
    def test_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            name='quantum_research_bundle.zip'
            with ZipFile(p/name,'w') as z:
                z.writestr('qcdt.py','raise SystemExit(3)')
            m=p/'manifest'
            m.write_text(f'{hashlib.sha256((p/name).read_bytes()).hexdigest()}  {name}\n')
            report=replay(p,m,p/'out',10,1,(('bundle','qcdt.py'),))
            self.assertEqual((report['rows'][0]['status'],report['rows'][0]['returncode']),('fail',3))
