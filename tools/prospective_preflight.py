"""Report missing preregistration evidence without fabricating readiness or running targets."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent.parent


def check(config):
    cfg=json.loads(Path(config).read_text());reasons=[]
    require=lambda ok,msg:reasons.append(msg) if not ok else None
    require(cfg.get('model_calls_allowed') is False,'model calls must be disabled')
    require(cfg.get('cash_api_budget_usd')==0,'API budget must be zero')
    require(cfg.get('status')=='FROZEN','design has not been publicly frozen')
    require(bool(re.fullmatch('[0-9a-f]{40}',cfg.get('public_freeze_commit') or '')),'missing public freeze commit')
    require(bool(cfg.get('public_freeze_time_utc')),'missing public freeze time')
    require(bool(cfg.get('seed_beacon_receipt')),'missing post-freeze beacon receipt')
    excluded=set(json.loads((ROOT/cfg['exclusion_manifest']).read_text())['repositories'])
    targets=cfg.get('targets',[]);repos={x.get('repository') for x in targets}
    require(len(repos)>=cfg['minimum_repositories'],'not enough distinct unseen repositories')
    ids=[t.get('id') for t in targets]
    require(len(ids)==len(set(ids)),'duplicate target ids')
    for skill in cfg['required_skills']:
        require(len({t.get('repository') for t in targets if t.get('skill')==skill})>=cfg['minimum_repositories_per_skill'],
                'insufficient repositories for '+skill)
    for target in targets:
        label=str(target.get('id','unnamed'))
        require(target.get('repository') not in excluded,label+': previously exposed repository')
        require(bool(re.fullmatch('[0-9a-f]{40}',target.get('revision') or '')),label+': missing source pin')
        require(target.get('outcomes_seen_before_freeze') is False,label+': exposure not excluded')
        for key in ('oracle_path','oracle_provenance_path','license_path','baseline_receipt_path','generator_path'):
            path=ROOT/str(target.get(key,''))
            require(bool(target.get(key)) and path.is_file(),label+': missing '+key)
    return {'status':'BLOCKED' if reasons else 'STRUCTURAL_CHECK_PASSED_MANUAL_PROVENANCE_REVIEW_REQUIRED',
            'model_calls':0,'reasons':reasons,'note':'A JSON field is not proof of public timing, oracle correctness or unseen outcomes.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',default='study_j/config_study_j.json')
    p.add_argument('--report-only',action='store_true');p.add_argument('--out');a=p.parse_args();result=check(a.config)
    text=json.dumps(result,indent=2);print(text)
    if a.out:Path(a.out).write_text(text+'\n')
    sys.exit(0 if a.report_only or not result['reasons'] else 2)
