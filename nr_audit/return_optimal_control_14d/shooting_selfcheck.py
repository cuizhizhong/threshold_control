"""shooting实现的局部导数与独立积分核对；显式运行才计算。"""
import json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from shooting import parameters, starting_state, ExactPlateau, TailMap


def main():
    rows=[]
    for case,T in [('base',20.),('xian',500.)]:
        p=parameters(case)
        start=starting_state(case)
        plateau=ExactPlateau(p,start,5,quadrature=8)
        z=np.r_[T,np.linspace(.2,.8,5)]
        out=plateau(z)
        ej=[]; cj=[]
        for k in range(len(z)):
            delta=1e-5*max(1.,abs(z[k]))
            zp=z.copy(); zm=z.copy(); zp[k]+=delta; zm[k]-=delta
            pp=plateau(zp); pm=plateau(zm)
            ej.append(np.max(abs((pp['final']-pm['final'])/(2*delta)-out['gradient'][:,k])))
            cj.append(abs((pp['J']-pm['J'])/(2*delta)-out['J_gradient'][k]))
        v=np.array([start['s_N'],start['sq_N'],0.])
        # 单独的自适应ODE给出平台传播和成本参照。
        for lam in z[1:]:
            def rhs(t,y):
                s,sq,J=y
                f=p['beta']*p['c0']*p['theta']*(p['sc']+lam*(s-p['sc']))
                a=(1-p['beta'])/p['beta']
                k=p['gamma']*p['theta']
                x=lam+(1-lam)*p['sc']/s
                uq=1-p['sc']/(x*s)
                return [-f/p['beta']+a*k+p['omega']*sq,
                        a*(f-k)-p['omega']*sq,(1-x)**2+2*uq**2]
            sol=solve_ivp(rhs,(0,T/5),v,rtol=1e-12,atol=1e-14,method='DOP853')
            v=sol.y[:,-1]
        qtest=min(.01,p['sc']*.01)
        tail=TailMap(p)
        ta=tail(qtest)
        eps=1e-6
        derivative=(tail(qtest+eps)['u_inf_N']-tail(qtest-eps)['u_inf_N'])/(2*eps)
        row=dict(case=case,start=start,
                 state_gradient_max_abs=max(ej),cost_gradient_max_abs=max(cj),
                 state_expm_vs_ivp_max_abs=float(np.max(abs(out['final'][:2]-v[:2]))),
                 J_gauss_vs_ivp_abs=float(abs(out['J']-v[2])),
                 tail_derivative_abs=float(abs(derivative-ta['du_inf_dsq'])),
                 tail_evaluations=tail.calls,start_ode_solves=1,plateau_ode_solves=5,
                 tail_sample=ta)
        rows.append(row)
    path=Path(__file__).resolve().parent/'results'/'shooting_selfcheck.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(rows,indent=2,ensure_ascii=False))


if __name__=='__main__':
    main()
