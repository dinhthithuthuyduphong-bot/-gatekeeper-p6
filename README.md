# Gatekeeper P6 — synthetic container smoke test

This private research repository contains a synthetic fixture, container runner,
mocked mechanism tests, and a manually triggered GitHub Actions workflow\.
It contains no company code, manuscript PDFs, model credentials, or real benchmark data\.

## Files

- `RUN_P6_REMOTE.py`: runner for an authorized Linux host with Docker already available\.
- `tests/test_remote.py`: 14 local mechanism checks using mocks where Docker is involved\.
- `.github/workflows/p6-remote-smoke.yml`: manual workflow; no push, pull request, or schedule trigger\.

## Before running

Verify permitted service use, remaining Actions allowance and account safeguards
against new paid overage\. A checkbox, 10\-minute timeout and 1\-day artifact retention
are not billing caps\. No paid spending is authorized by this repository\.
Do not install Docker or WSL on the company Windows computer\.

Once those checks are complete, open Actions \> Gatekeeper P6 synthetic smoke \>
Run workflow\. Select the default branch and confirm the permission/budget input\.
Download the `P6_REMOTE_OUTPUT` artifact promptly: its retention is one day\.
Return `P6_REMOTE_OUTPUT.zip` for review, including failures\. If no artifact exists,
return the run URL and failed\-step log after removing any sensitive information\.

## Expected result and limits

Four fresh containers run two counterbalanced rounds of the same fixture\.
Baseline: 5/6 passing cases; treatment: 6/6\. The baseline failure is intentional\.
A successful overall receipt reports `PASS_SYNTHETIC_CONTAINER_SMOKE`\.
This is not evidence of independent statistical trials, real\-repository transfer,
production sandbox security, or results matching a research paper\.
GK\-07 remains incomplete until the broader runner requirements are validated\.

The bootstrap image tag can change across workflow runs; each individual run
resolves and records the immutable local image ID before starting containers\.
No model API is called and no API key is required for this smoke test\.
