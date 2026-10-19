from core import *
import time
for name,b in [("base",0.8321053),("xian",0.5755854)]:
    ra,ua=rA(b)
    print(f"[{name}] b={b} Usw={Usw(b):.6f} rA'={ra:.6f}(u={ua:.4f}) rhat={rhat(b):.6f} rloc={rloc(b):.6f} rinf={rinf(b):.6f}")
    for r in [1.0, 2.0, 3.0, ra+0.01, 0.5*(ra+rhat(b)), rhat(b)-1e-3, rhat(b)+1e-3, rhat(b)+0.02, 3.3, 3.6, 4.0, 6.0, 10.0, 13.0, 30.0, 100.0]:
        Ug,_ = Uglob(r,b)
        Umax=max(Ug*1.3, 5.0)
        t=time.time(); _,_,J=locate_jumps(b,r,Umax,n=3000)
        js="; ".join(f"U={j['U']:.5f} x:{j['x_left']:.4f}->{j['x_right']:.4f}" for j in J)
        print(f"  r={r:9.5f} Uglob={Ug:.5f}  jumps({len(J)}): {js}   [{time.time()-t:.1f}s]")
