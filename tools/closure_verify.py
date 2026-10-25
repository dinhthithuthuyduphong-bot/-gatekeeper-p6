"""Reproduce the zero-paid-cost closure checks; preserve stdout/stderr and exit codes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent.parent


def main(output):
    out=Path(output).resolve()
    if out.exists() and any(out.iterdir()):raise ValueError('choose a new output directory')
    out.mkdir(parents=True,exist_ok=True);records=[]
    def execute(label,args):
        start=time.perf_counter();command=[sys.executable,*args]
        print('RUN',label,json.dumps(command),flush=True)
        p=subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
        (out/(label+'.log')).write_text(p.stdout+p.stderr)
        row={'check':label,'command':command,'returncode':p.returncode,'seconds':time.perf_counter()-start}
        records.append(row);print('CHECK',json.dumps(row),flush=True)
        (out/'CHECKS.json').write_text(json.dumps({'model_calls':0,'checks':records},indent=2))
        if p.returncode:raise RuntimeError(label+' failed; inspect '+str(out/(label+'.log')))
    execute('unit_tests',['-m','unittest','discover','-s','tests','-v'])
    for study in ['study_d','study_e','study_f','study_g','study_h']:
        execute('freeze_'+study,['tools/freeze_study.py','verify',study])
    execute('results_check',['tools/results_check.py'])
    execute('study_i_ci_raw_audit',['study_i/verify.py','--results','study_i/results/ci-40084717332/inputs',
                                  '--output',str(out/'study_i_verified')])
    execute('study_k_raw_audit',['study_k/verify.py','--results','study_k/results/local-20261025-clean',
                               '--output',str(out/'STUDY_K_VERIFIED.json')])
    execute('statistics_replay',['tools/closure_statistics.py','--out',str(out/'statistics')])
    execute('cost_raw_audit',['tools/verify_cost_evidence.py','--out',str(out/'COST_VERIFIED.json')])
    execute('prospective_status',['tools/prospective_preflight.py','--report-only','--out',str(out/'PROSPECTIVE_STATUS.json')])
    sys.path.insert(0,str(ROOT))
    from tools.preflight_b9 import validate
    from datetime import datetime,timezone
    try:
        validate('study_d/b9_config.json','D1_py_ecc','deepseek-flash','record',
                 now=datetime(2026,11,1,tzinfo=timezone.utc))
    except ValueError as exc:
        if 'HOLD' not in str(exc):raise
        (out/'paid_hold.log').write_text('EXPECTED BLOCK: '+str(exc)+'\n')
    else:raise RuntimeError('paid preflight unexpectedly allowed record')
    release=json.loads((ROOT/'pre_b9/RELEASE_GATE.json').read_text())
    if release['status']!='HOLD':raise RuntimeError('release gate was changed')
    # Parse workflow events with BaseLoader so YAML 1.1 does not turn `on` into True.
    import yaml
    for name in ['study-i-zero-cost.yml','study-k-zero-cost.yml','research-closure-zero-cost.yml',
                 'next-evidence-zero-cost.yml']:
        path=ROOT/'.github/workflows'/name
        doc=yaml.load(path.read_text(),Loader=yaml.BaseLoader)
        if path.stat().st_size>500*1024 or 'workflow_dispatch' not in doc.get('on',{}):
            raise RuntimeError('invalid workflow trigger/size: '+name)
        if doc.get('permissions',{}).get('contents')!='read':raise RuntimeError('audit workflow must be read-only')
    receipt={'status':'PASS_ZERO_PAID_API_CHECKS','model_calls':0,'B9':'HOLD','checks':records,
             'prospective_status':json.loads((out/'PROSPECTIVE_STATUS.json').read_text())['status'],
             'note':'PASS validates implementation and recorded evidence; it does not mean empirical weaknesses are closed.'}
    (out/'VALIDATION.json').write_text(json.dumps(receipt,indent=2))
    (out/'RESULT.md').write_text('# Zero-cost closure validation\n\n'+
        '\n'.join('- '+x['check']+': PASS (exit 0)' for x in records)+
        '\n- Paid B9 preflight after 31/10: expected HOLD.\n- Workflow triggers/size/read-only permissions: PASS.\n'+
        '- Study J readiness: '+receipt['prospective_status']+'; no fresh outcomes exist.\n')
    print(json.dumps(receipt,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);a=p.parse_args();main(a.out)
