"""Apply only the manifest-listed update to a clean main checkout. Never pushes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',required=True);parser.add_argument('--check-only',action='store_true')
    args=parser.parse_args();package=Path(__file__).resolve().parent;repo=Path(args.repo).resolve()
    manifest=json.loads((package/'UPDATE_MANIFEST.json').read_text())
    def git(*argv):
        return subprocess.check_output(['git','-C',str(repo),*argv],text=True).strip()
    if git('branch','--show-current')!='main':raise SystemExit('Stop: choose the existing main branch first.')
    if git('rev-parse','HEAD')!=manifest['base_commit']:
        raise SystemExit('Stop: main differs from the reviewed base. Reconcile newer changes; do not reset or force-push.')
    if git('status','--porcelain'):raise SystemExit('Stop: working tree is not clean. Preserve your own changes first.')
    pending=[];seen=set()
    for item in manifest['files']:
        name=item['path'];relative=Path(name)
        if name in seen or relative.is_absolute() or '..' in relative.parts:raise SystemExit('Invalid manifest path')
        seen.add(name);source=(package/'main_update'/relative).resolve();dest=repo/relative
        if not source.is_relative_to((package/'main_update').resolve()) or not dest.resolve().is_relative_to(repo):
            raise SystemExit('Path escapes the update or repository root')
        if '.git' in relative.parts:raise SystemExit('Git internals cannot be updated')
        payload=source.read_bytes()
        if len(payload)!=item['bytes'] or hashlib.sha256(payload).hexdigest()!=item['sha256']:
            raise SystemExit('Damaged package: '+name)
        if item['previous_sha256'] is None:
            if dest.exists():raise SystemExit('Unexpected existing file: '+name)
        elif not dest.is_file() or hashlib.sha256(dest.read_bytes()).hexdigest()!=item['previous_sha256']:
            raise SystemExit('Changed base file: '+name)
        pending.append((dest,payload))
    print('Verified',len(pending),'files. B9 remains HOLD.')
    if args.check_only:return
    for dest,payload in pending:
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(payload)
    print('Copied the update. Review, commit and push to main yourself; no remote action was taken.')

if __name__=='__main__':main()
