"""Evidence must fail closed when outcomes, selection or raw observations disagree."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from study_k.oracles.control_frequency import valid
from study_k.verify import audit

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "study_k/results/local-20261025-clean"


class StudyKEvidence(unittest.TestCase):
    def fixture(self, directory):
        dest=Path(directory)/"evidence"
        shutil.copytree(EVIDENCE,dest,ignore=shutil.ignore_patterns("work","__pycache__"))
        return dest

    def test_independent_numeric_oracle_rejects_wrong_response(self):
        d={"supplied":True,"omega":[1.0,2.0],"gain":2.0,"a":1.0,"b":3.0}
        values=[2.0/((1j*w)**2+1j*w+3.0) for w in d["omega"]]
        outcome={"ok":True,"omega":d["omega"],"real":[v.real for v in values],"imag":[v.imag for v in values]}
        self.assertTrue(valid(d,outcome))
        outcome["real"][0] += 0.1
        self.assertFalse(valid(d,outcome))

    def test_missing_raw_draw_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst=self.fixture(tmp);path=dst/"draws.jsonl"
            path.write_text("\n".join(path.read_text().splitlines()[:-1])+"\n")
            with contextlib.redirect_stdout(io.StringIO()),self.assertRaisesRegex(ValueError,"Incomplete draws"):
                audit(dst)

    def test_changed_generator_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst=self.fixture(tmp);path=dst/"draws.jsonl";lines=path.read_text().splitlines()
            row=json.loads(lines[0]);row["draw"]["unused_unregistered_field"]=True
            lines[0]=json.dumps(row);path.write_text("\n".join(lines)+"\n")
            with contextlib.redirect_stdout(io.StringIO()),self.assertRaisesRegex(ValueError,"Generator/order/seed"):
                audit(dst)

    def test_retrospective_result_cannot_be_relabeled(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst=self.fixture(tmp);path=dst/"RESULT.json";result=json.loads(path.read_text())
            result["not_preregistered"]=False;path.write_text(json.dumps(result))
            with self.assertRaisesRegex(ValueError,"Invalid status"):
                audit(dst)
