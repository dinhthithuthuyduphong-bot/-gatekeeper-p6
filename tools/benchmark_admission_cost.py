"""Measure real sequential versus full-draw validation on the known Study I targets.

Each arm pays the SAME selected-module census and fresh-worker setup. This is
an exploratory cost microbenchmark, not new target evidence or a model trial.
Dependency installation/source download are separately excluded from warm evaluation.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import shutil
import statistics
import sys
import time

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from study_i.run import digest,run_command,xml_cases
from gatekeeper_ext.none_identity import register
from gatekeeper_lite.gatekeeper import bind_modules
from gatekeeper_lite.skill import Skill,Target
from gatekeeper_lite import drawharness


def benchmark(target_name,source,out,repetitions=3):
    source=Path(source).resolve();out=Path(out).resolve()
    if repetitions<3:raise ValueError('at least three repetitions')
    if out.exists() and any(out.iterdir()):raise ValueError('output must be new/empty')
    out.mkdir(parents=True)
    config=json.loads((ROOT/'study_i/targets.json').read_text());cfg=config['targets'][target_name]
    if list(sys.version_info[:2])!=cfg['python']:raise ValueError('wrong Python minor')
    for rel,sha in config['gatekeeper_sha256'].items():
        if digest(ROOT/rel)!=sha:raise ValueError('frozen core changed: '+rel)
    original=json.loads((ROOT/'study_i/results/ci-40084717332/inputs'/target_name/'RESULT.json').read_text())
    for rel,sha in original['source_and_test_sha256'].items():
        if digest(source/rel)!=sha:raise ValueError('source/test hash changed: '+rel)
    schedule=[]
    for rep in range(repetitions):
        modes=['sequential','full_draws'];random.Random(20261024+rep).shuffle(modes)
        schedule.extend((rep,mode) for mode in modes)
    pre={'evidence':'EXPLORATORY_REAL_WALL_CLOCK','target':cfg['target_id'],'repetitions':repetitions,
         'schedule':schedule,'source_revision':cfg['revision'],'source_hashes':original['source_and_test_sha256'],
         'python':sys.version,'packages':sorted((d.metadata['Name'],d.version) for d in importlib.metadata.distributions()),
         'code_sha256':digest(Path(__file__)),'scope':'selected-module census + paired generated draws',
         'excluded_costs':['dependency installation','source download'],'model_calls':0,'model_cost_usd':0}
    (out/'PRE_EXECUTION.json').write_text(json.dumps(pre,indent=2))
    register();rows=[]
    for rep,mode in schedule:
        label=f'{rep}_{mode}';directory=out/label;directory.mkdir()
        start=time.perf_counter()
        target=Target(cfg['target_id'],source,{'modules':cfg['modules'],'pythonpath':cfg['pythonpath']})
        bound=bind_modules([Skill.load(ROOT/'study_g/skills/none-identity.json')],target)
        if len(bound['sites'])!=cfg['site_count']:raise ValueError('binding count changed')
        states={};census_seconds=0
        for arm in ('baseline','treated'):
            snapshot=directory/'work'/arm
            shutil.copytree(source,snapshot,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','.pytest_cache'))
            if arm=='treated':
                for rel,text in bound['treated'].items():(snapshot/rel).write_text(text)
            for rel in cfg['census']:
                if digest(snapshot/rel)!=original['source_and_test_sha256'][rel]:raise ValueError('test changed')
            xml=directory/(arm+'.xml')
            if cfg['test_runner']=='pytest':
                command=[sys.executable,'-m','pytest','-q','-o','addopts=','-p','no:cacheprovider','--junitxml='+str(xml),*cfg['census']]
            else:
                command=[sys.executable,'-m','nose','--with-xunit','--xunit-file='+str(xml),*cfg['census']]
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',
                     PYTHONPATH=os.pathsep.join([str(snapshot/p) for p in cfg['pythonpath']]+[str(snapshot)]))
            execution=run_command(command,snapshot,directory/(arm+'.log'),env=env)
            if execution['returncode'] not in (0,1):raise RuntimeError('census environment error')
            states[arm]=xml_cases(xml)
            if any(v['status']=='error' for v in states[arm].values()):raise RuntimeError('census setup/collection error')
            census_seconds+=execution['seconds']
        if states['baseline'].keys()!=states['treated'].keys():raise RuntimeError('census inventory mismatch')
        if any(v['status']=='failure' for v in states['baseline'].values()):raise RuntimeError('baseline failed')
        regressions=[k for k,v in states['baseline'].items() if v['status']=='passed' and states['treated'][k]['status']!='passed']
        setup_seconds=time.perf_counter()-start-census_seconds
        previous_load=drawharness._load
        def logging_load(path):
            module=previous_load(path);judge=module.judge
            def logged(scope,draw,without,with_):
                pw,pt=judge(scope,draw,without,with_)
                with (directory/'draws.jsonl').open('a') as stream:
                    stream.write(json.dumps({'scope':scope,'draw':draw,'without':without,'with':with_,
                                            'z':int(not pt)-int(not pw)},allow_nan=False)+'\n')
                return pw,pt
            module.judge=logged;return module
        drawharness._load=logging_load
        draw_start=time.perf_counter()
        try:
            result=drawharness.run_draw_study(target,bound['treated'],ROOT/'study_i'/cfg['draw_oracle'],
                  dict(config['diagnostic_draws'],b8_full=mode=='full_draws'),len(config['diagnostic_draws']['cells']))
        finally:drawharness._load=previous_load
        draw_seconds=time.perf_counter()-draw_start
        for s in result['scopes'].values():
            counts=(s.get('b8') or s)['counts']
            if counts['harness_error']:raise RuntimeError('draw harness error')
        row={'rep':rep,'mode':mode,'seconds':time.perf_counter()-start,'setup_copy_seconds':setup_seconds,
             'census_seconds':census_seconds,'draw_pipeline_seconds':draw_seconds,
             'paired_draws':sum(len(s['trace']) for s in result['scopes'].values()),
             'census_regressions':regressions,'draw_result':result}
        (directory/'RESULT.json').write_text(json.dumps(row,indent=2,allow_nan=False));rows.append(row)
        print('MEASURED_POLICY',json.dumps({k:v for k,v in row.items() if k not in ('draw_result','census_regressions')}),flush=True)
        shutil.rmtree(directory/'work')
    means={m:{k:statistics.mean(r[k] for r in rows if r['mode']==m) for k in
               ('seconds','census_seconds','draw_pipeline_seconds','setup_copy_seconds','paired_draws')}
           for m in ('sequential','full_draws')}
    # The stopped evidence must be identical; timing is the only repeated outcome.
    for rep in range(repetitions):
        a,b=[next(r for r in rows if r['rep']==rep and r['mode']==m) for m in ('sequential','full_draws')]
        if a['census_regressions']!=b['census_regressions']:raise RuntimeError('census changed between modes')
        for scope in a['draw_result']['scopes']:
            x,y=a['draw_result']['scopes'][scope],b['draw_result']['scopes'][scope]
            if any(x[k]!=y[k] for k in ('decision','draws','e_min')):raise RuntimeError('stopped decision mismatch')
    record=dict(pre,status='MEASURED_AND_DECISIONS_MATCH',measurements=rows,means=means)
    (out/'COST_RESULT.json').write_text(json.dumps(record,indent=2,allow_nan=False))
    lines=['# Chi phí chạy thật: '+cfg['target_id'],'',
           'Hậu kiểm trên target đã biết; 0 lượt gọi model. Cả hai chính sách trả cùng census và worker/snapshot setup.','',
           '| Chính sách | Tổng giây TB | Census giây TB | Draw pipeline giây TB | Paired draws TB |','|---|---|---|---|---|']
    for m,v in means.items():lines.append(f"| {m} | {v['seconds']:.4f} | {v['census_seconds']:.4f} | {v['draw_pipeline_seconds']:.4f} | {v['paired_draws']:.0f} |")
    saving=1-means['sequential']['seconds']/means['full_draws']['seconds']
    lines+=['',f'Chênh lệch tổng thời gian trung bình: {saving:.2%} ít hơn khi sequential (âm nghĩa là chậm hơn).',
            'Ba lần lặp thời gian trên cùng workload/seed không phải ba target độc lập; không suy ra speedup tổng quát.',
            'So sánh này đo dừng thật với tiếp tục đủ draws, không chứng minh thắng baseline chỉ chạy census.',
            'Census-only đã bắt được SQLAlchemy; phần draw bổ sung vẫn là overhead so với census-only trên case đó.',
            'Không cộng thời gian download/install vào warm evaluation. Raw log, XML, paired outcomes và số đo từng lần được giữ cạnh báo cáo.']
    (out/'COST_RESULT.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('target',choices=['sqlalchemy','networkx'])
    p.add_argument('--checkout',required=True);p.add_argument('--out',required=True);p.add_argument('--repetitions',type=int,default=3)
    a=p.parse_args();benchmark(a.target,a.checkout,a.out,a.repetitions)
