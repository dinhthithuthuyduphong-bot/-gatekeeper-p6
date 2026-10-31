import datetime
import io
import sys
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import fresh_gcp_token as F  # noqa: E402


class FreshTokenTest(unittest.TestCase):
    def test_mints_with_refresh_every_call(self):
        calls = []

        class Creds:
            token, expiry = None, None

            def refresh(self, _req):
                calls.append(1)
                self.token = "tok%d" % len(calls)
                self.expiry = datetime.datetime(2026, 1, 1, 1, 0)

        auth = types.ModuleType("google.auth")
        auth.default = lambda scopes: (Creds(), "proj")
        transport = types.ModuleType("google.auth.transport")
        requests_mod = types.ModuleType("google.auth.transport.requests")
        requests_mod.Request = lambda: None
        google = types.ModuleType("google")
        google.auth = auth
        auth.transport = transport
        transport.requests = requests_mod
        mods = {"google": google, "google.auth": auth, "google.auth.transport": transport, "google.auth.transport.requests": requests_mod}
        with mock.patch.dict(sys.modules, mods):
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(F.main([]), 0)
                self.assertEqual(F.main([]), 0)
        self.assertEqual(out.getvalue().split(), ["tok1", "tok2"])      # a new token each call, nothing cached
        self.assertEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()
