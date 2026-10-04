import numpy as np
from scipy.integrate import quad, simpson
import joint_cost_optimal as M

P = dict(N=13163000, S0=13163000 - 1.00663e-3, I0=1.00663e-3, beta=0.1498, gamma=0.2953,
         dq=0.3531, c0=12.8872, q0=0.3230, eta=0.002*13163000)
try:
    Sc, Sbar, Sstar = M.basic_quantities(P)
except Exception as e:
    print("param key issue", e); raise
wc, wq = 1.0, 2.0
c0, q0 = P['c0'], P['q0']
# ---- TDINN ----
T = 45.27
uc = lambda t: (c0 - ((c0-3.4625)*np.exp(-(0.0463*t)**2)+3.4625))/c0
uq = lambda t: (((0.3230-0.9844)*np.exp(-(0.0452*t)**2)+0.9844) - q0)/(1-q0)
Jq_T = quad(lambda t: wc*uc(t)**2 + wq*uq(t)**2, 0, T)[0]
Jl_T = quad(lambda t: wc*uc(t) + wq*uq(t), 0, T)[0]
print(f"TDINN: quad J={Jq_T:.2f}, linear J={Jl_T:.2f}, uc(T)={uc(T):.3f}, uq(T)={uq(T):.3f}")
# ---- plateau policies, cost densities in s ----
sbar, sstar = Sbar/Sc, Sstar/Sc
pref = P['N']/(P['eta']*c0)
s = np.linspace(1, sstar, 20001)
def J_of(x, pw):
    dens = (wc*(1-x)**pw + wq*np.abs(1-1/(x*s))**pw)/(x*s - sbar)
    return pref*simpson(dens, x=s), pref*simpson(1/(x*s-sbar), x=s)
print(f"sbar={sbar:.4f}, s*={sstar:.4f}")
for name, x in [('q_only', np.ones_like(s)), ('c_only', 1/s)]:
    for pw in (1, 2):
        J, dT = J_of(x, pw)
        print(f"{name} p={pw}: J={J:.2f}, dT={dT:.2f}")
# quadratic optimum
sol = M.solve_allocation(P, wc, wq, policy='optimal')
print(f"joint optimal p=2: J={sol['J']:.2f}, dT={sol['dT']:.2f}, s_sw={sol['s_sw']:.3f}")
# linear optimum: bang rule, q-only iff s > sbar + r(1-sbar)
r = wq/wc
s_lin = sbar + r*(1-sbar)
x_lin = np.where(s > s_lin, 1.0, 1/s)
J, dT = J_of(x_lin, 1)
print(f"joint optimal p=1: switch s_lin={s_lin:.4f}, J={J:.2f}, dT={dT:.2f}")
# brute-force check of bang rule at several s
for si in [1.2, s_lin-0.05, s_lin+0.05, 2.5, sstar*0.9]:
    xs = np.linspace(1/si, 1, 200001)
    f = (wc*(1-xs) + wq*(1-1/(xs*si)))/(xs*si - sbar)
    print(f"  s={si:.3f}: argmin x={xs[np.argmin(f)]:.4f} (1/s={1/si:.4f})")
