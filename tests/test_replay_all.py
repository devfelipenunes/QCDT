import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from scripts.replay_all import replay

class FullReplayTests(unittest.TestCase):
    def test_context_comparison_and_failure(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);arc=root/'test.zip'
            with ZipFile(arc,'w') as z:
                z.writestr('helper.py','VALUE=4\n')
                z.writestr('experiment.py',"from pathlib import Path\nfrom helper import VALUE\nimport json\nif __name__=='__main__':\n Path('result.json').write_text(json.dumps({'value':VALUE,'seconds':2}))\n")
                z.writestr('result.json','{"value":4,"seconds":1}')
                z.writestr('fail.py',"if __name__=='__main__':\n raise SystemExit(2)\n")
            manifest=root/'manifest';manifest.write_text(hashlib.sha256(arc.read_bytes()).hexdigest()+'  test.zip\n')
            result=replay(root,'test.zip',manifest,root/'out',timeout=10,workers=2)
            rows={r['path']:r for r in result['rows']}
            self.assertEqual(result['compiled'],3)
            self.assertEqual(rows['helper.py']['kind'],'module_smoke')
            self.assertEqual(rows['experiment.py']['comparisons'][0]['comparison'],'match')
            self.assertEqual(rows['fail.py']['status'],'fail')
