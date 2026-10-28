"""14天回流、时间域Radau配点；显式CLI才求解，全部输出留在本目录。"""
from __future__ import annotations
import argparse
import json
import os
import pathlib
import sys
import time

os.environ.setdefault('OMP_NUM_THREADS', '1')
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / '_runtime'))
import casadi as ca
import numpy as np
from scipy.integrate import solve_ivp
from evaluate import load_params, prepare_start

RESULTS = HERE / 'results'


def dump(path, data):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def radau(degree=3):
    tau = np.r_[0., ca.collocation_points(degree, 'radau')]
    C, D, B = np.zeros((degree+1, degree+1)), np.zeros(degree+1), np.zeros(degree+1)
    for j in range(degree+1):
        poly = np.poly1d([1.])
        for r in range(degree+1):
            if r != j:
                poly *= np.poly1d([1., -tau[r]]) / (tau[j]-tau[r])
        D[j] = poly(1.)
        derivative = np.polyder(poly)
        for r in range(degree+1):
            C[j, r] = derivative(tau[r])
        integ = np.polyint(poly)
        B[j] = integ(1.)-integ(0.)
    return tau, C, D, B


class Problem:
    def __init__(self, case, objective, n, verbose=False, infection_scale=1.):
        self.case, self.objective, self.n = case, objective, n
        self.infection_scale = infection_scale
        self.p, self.start = p, start = load_params(case), prepare_start(case)
        sc, theta, gamma, omega = p['sc_N'], p['theta'], p['gamma'], p['omega']
        self.xstart = np.array([start['y'][0], start['y'][2]])
        self.max_duration = (sum(self.xstart)-sc)/(gamma*theta/(1-p['q0']))
        self.qcrit = p['c0']*(p['beta']+(1-p['beta'])*p['q0'])*sc*theta/omega
        s = ca.MX.sym('s', 2)
        lam = ca.MX.sym('lambda')
        # 与原方程独立写出的仿射平台形式，便于核对缩放。
        excess = p['c0']*theta*lam*(s[0]-sc)
        D0 = p['c0']*(p['beta']+(1-p['beta'])*p['q0'])*sc*theta
        B0 = (1-p['beta'])*p['c0']*p['q0']*sc*theta
        rhs = ca.vertcat(-D0+omega*s[1]-excess,
                        B0-omega*s[1]+(1-p['beta'])*excess)
        x = sc/s[0]+lam*(1-sc/s[0])
        qnorm = 1-sc/(x*s[0])
        rate = (1-x)**2+2*qnorm**2
        self.f = ca.Function('platform', [s, lam], [rhs, rate])

        # 被动尾段只有退出Sq是自由初值；CVODES输出显式约束的尾段网格。
        self.tail_horizon = H = 600. if case == 'base' else 4000.
        grid = np.unique(np.r_[0.001, .01, .1, .5, 1., 2., 5., np.linspace(10., H, 161)])
        yt = ca.MX.sym('tail_y', 3)
        ss, li, qq = yt[0], yt[1], yt[2]
        ii = ca.exp(li)
        tailrhs = ca.vertcat(-p['c0']*(p['beta']+(1-p['beta'])*p['q0'])*ss*ii+omega*qq,
            p['beta']*p['c0']*(1-p['q0'])*ss-gamma,
            (1-p['beta'])*p['c0']*p['q0']*ss*ii-omega*qq)
        tailintegrator = ca.integrator(f'tail_{case}_{n}', 'cvodes', {'x': yt, 'ode': tailrhs},
            0., grid.tolist(), {'abstol': 1e-13, 'reltol': 1e-11,
             'max_num_steps': 100000, 'max_step_size': 2. if case == 'xian' else .5,
             'disable_internal_warnings': True})
        qexit = ca.MX.sym('qexit')
        tail = tailintegrator(x0=ca.vertcat(sc, np.log(theta), qexit))['xf']
        uf = tail[0,-1]+tail[2,-1]
        cnorm = (p['S0']+p['Sq0'])/p['N']-uf
        bnorm = p['beta']*p['c0']*uf*ca.exp(tail[1,-1])/(gamma*(1-uf/sc))
        self.tailfun = ca.Function(f'terminal_{case}_{n}', [qexit],
            [cnorm, tail[1,:].T-np.log(theta), bnorm, uf])
        self.tail_grid = grid

        tau, C, D, B = radau()
        w, lbw, ubw, constraints, lbg, ubg = [], [], [], [], [], []
        def var(name, size, lo, hi):
            v = ca.MX.sym(name, size)
            w.append(v)
            lbw.extend(np.broadcast_to(lo, (size,)).tolist())
            ubw.extend(np.broadcast_to(hi, (size,)).tolist())
            return v
        def con(expr, lo=0., hi=0.):
            constraints.append(ca.vec(expr))
            lbg.extend(np.broadcast_to(lo, (expr.numel(),)).tolist())
            ubg.extend(np.broadcast_to(hi, (expr.numel(),)).tolist())
        Tscaled = var('gamma_duration', 1, 1e-5, gamma*self.max_duration)
        L = var('lambda_nodes', n+1, 0., 1.)
        X = var('X0', 2, self.xstart, self.xstart)
        self.state_node_indices = [slice(1+n+1, 1+n+1+2)]
        self.collocation_indices = []
        objJ = 0.
        h = Tscaled/(gamma*n)
        for k in range(n):
            points = [X]
            for j in range(1, 4):
                self.collocation_indices.append((sum(v.numel() for v in w), k, float(tau[j])))
                points.append(var(f'X_{k}_{j}', 2, [sc, 0.], [1., 1.]))
            for j in range(1, 4):
                deriv = sum(C[r,j]*points[r] for r in range(4))
                lj = L[k]*(1-tau[j])+L[k+1]*tau[j]
                dyn, cost = self.f(points[j], lj)
                con(h*dyn-deriv)
                objJ += h*B[j]*cost
            Xend = sum(D[j]*points[j] for j in range(4))
            index = sum(v.numel() for v in w)
            X = var(f'X{k+1}', 2, [sc, 0.], [1., 1.])
            self.state_node_indices.append(slice(index, index+2))
            con(X-Xend)
        con(X[0]-sc)
        # 出口必要条件只筛查立即上升；完整尾段网格约束另行保留。
        con(X[1], 0., self.qcrit)
        cinf, postcap, bound, uf = self.tailfun(X[1])
        con(postcap, -np.inf, 0.)
        con(uf-sc, -np.inf, -1e-10)
        con(bound*p['N'], 0., 1e-5 if case == 'base' else 1e-3)
        goal = {'time': Tscaled, 'infections': infection_scale*(cinf-(p['S0']+p['Sq0'])/p['N']+sc),
                'cost': gamma*objJ/3.}[objective]
        self.w, self.lbx, self.ubx = ca.vertcat(*w), np.array(lbw), np.array(ubw)
        self.lbg, self.ubg = np.array(lbg), np.array(ubg)
        g = ca.vertcat(*constraints)
        self.inspect = ca.Function('inspect', [self.w], [g, cinf, objJ, X])
        self.solver = ca.nlpsol(f'solve_{case}_{objective}_{n}', 'ipopt', {'x':self.w,'f':goal,'g':g},
            {'print_time': False, 'ipopt.print_level': 5 if verbose else 0,
             'ipopt.sb': 'yes', 'ipopt.max_iter': 1800, 'ipopt.tol': 1e-9,
             'ipopt.constr_viol_tol': 1e-10, 'ipopt.acceptable_tol': 1e-8,
             'ipopt.acceptable_iter': 8, 'ipopt.bound_relax_factor': 0.,
             'ipopt.mu_strategy': 'adaptive', 'ipopt.linear_solver': 'mumps',
             'ipopt.nlp_scaling_method': 'none' if infection_scale!=1. else 'gradient-based'})

    def initial(self, lambda_nodes, duration=None):
        p, n = self.p, self.n
        values = np.interp(np.linspace(0,1,n+1), np.linspace(0,1,len(lambda_nodes)), lambda_nodes)
        qref = json.loads((RESULTS/'references'/f'{self.case}_q_only.json').read_text(encoding='utf-8'))
        cref = json.loads((RESULTS/'references'/f'{self.case}_c_only.json').read_text(encoding='utf-8'))
        guess = duration or (np.mean(values)*qref['duration']+(1-np.mean(values))*cref['duration'])
        def dynamics(t, y):
            ll = np.interp(min(t/guess,1.), np.linspace(0,1,n+1), values)
            return np.asarray(self.f(y,ll)[0]).ravel()
        # 仅用于生成初值，单独统计，不冒充最优求解或独立核验。
        out = solve_ivp(dynamics, (0,guess), self.xstart, method='DOP853',rtol=1e-9,atol=1e-12,dense_output=True)
        with (RESULTS/'initial_guess_ode_log.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps({'case':self.case,'objective':self.objective,'n':n,'duration':guess,'nfev':out.nfev})+'\n')
        x0 = np.zeros(len(self.lbx))
        x0[0], x0[1:n+2] = guess*p['gamma'], values
        # 初猜允许有动态缺陷；状态边界投影仅针对NLP初猜，不用于最终回放。
        for k, sl in enumerate(self.state_node_indices):
            x0[sl] = out.sol(guess*k/n)
        for index,k,tau in self.collocation_indices:
            x0[index:index+2] = out.sol(guess*(k+tau)/n)
        return np.minimum(np.maximum(x0,self.lbx),self.ubx)

    def solve(self, initial, label):
        t0=time.perf_counter()
        attempt = f'{self.case}_{self.objective}_n{self.n}_{label}_{time.time_ns()}'
        try:
            sol=self.solver(x0=initial,lbx=self.lbx,ubx=self.ubx,lbg=self.lbg,ubg=self.ubg)
            stats=self.solver.stats()
            x=np.asarray(sol['x']).ravel()
            gv,cinf,J,exitstate=self.inspect(x)
            gv=np.asarray(gv).ravel()
            residual=float(max(np.max(self.lbg-gv),np.max(gv-self.ubg),0.))
            iterations=stats.get('iterations',{})
            result={'attempt':attempt,'case':self.case,'objective':self.objective,'method':'Radau3_IPOPT',
                'n':self.n,'seed_label':label,'duration':float(x[0]/self.p['gamma']),
                'lambda_values':x[1:self.n+2].tolist(),'interpolation':'linear',
                'state_nodes':np.array([x[sl] for sl in self.state_node_indices]).tolist(),
                'solver_success':bool(stats['success']),'return_status':stats['return_status'],
                'iter_count':int(stats['iter_count']),'scaled_objective':float(sol['f']),
                'C_infinity_estimate':float(cinf)*self.p['N'],'J':float(J),
                'constraint_residual':residual,'exit_state_N':np.asarray(exitstate).ravel().tolist(),
                'inf_pr':float(iterations['inf_pr'][-1]) if iterations.get('inf_pr') else None,
                'inf_du':float(iterations['inf_du'][-1]) if iterations.get('inf_du') else None,
                'tail_horizon':self.tail_horizon,'elapsed_seconds':time.perf_counter()-t0,
                'casadi_version':ca.__version__,'full_decision':x.tolist(),
                'oracle_counts':{k:v for k,v in stats.items() if k.startswith('n_call_')},
                'tail_grid_count':len(self.tail_grid),'infection_objective_scale':self.infection_scale}
        except Exception as exc:
            result={'attempt':attempt,'case':self.case,'objective':self.objective,'n':self.n,
                'solver_success':False,'error':str(exc),'elapsed_seconds':time.perf_counter()-t0}
        dump(RESULTS/'collocation'/f'{attempt}.json',result)
        with (RESULTS/'optimization_log.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps({k:v for k,v in result.items() if k not in ['full_decision','state_nodes','lambda_values']})+'\n')
        print(json.dumps({k:result.get(k) for k in ['attempt','solver_success','return_status','duration','J','C_infinity_estimate','constraint_residual','elapsed_seconds']}),flush=True)
        return result


def seeds(case,n):
    grid=np.linspace(0,1,n+1)
    migrate=json.loads((RESULTS/'references'/f'{case}_opt_noreturn.json').read_text(encoding='utf-8'))
    values=[('q_only',np.ones(n+1)),('c_only',np.zeros(n+1)),
        ('migrated',np.interp(grid,np.linspace(0,1,len(migrate['lambda_values'])),migrate['lambda_values'])),
        ('half',np.full(n+1,.5)),('q_then_c',np.where(grid<.5,1.,0.)),
        ('c_then_q',np.where(grid<.5,0.,1.))]
    for i in range(2):
        rng=np.random.default_rng(20261027+i)
        values.append((f'random{i}',np.interp(grid,np.linspace(0,1,6),rng.uniform(.05,.95,6))))
    return values


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--case',choices=['base','xian'],required=True)
    parser.add_argument('--objective',choices=['time','infections','cost'],required=True)
    parser.add_argument('--n',type=int,default=20)
    parser.add_argument('--seed-limit',type=int,default=8)
    parser.add_argument('--warm',nargs='*',default=[])
    parser.add_argument('--verbose',action='store_true')
    parser.add_argument('--infection-scale',type=float,default=1.)
    args=parser.parse_args()
    problem=Problem(args.case,args.objective,args.n,args.verbose,args.infection_scale)
    if args.warm:
        for i,path in enumerate(args.warm):
            data=json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
            problem.solve(problem.initial(data['lambda_values'],data['duration']),f'warm{i}')
    else:
        for label,values in seeds(args.case,args.n)[:args.seed_limit]:
            problem.solve(problem.initial(values),label)


if __name__=='__main__':
    main()
