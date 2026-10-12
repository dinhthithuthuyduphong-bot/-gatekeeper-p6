"""Linux-only synthetic container smoke test. No installs, pull, or model calls.

Run only on an authorized disposable Linux host with an existing Docker daemon.
This is NOT a production sandbox certification or a prospective trial runner.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tempfile
import uuid

BASELINE = 'def classify(x):\n    return "integer" if isinstance(x, int) else "other"\n'
TREATMENT = BASELINE.replace('isinstance(x, int)', 'isinstance(x, int) and not isinstance(x, bool)')
LABEL = 'gatekeeper.p6.run'
PROBE = '''import hashlib, importlib.util, json, os
from pathlib import Path
spec=importlib.util.spec_from_file_location("target", "/work/target.py")
target=importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)
cases=[("int_zero",0,"integer"),("int_one",1,"integer"),("bool_true",True,"other"),("string","1","other"),("none",None,"other"),("float",1.5,"other")]
result={"tests":[{"id":name,"passed":target.classify(value)==expected} for name,value,expected in cases]}
result["uid"]=os.getuid()
result["root_mount_writable"]="rw" in next(line.split()[3].split(",") for line in Path("/proc/mounts").read_text().splitlines() if line.split()[1]=="/")
result["interfaces"]=sorted(p.name for p in Path("/sys/class/net").iterdir())
result["target_sha256"]=hashlib.sha256(Path("/work/target.py").read_bytes()).hexdigest()
result["github_token_present"]="GITHUB_TOKEN" in os.environ
print(json.dumps(result))
'''

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def image_id(value):
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', value):
        raise ValueError('Use a locally available immutable image ID, not a mutable tag')
    return value

def create_command(image, folder, run_id):
    image_id(image)
    folder=Path(folder).resolve()
    if not folder.is_dir() or ',' in str(folder):
        raise ValueError('Invalid fixture directory')
    if not re.fullmatch(r'[0-9a-f]{32}', run_id):
        raise ValueError('Invalid run identity')
    return ['docker','create','--pull=never','--label',LABEL+'='+run_id,
            '--network=none','--read-only','--user=65534:65534',
            '--cap-drop=ALL','--security-opt=no-new-privileges:true',
            '--memory=256m','--memory-swap=256m','--cpus=1','--pids-limit=64',
            '--init','--tmpfs','/tmp:rw,noexec,nosuid,size=16m',
            '--mount','type=bind,src='+str(folder)+',dst=/work,readonly',
            '--env','PYTHONHASHSEED=1729','--entrypoint=python',
            image,'-I','-B','/work/probe.py']

def checked(command, timeout=20):
    r=subprocess.run(command,capture_output=True,text=True,timeout=timeout)
    if r.returncode:
        raise RuntimeError('Command failed: '+command[0]+' '+command[1]+': '+r.stderr[:800])
    return r.stdout

def verify_settings(obj, image, folder, run_id):
    h,c=obj['HostConfig'],obj['Config']
    mounts=obj['Mounts']
    checks={
        'image':obj['Image']==image,
        'label':c.get('Labels',{}).get(LABEL)==run_id,
        'network_none':h['NetworkMode']=='none',
        'root_readonly':h['ReadonlyRootfs'] is True,
        'unprivileged':h['Privileged'] is False,
        'nonroot':c['User']=='65534:65534',
        'drop_caps':{s.upper() for s in h.get('CapDrop',[])}=={'ALL'},
        'no_new_privileges':any(s in ('no-new-privileges','no-new-privileges:true') for s in h.get('SecurityOpt',[])),
        'cpu_limit':h.get('NanoCpus')==1000000000,
        'memory_limit':h['Memory']==268435456 and h['MemorySwap']==268435456,
        'pid_limit':h['PidsLimit']==64,
        'single_readonly_fixture':len([m for m in mounts if m['Type']=='bind'])==1 and any(
            m['Type']=='bind' and m['Source']==str(Path(folder).resolve()) and m['Destination']=='/work' and m['RW'] is False for m in mounts),
        'no_token_env':not any(x.split('=',1)[0] in ('GITHUB_TOKEN','ACTIONS_RUNTIME_TOKEN') for x in c.get('Env',[])),
    }
    if not all(checks.values()):
        raise ValueError('Container configuration mismatch: '+str(checks))
    return checks

def verify_probe(record, expected_sha, arm):
    expected=[('int_zero',True),('int_one',True),('bool_true',arm=='treatment'),('string',True),('none',True),('float',True)]
    require([(r['id'],r['passed']) for r in record['tests']]==expected,'Unexpected synthetic outcomes')
    require(record['uid']==65534 and record['root_mount_writable'] is False,'Runtime privilege/rootfs check failed')
    require(record['interfaces']==['lo'] and record['github_token_present'] is False,'Runtime network/env check failed')
    require(record['target_sha256']==expected_sha,'Target source hash mismatch')

def one_arm(image, arm, out, run_id, progress=None):
    source=BASELINE if arm=='baseline' else TREATMENT
    # World-searchable only inside a new disposable fixture dir; no private inputs.
    with tempfile.TemporaryDirectory(prefix='gk_p6_fixture_') as td:
        folder=Path(td)
        folder.chmod(0o755)
        (folder/'target.py').write_text(source,encoding='utf-8')
        (folder/'probe.py').write_text(PROBE,encoding='utf-8')
        for p in folder.iterdir(): p.chmod(0o644)
        original={p.name:sha(p.read_bytes()) for p in folder.iterdir()}
        cid=checked(create_command(image,folder,run_id)).strip()
        if not re.fullmatch(r'[0-9a-f]{64}',cid):
            raise RuntimeError('Unexpected container ID; no broad cleanup attempted')
        owned=False
        try:
            obj=json.loads(checked(['docker','inspect',cid]))[0]
            owned=obj['Config'].get('Labels',{}).get(LABEL)==run_id
            settings=verify_settings(obj,image,folder,run_id)
            if progress is not None:
                progress['container_start_attempts']+=1
            raw=checked(['docker','start','--attach',cid],timeout=30)
            record=json.loads(raw)
            state=json.loads(checked(['docker','inspect',cid]))[0]['State']
            require(state['ExitCode']==0 and not state['OOMKilled'] and not state['Running'],'Container did not finish cleanly')
            verify_probe(record,sha(source.encode()),arm)
            require(original=={p.name:sha(p.read_bytes()) for p in folder.iterdir()},'Fixture mutated')
            result={'arm':arm,'container_id':cid,'checks':settings,'probe':record,'fixture_unchanged':True}
            (out/(arm+'.json')).write_text(json.dumps(result,indent=2)+'\n')
            return result
        finally:
            # Remove only the exact ID just created and independently labelled.
            if owned:
                checked(['docker','rm','--force',cid])

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--image',required=True,type=image_id)
    parser.add_argument('--out',default='P6_REMOTE_OUTPUT')
    args=parser.parse_args()
    out=Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=False)
    result={'schema':'gk_p6_remote_smoke_v1','status':'BLOCKED',
            'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'image_id':args.image,'scope':'SYNTHETIC_DEVELOPMENT_ONLY',
            'prospective_pairs':0,'GK07_complete':False,'all_smoke_trials_completed':False,
            'container_start_attempts':0,
            'limitations':['No source repository trial','No hidden oracle','Not a security audit','No population guarantee','Repeated fixture tasks are not fresh statistical trials']}
    try:
        if platform.system()!='Linux' or not shutil.which('docker'):
            raise RuntimeError('Authorized Linux Docker host required; nothing will be installed')
        result['engine_version']=checked(['docker','version','--format','{{.Server.Version}}']).strip()
        result['image_metadata']=json.loads(checked(['docker','image','inspect',args.image]))[0]['RepoDigests']
        result['runs']=[]
        for i,order in enumerate((('baseline','treatment'),('treatment','baseline')),1):
            dest=out/('round_'+str(i))
            dest.mkdir()
            result['runs'].append([])
            for arm in order:
                result['runs'][-1].append(one_arm(args.image,arm,dest,uuid.uuid4().hex,result))
        result.update(status='PASS_SYNTHETIC_CONTAINER_SMOKE',all_smoke_trials_completed=True)
    except Exception as exc:
        result.update(status='BLOCKED_OR_FAILED',error=type(exc).__name__+': '+str(exc))
    finally:
        (out/'P6_REMOTE_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return 0 if result['status']=='PASS_SYNTHETIC_CONTAINER_SMOKE' else 2

if __name__=='__main__':
    raise SystemExit(main())
