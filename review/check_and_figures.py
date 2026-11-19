import numpy as np
rho,mu,U,L=1.225,1.7894e-5,36,0.46
nu=mu/rho
print("Re_L",U*L/nu, "q",0.5*rho*U**2, "Re_s",U*0.23/nu, "d_flat",0.37*0.23*(U*0.23/nu)**-0.2)
print("infl",0.01*(1.2**25-1)/0.2, "dU/dy wall (Cf=3e-3)",3e-3*0.5*rho*U**2/mu)
N=np.array([0.529,1.150,2.528])*1e6; h=np.array([10.41,8.04,6.18])
print("h ratios",h[0]/h[1],h[1]/h[2],"N-based",(N[1]/N[0])**(1/3),(N[2]/N[1])**(1/3),"V",N*(h*1e-3)**3)
def gci(f3,f2,f1,r21,r32):
    e21,e32=f2-f1,f3-f2; s=np.sign(e32/e21); p=1.0
    for _ in range(200):
        q=np.log((r21**p-s)/(r32**p-s)); p=abs(np.log(abs(e32/e21))+q)/np.log(r21)
    ext=(r21**p*f1-f2)/(r21**p-1); ea=abs((f1-f2)/f1)
    return p,ext,1.25*ea/(r21**p-1)*100, abs((ext-f1)/ext)*100
r21,r32=h[1]/h[2],h[0]/h[1]
for n,f in [("Cd",[0.063731,0.062529,0.061649]),("Uc",[33.195,29.546,28.304]),("Uw",[28.569,27.162,25.600])]:
    print(n,gci(*f,r21,r32), "med->fine %",(f[1]-f[2])/f[2]*100)
print("Gamma ratios",160.4/18.2,144.7/14.1,305.1/32.3, 29.3+19.4)
print("Ue",37.4/36, "sqrt2 d99",np.sqrt(2)*25.8, "bisector 27.3/sqrt2",27.3/np.sqrt(2))
print("Cf ratios",1.05/2.16,2.86/2.16, "crossflow",3.5/36,0.07/36,0.46/36)
print("p_tot overshoot",837/819)
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
B,O,G="#2c6fbb","#e8692e","#1e9e6a"; INK="#333"; MUT="#888"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"axes.edgecolor":MUT,"axes.labelcolor":INK,
 "xtick.color":INK,"ytick.color":INK,"axes.spines.top":False,"axes.spines.right":False,"axes.grid":True,
 "grid.color":"#e6e6e6","grid.linewidth":0.6,"lines.linewidth":2})
out="/home/user/BTP/review/figures/"
h=np.array([10.41,8.04,6.18])
# ---- Fig 1: grid convergence
fig,ax=plt.subplots(1,3,figsize=(9.5,3.0))
data=[("Drag coefficient $C_d$",[0.063731,0.062529,0.061649],0.059424,1.27,B,"{:.4f}"),
      ("Corner speed $U_{corner}$ (m/s)",[33.195,29.546,28.304],27.692,4.21,O,"{:.2f}"),
      ("Wake speed $U_{wake}$ (m/s)",[28.569,27.162,25.600],None,None,G,"{:.2f}")]
for a,(t,f,ext,p,c,fmt) in zip(ax,data):
    a.plot(h,f,"-o",color=c,ms=7,mec="white",mew=1.5)
    for hi,fi,n in zip(h,f,["C","M","F"]):
        a.annotate(n+": "+fmt.format(fi),(hi,fi),textcoords="offset points",xytext=(6,4),fontsize=8,color=INK)
    if ext:
        hh=np.linspace(0,h[-1],30); C=(f[2]-ext)/h[2]**p
        a.plot(hh,ext+C*hh**p,"--",color=c,lw=1.2)
        a.plot([0],[ext],"s",color=c,ms=7,mec="white",mew=1.5)
        a.annotate("Richardson\nextrap. "+fmt.format(ext)+f"\n(p = {p:.2f})",(0,ext),xytext=(4,6),textcoords="offset points",fontsize=8,color=INK)
    else:
        a.text(0.04,0.62,"No asymptotic convergence:\ndifferences grow\n1.41 → 1.56 m/s",transform=a.transAxes,fontsize=8,color=INK)
    a.set_xlim(-0.5,12); a.set_xlabel("Effective cell size h = (V/N)$^{1/3}$ (mm)"); a.set_title(t,fontsize=9,color=INK,loc="left")
fig.tight_layout(); fig.savefig(out+"grid_convergence.png",dpi=250); plt.close()
# ---- Fig 2: circulation decay + asymmetry
s=np.array([30,130,230,430]); gp=np.array([160.4,53.0,29.0,18.2]); gm=np.array([144.7,28.6,19.4,14.1])
fig,ax=plt.subplots(1,2,figsize=(8.5,3.1))
a=ax[0]
for y,c,lab,mk in [(gp+gm,INK,r"$\Gamma^+ + |\Gamma^-|$","o"),(gp,"#c0392b",r"$\Gamma^+$ (plate-side cell)","^"),(gm,"#2c6fbb",r"$|\Gamma^-|$ (floor-side cell)","v")]:
    a.plot(s,y,"-"+mk,color=c,ms=7,mec="white",mew=1.2,label=lab)
a.set_yscale("log"); a.set_xlabel("Distance from leading edge s (mm)"); a.set_ylabel(r"Circulation ($10^{-3}$ m$^2$/s)")
a.set_title("(a) Decay of corner streamwise circulation",loc="left",fontsize=9); a.legend(fontsize=8,frameon=False)
a.set_xticks(s)
a=ax[1]; r=gp/gm
a.bar(s,r,width=45,color="#9aa7b4",edgecolor="white",zorder=3); a.grid(axis="x",visible=False)
for si,ri in zip(s,r): a.text(si,ri+0.03,f"{ri:.2f}",ha="center",fontsize=8,color=INK)
a.axhline(1,color=MUT,lw=1,ls="--"); a.text(440,1.02,"equal strength",fontsize=7.5,color=MUT,ha="right",va="bottom")
a.set_xticks(s); a.set_xlabel("Distance from leading edge s (mm)"); a.set_ylabel(r"$\Gamma^+/|\Gamma^-|$"); a.set_ylim(0,2.1)
a.set_title("(b) Asymmetry of the corner pair",loc="left",fontsize=9)
fig.tight_layout(); fig.savefig(out+"circulation_decay.png",dpi=250); plt.close()
print("ok")
