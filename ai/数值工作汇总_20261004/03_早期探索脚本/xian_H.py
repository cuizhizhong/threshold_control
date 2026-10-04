import numpy as np
from scipy.integrate import solve_ivp
N=13163000.0; beta=0.1498; gam=0.2953; dq=0.3531; c0=12.8872; q0=0.3230
I0=1.00663e-3; S0=N-I0
Sc=gam*N/(beta*c0*(1-q0))
def run(theta,L=8.0,verbose=False):
    eta=theta*N
    def rhs(t,y,mode):
        S,I,Sq,Iq,H1,H2=y
        if mode=='base': c,q=c0,q0
        else: c=c0; q=1-gam*N/(beta*c0*S)
        inc=beta*c*S*I/N
        return [-(c*(beta+(1-beta)*q))*S*I/N, inc*(1-q)-gam*I, (1-beta)*c*q*S*I/N, inc*q-dq*Iq,
                gam*I-H1/L, gam*I+dq*Iq-H2/L]
    ev1=lambda t,y,m: y[1]-eta; ev1.terminal=True; ev1.direction=1
    y0=[S0,I0,0,0,0,0]
    s1=solve_ivp(rhs,[0,500],y0,args=('base',),events=ev1,rtol=1e-10,atol=1e-8,max_step=0.5)
    t1=s1.t_events[0][0]; y1=s1.y_events[0][0]; y1[1]=eta
    ev2=lambda t,y,m: y[0]-Sc; ev2.terminal=True; ev2.direction=-1
    s2=solve_ivp(rhs,[t1,t1+1e5],y1,args=('plat',),events=ev2,rtol=1e-10,atol=1e-8,max_step=0.5)
    t2=s2.t_events[0][0]; y2=s2.y_events[0][0]
    s3=solve_ivp(rhs,[t2,t2+400],y2,args=('base',),rtol=1e-10,atol=1e-8,max_step=0.5)
    H1=np.concatenate([s1.y[4],s2.y[4],s3.y[4]]); H2=np.concatenate([s1.y[5],s2.y[5],s3.y[5]])
    C=gam*L*eta
    qmax=1-gam*N/(beta*c0*y1[0])
    return dict(t1=t1,t2=t2,qmax=qmax,H1=H1.max()/C,H2=H2.max()/C, H2abs=H2.max()/(gam*L))
for L in [5,8,13]:
    r=run(0.002,L)
    print(L, {k:round(v,4) for k,v in r.items()})
# find theta such that two-channel peak (in units of gam*L) equals 0.002N (central calibrated capacity)
from scipy.optimize import brentq
for L in [5,8,13]:
    f=lambda th: run(th,L)['H2abs']-0.002*N
    th=brentq(f,1e-4,2e-3,xtol=1e-7)
    print('L',L,'theta_two_channel',th)

print('---- extra')
def metrics(theta,L=8.0):
    eta=theta*N
    def rhs(t,y,mode):
        S,I,Sq,Iq,H1,H2,Cum=y
        if mode=='base': c,q=c0,q0
        else: c=c0; q=1-gam*N/(beta*c0*S)
        inc=beta*c*S*I/N
        return [-(c*(beta+(1-beta)*q))*S*I/N, inc*(1-q)-gam*I, (1-beta)*c*q*S*I/N, inc*q-dq*Iq, gam*I-H1/L, gam*I+dq*Iq-H2/L, inc]
    ev1=lambda t,y,m: y[1]-eta; ev1.terminal=True; ev1.direction=1
    s1=solve_ivp(rhs,[0,500],[S0,I0,0,0,0,0,0],args=('base',),events=ev1,rtol=1e-10,atol=1e-8,max_step=0.5)
    t1=s1.t_events[0][0]; y1=s1.y_events[0][0]; y1[1]=eta
    ev2=lambda t,y,m: y[0]-Sc; ev2.terminal=True; ev2.direction=-1
    s2=solve_ivp(rhs,[t1,t1+1e5],y1,args=('plat',),events=ev2,rtol=1e-10,atol=1e-8,max_step=0.5)
    t2=s2.t_events[0][0]; y2=s2.y_events[0][0]
    s3=solve_ivp(rhs,[t2,t2+600],y2,args=('base',),rtol=1e-10,atol=1e-8,max_step=0.5)
    H2=np.concatenate([s1.y[5],s2.y[5],s3.y[5]])
    return dict(t1=t1,dt=t2-t1,qmax=1-gam*N/(beta*c0*y1[0]),cum=s3.y[6][-1],H1cap=gam*L*eta,H2peak=H2.max(),ratio=H2.max()/(gam*L*eta))
for th in [0.002,3.4e-4,2e-4,5e-4]:
    print(th,{k:float('%.4g'%v) for k,v in metrics(th).items()})
# uncontrolled
L=8.0
def rhs0(t,y):
    S,I,Sq,Iq,H1,H2=y; c,q=c0,q0; inc=beta*c*S*I/N
    return [-(c*(beta+(1-beta)*q))*S*I/N, inc*(1-q)-gam*I,(1-beta)*c*q*S*I/N, inc*q-dq*Iq, gam*I-H1/L, gam*I+dq*Iq-H2/L]
s=solve_ivp(rhs0,[0,800],[S0,I0,0,0,0,0],rtol=1e-10,atol=1e-8,max_step=0.5)
print('uncontrolled Imax/N',s.y[1].max()/N,'H1peak/(gL*0.002N)',s.y[4].max()/(gam*L*0.002*N),'H2peak/(gL*0.002N)',s.y[5].max()/(gam*L*0.002*N))
# calibration numbers
b=4.37e-5
for p in [0.0086,0.0172]:
    for Lx in [5,8,13]:
        print('p',p,'L',Lx,'theta',b/(p*gam*Lx))
print('implied p for theta=0.002,L=8:', b/(0.002*gam*8))
print('ICU beds Xi an at 4.37/1e5:', b*N, ' community-channel need at theta=0.002,p=.86%,L=8:', 0.0086*gam*8*0.002*N)
