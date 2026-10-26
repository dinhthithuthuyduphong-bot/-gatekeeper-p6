import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import vertex_smoke as V  # noqa: E402

CFG = {"models": [
    {"name": "vertex-x", "model_id": "google/m", "base_url": "https://h/v1/projects/{GCP_PROJECT}/endpoints/openapi", "key_env": "TOK",
     "extra": {"reasoning_effort": "low"}, "prices_usd_per_mtok": {"input": 2.0, "output": 12.0}},
    {"name": "other", "model_id": "m2", "base_url": "https://o", "key_env": "NOT_SET", "extra": {}}]}


class Resp:
    status = 200

    def __init__(self, body):
        self._b = json.dumps(body).encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def m_probe_tokens(res):
    return res["models"]["vertex-x"]["probe"][0] and 1000


class Smoke(unittest.TestCase):
    def run_with(self, opener):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "c.json"
            cfg.write_text(json.dumps(CFG))
            V.main(str(cfg), str(Path(tmp) / "o"), 3, opener, {"TOK": "secret", "GCP_PROJECT": "proj"})
            return json.loads((Path(tmp) / "o" / "VERTEX_SMOKE.json").read_text()), (Path(tmp) / "o" / "VERTEX_SMOKE.md").read_text()

    def test_same_request_shape_as_the_pipeline_and_cost_from_usage(self):
        seen = []

        def opener(req, timeout=0):
            seen.append((req.full_url, json.loads(req.data), req.headers))
            return Resp({"model": "served", "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
                         "usage": {"prompt_tokens": 10, "total_tokens": 22, "completion_tokens_details": {"reasoning_tokens": 12}}})
        res, md = self.run_with(opener)
        url, payload, headers = seen[0]
        self.assertEqual(url, "https://h/v1/projects/proj/endpoints/openapi/chat/completions")
        self.assertEqual((payload["model"], payload["max_tokens"], payload["temperature"], payload["seed"], payload["reasoning_effort"]),
                         ("google/m", 16, 0, 1, "low"))
        self.assertEqual(headers["Authorization"], "Bearer secret")
        self.assertEqual(m_probe_tokens(res), 1000)
        m = res["models"]["vertex-x"]
        self.assertEqual(m["ok"], 3)
        self.assertAlmostEqual(m["implied_cost_usd"], 6 * (10 * 2.0 + 12 * 12.0) / 1e6)   # usage has no completion_tokens: total - prompt = 12
        self.assertIn("skipped", res["models"]["other"])
        self.assertNotIn("secret", json.dumps(res) + md)

    def test_quota_and_errors_are_recorded_not_raised(self):
        n = [0]

        def opener(req, timeout=0):
            n[0] += 1
            code = 429 if n[0] > 1 else 403
            raise urllib.error.HTTPError(req.full_url, code, "x", {}, io.BytesIO(b'{"error":"quota"}'))
        res, md = self.run_with(opener)
        m = res["models"]["vertex-x"]
        self.assertEqual((m["ok"], m["rate_limited"]), (0, 5))   # 3 burst + 3 probe calls: first is 403, the rest 429
        self.assertIn("quota", md)


if __name__ == "__main__":
    unittest.main()
