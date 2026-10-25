import ast,json,subprocess,sys,hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent/'research_closure_20261024/repo'
sys.path.insert(0,str(ROOT))
from gatekeeper_ext.none_identity import register
from gatekeeper_lite.skill import Skill
from gatekeeper_lite.transforms import Abstain
register()

def one(repo):
    name=repo.replace('/','__');dest=BASE/'upstream'/name;log=BASE/'logs'/(name+'.clone.log')
    row={'repository':repo,'evidence':'EXPLORATORY_STATIC_SCREEN','test_runs':0}
    try:
        command=['git','-c','gc.auto=0','clone','--depth=1','https://github.com/'+repo+'.git',str(dest)]
        p=subprocess.run(command,capture_output=True,text=True,timeout=90)
        log.write_text(json.dumps({'command':command,'returncode':p.returncode})+'\n'+p.stdout+p.stderr)
        if p.returncode:raise RuntimeError('clone failed')
        row['revision']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=dest,text=True).strip()
        row['license_files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.iterdir() if p.is_file() and p.name.lower().startswith(('license','copying'))}
        skill=Skill.load(ROOT/'study_g/skills/none-identity.json').transform();sites=[];errors=[]
        for path in sorted(dest.rglob('*.py')):
            parts=path.relative_to(dest).parts
            if path.is_symlink() or any(x in ('tests','test','testing','doc','docs','examples','.git') for x in parts) or path.name.startswith('test_'):continue
            source=path.read_text(errors='replace')
            try:result=skill.apply(source,single_site=False)
            except Abstain:continue
            except Exception as exc:errors.append({'file':str(path.relative_to(dest)),'error':str(exc)});continue
            for site in result.sites:sites.append({'file':str(path.relative_to(dest)),'function':site.function,'line':site.lineno,'snippet':site.snippet})
        row.update(status='STATIC_ONLY',sites=sites,errors=errors)
    except Exception as exc:row.update(status='BLOCKED',error=str(exc))
    (BASE/'logs'/(name+'.scan.json')).write_text(json.dumps(row,indent=2))
    print(json.dumps(row),flush=True)
    return row

if __name__=='__main__':
    selection=json.loads((BASE/'SELECTION.json').read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(one,selection['ordered_repositories']))
    (BASE/'CURRENT_SCREEN.json').write_text(json.dumps(rows,indent=2))
