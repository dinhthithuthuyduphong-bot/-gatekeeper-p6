"""Zero-API post-hoc comparison on unchanged Study H traces, with raw per-family decisions."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from gatekeeper_lite.eprocess import BettingEProcess,HarmCertEProcess,HarmAlarmEProcess,e_holm
from gatekeeper_ext.robust_cert import AdaptiveHarmCert,BalancedHarmCert,binomial_cdf,fixed_iut_pvalue,holm


def sequential(trace,cfg,k,certificate):
    ben=BettingEProcess(cfg['theta']); cert=certificate(cfg['eta']); alarm=HarmAlarmEProcess(cfg['eta'])
    for n,(z,h) in enumerate(trace[:cfg['n_max']],1):
        ben.update(z);cert.update(h);alarm.update(h)
        if alarm.value >= 1/cfg['alpha_alarm']:return 0.,n,'REJECT_HARM'
        if min(ben.value,cert.value)>=k/cfg['alpha']:return min(ben.value,cert.value),n,'THRESHOLD'
    return min(ben.value,cert.value),n,'BUDGET'


def analyze(config,result,outdir):
    cfg=json.loads(Path(config).read_text()); data=json.loads(Path(result).read_text())
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    if (out/'families.jsonl').exists():raise ValueError('output exists; keep previous logs')
    cells=cfg['cells'];k=len(cells);R=len(data['replications'])
    census_ok=data['census']['status']=='VALID' and not data['census']['new_failures']
    null={c for c in cells if cfg['rho_by_cell'][c]>=cfg['eta']}
    aggregate={};raw=[]
    for rep in data['replications']:
        traces={c:rep['scopes'][c]['trace'] for c in cells}
        if any(len(t)!=cfg['n_max'] for t in traces.values()):raise ValueError('truncated trace')
        decisions={}
        for name,cert in [('GK original',HarmCertEProcess),('GK adaptive (post hoc)',AdaptiveHarmCert),
                          ('GK balanced mixture (post hoc)',BalancedHarmCert)]:
            states={c:sequential(traces[c],cfg,k,cert) for c in cells}
            es={c:(states[c][0] if census_ok else 0) for c in cells}
            selected=set(e_holm(es,cfg['alpha']))
            decisions[name]={'selected':sorted(selected),'draws':sum(s[1] for s in states.values()),
                             'cells':{c:{'e':es[c],'n':states[c][1],'stop':states[c][2]} for c in cells}}
            if name=='GK original':
                assert selected=={c for c in cells if rep['scopes'][c]['decision']=='ADMIT'},'original replay mismatch'
        for n in [100,200,300]:
            p={c:fixed_iut_pvalue(traces[c],n,cfg['theta'],cfg['eta']) if census_ok else 1 for c in cells}
            for label,chosen in [('IUT Bonferroni',{c for c in cells if p[c]<=cfg['alpha']/k}),
                                 ('IUT Holm',set(holm(p,cfg['alpha'])))]:
                decisions[f'Fixed {n}, {label}']={'selected':sorted(chosen),'draws':n*k,'pvalues':p}
        for name,d in decisions.items():
            a=aggregate.setdefault(name,{'false_families':0,'draws':0,'admitted':{c:0 for c in cells}})
            a['false_families']+=bool(set(d['selected'])&null);a['draws']+=d['draws']
            for c in d['selected']:a['admitted'][c]+=1
        row={'rep':rep['rep'],'decisions':decisions};raw.append(row)
        print('FAMILY',rep['rep'],json.dumps({m:d['selected'] for m,d in decisions.items()}),flush=True)
    (out/'families.jsonl').write_text(''.join(json.dumps(x,allow_nan=False)+'\n' for x in raw))
    summary={'evidence':'POST_HOC_REPLAY_NOT_NEW_TARGETS','model_calls':0,'replications':R,
             'config_sha256':hashlib.sha256(Path(config).read_bytes()).hexdigest(),
             'source_sha256':hashlib.sha256(Path(result).read_bytes()).hexdigest(),'methods':aggregate}
    (out/'STATISTICS.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
    lines=['# Kết quả kiểm toán baseline và power (0 API)','',
           'Phân tích hậu kiểm trên cùng 50 họ Study H; không phải nghiên cứu tiến cứu mới. Các bảng gốc được giữ nguyên.','',
           '| Phương pháp | Họ admit sai | '+ ' | '.join(f"h={cfg['rho_by_cell'][c]:.0%}" for c in cells)+' | Draw/họ |',
           '|---|---|'+ '---|'*len(cells)+'---|']
    for name,a in aggregate.items():
        lines.append(f"| {name} | {a['false_families']}/{R} | "+' | '.join(str(a['admitted'][c]) for c in cells)+f" | {a['draws']/R:.2f} |")
    lines+=['','Fixed IUT dùng max(p_benefit,p_harm), không chia đôi alpha trong một ô. Holm kiểm soát FWER trên cả họ với p-value hợp lệ; không cần độc lập giữa các ô.',
            'P-value lợi ích vẫn dùng Hoeffding nên đây chưa phải baseline fixed-size tối ưu. Mỗi n là một chính sách riêng; không được chọn n hậu kiểm rồi tuyên bố còn cùng bảo đảm.',
            'Số draw là replay trên trace; không phải đo tiết kiệm wall-clock. Các chứng chỉ mới chưa thay primary rule.',
            f'Nếu quan sát 0/{R} họ có lỗi, cận trên nhị thức một phía 95% là {1-.05**(1/R):.4%}; không gọi đó là chứng minh FWER=0.','',
            '## Cỡ mẫu cho riêng chứng chỉ ít hại','',
            'Tính chính xác theo mô hình Binomial với mức alpha/K. Đây là xác suất qua riêng cổng harm ở fixed n; xác suất admit đầy đủ không thể cao hơn khi còn cổng benefit/census.','',
            '| n | Số harm tối đa được chứng nhận | Power h=0% | h=1% | h=2% | h=3% |','|---|---|---|---|---|---|']
    planning=[]
    for n in [100,200,300,500,1000,2000]:
        critical=-1
        for x in range(n+1):
            if binomial_cdf(x,n,cfg['eta'])<=cfg['alpha']/k:critical=x
            else:break
        powers={str(h):binomial_cdf(critical,n,h) for h in [0,.01,.02,.03]}
        planning.append({'n':n,'max_harms':critical,'harm_only_power':powers})
        lines.append(f'| {n} | {critical} | '+' | '.join(f'{p:.1%}' for p in powers.values())+' |')
    (out/'POWER_PLANNING.json').write_text(json.dumps(planning,indent=2))
    (out/'STATISTICS_RESULT.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',default='study_h/config_study_h.json');p.add_argument('--result',default='study_h/results/RESULT_H1_rare.json')
    p.add_argument('--out',required=True);a=p.parse_args();analyze(a.config,a.result,a.out)
