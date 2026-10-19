import numpy as np, json, sys
from multiprocessing import Pool
from core import *
def rA_closed(b): return 16/(b+np.sqrt(b*b-8*b+8))**2
def Uc_closed(b):
    r=rA_closed(b); return float(Us_branch(np.array([2.0]),b,r)[0])
def job(args):
    b,r=args
    Ug,_=Uglob(r,b)
    Umax=max(Ug*1.25,4.0)
    _,_,J=locate_jumps(b,r,Umax,n=6000)
    return dict(b=b,r=r,Uglob=Ug,jumps=[(j['U'],j['x_left'],j['x_right']) for j in J])
if __name__=="__main__":
    bs=[0.02,0.1,0.2,0.3,0.4,0.5,0.5755854,0.6,0.7,0.8,0.8321053,0.9,0.95,0.98]
    tasks=[]
    for b in bs:
        ra,rh=rA_closed(b),rhat(b)
        rs=sorted(set(list(np.geomspace(0.05,300,90))+list(np.linspace(ra*0.98,rh*1.02,24))+[ra*0.999,ra*1.001,rh*0.999,rh*1.001]))
        tasks+= [(b,float(r)) for r in rs]
    with Pool(8) as p: res=p.map(job,tasks,chunksize=8)
    bad=[]
    for o in res:
        b,r=o['b'],o['r']; ra,rh=rA_closed(b),rhat(b); n=len(o['jumps'])
        if r<=ra*0.9999:
            ok = n==0
        elif r<rh*0.9999:
            ok = n==1 and Uc_closed(b)-1e-3<=o['jumps'][0][0]<=Usw(b)+1e-9
        elif r>rh*1.0001:
            ok = n==1 and abs(o['jumps'][0][0]-o['Uglob'])<1e-6*o['Uglob'] and abs(o['jumps'][0][2]-1)<1e-9
        else: ok = n<=1
        if not ok: bad.append(o)
    print("tasks:",len(res)," mismatches:",len(bad))
    for o in bad[:15]: print(o)
    # 尖点数据
    for b in [0.8321053,0.5755854]:
        print(f"b={b}: rA'={rA_closed(b):.6f}  U_c={Uc_closed(b):.6f}  rhat={rhat(b):.6f} rinf={rinf(b):.4f}")
    json.dump(res,open("scan_grid.json","w"))
