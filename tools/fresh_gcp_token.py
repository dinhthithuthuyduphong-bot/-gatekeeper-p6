"""Print a FRESHLY minted Google Cloud access token (about one hour of validity from now).

Used as GK_TOKEN_CMD by every workflow that calls Vertex AI.  `gcloud auth print-access-token` returns its cached token
while it is still valid, so a client that "refreshes" every 25 minutes can keep receiving the token minted at the start of
the job and fail with ACCESS_TOKEN_EXPIRED after about an hour (run 41193552100; docs/API_AND_FAILURES.md, 3.1).  This
script asks google-auth to refresh the service-account credentials (GOOGLE_APPLICATION_CREDENTIALS, written by
google-github-actions/auth), which always mints a new token.

python tools/fresh_gcp_token.py [--expiry]   (--expiry prints the expiry time, UTC, on stderr)
"""
import subprocess
import sys

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def mint():
    import google.auth
    import google.auth.transport.requests
    creds, _project = google.auth.default(scopes=SCOPES)
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token, creds.expiry


def main(argv):
    try:
        token, expiry = mint()
    except ImportError:
        sys.stderr.write("google-auth not installed; falling back to gcloud (may return a cached token)\n")
        p = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
        if p.returncode:
            sys.stderr.write(p.stderr)
            return p.returncode
        token, expiry = p.stdout.strip(), None
    if "--expiry" in argv:
        sys.stderr.write("expiry_utc=%s\n" % (expiry.isoformat() if expiry else "unknown"))
    print(token)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
