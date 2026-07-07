#!/home/mileshsieh/anaconda3/tobac/bin/python
import matplotlib
import numpy as np
import pandas as pd
import datetime,matplotlib
import sys,os,glob,time
import vvmDataUtil_s as vvm
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

#for plotting
pltCfg={'pAbd':['Pseudo Albedo[case=%s Local Time=%s]','Pseudo Albedo',np.linspace(0.0,1.0,51,endpoint=True)],
        'CBH':['Cloud Base Height Above Ground','Cloud Base Height(m)',np.linspace(0.0,7500.0,101,endpoint=True)],
        'CTH':['Cloud Top Height Above Ground','Cloud Top Height(m)',np.linspace(0.0,7500.0,101,endpoint=True)],
        'PBLH':['PBL Height Above Ground','PBL Height(m)',np.linspace(0.0,2500.0,101,endpoint=True),'jet'],
        'tr01':['Tracer01 Con. on the Ground','Tracer Con.(a.u.)',np.linspace(0.0,0.1,101,endpoint=True),'hot_r'],
        }


#get universal setting
vvmDir='/data2/VVM/taiwanvvm_s_winter_era5'
case='ish_20191215'
s=True
dataDir=vvmDir+'/%s'%case
#case='exp'
nt=vvm.getNT(dataDir)
(nz,ny,nx),zc=vvm.getDimension(case,dataDir)
topo,lon,lat=vvm.getTOPO(dataDir,s)
topo_idx,uti,vti=vvm.getTOPO_idx(dataDir,s)

ztop=4000
idx_top=np.where(zc>ztop)[0][0]
zF=2500
idxF=np.where(zc>zF)[0][0]

#read the caseList and the corresponding directory
a=pd.read_csv('../data/selected_16_cases_WS4-10_WD30-180_recent5yr.csv',header=0)

caseList=[]
for c in a.caseName:
    caseList.append(c)

def plotTR(tr):
    plt.close()
    plt.contourf(tr,cmap='jet',levels=np.linspace(0,5,51),extend='max')
    plt.contourf(topo_idx,levels=np.linspace(3,14,12),cmap='Greys')
    plt.contour(topo,levels=[1.5,],colors=['k',])
    return

nt=48
idxDict={}
#idx=2+src*2+chem
#idxO3=1
#idxTotal=0
chem_idx=0
var='tr%02d'%(chem_idx+1)
trList=[]

#for west plain sampling
xstart=0
xend=265
ystart=220
yend=360

y_slice, x_slice = slice(150, 438), slice(33, 321)

#for tt in range(nt):
for tt in [45,]:
  plt.close()
  fig, axes = plt.subplots(ncols=4,nrows=4,constrained_layout=False,figsize=(8,5))
  for i,ax in enumerate(axes.ravel()):
  #for case in caseList[:1]:
    #tr=vvm.getVarSfcOnTime(caseDirList[i],caseList[i],var,topo_idx,tt)
    ax.contourf(topo_idx,levels=np.linspace(3,14,12),cmap='Greys')
    tr=vvm.getVarSfcOnTime(vvmDir+'/%s'%caseList[i],caseList[i],'NO',topo_idx,tt)+vvm.getVarSfcOnTime(vvmDir+'/%s'%caseList[i],caseList[i],'NO2',topo_idx,tt)
    tr[tr<0.01]=np.nan
    c1=ax.contourf(tr,cmap='jet',levels=np.linspace(0,1,21),extend='max')
    #c1=ax.contour(tr,levels=[0.1],colors=['r'])
    #for polluted areas
    ax.contour(topo_idx,levels=[1.5,],colors=['k',])

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(170,340)
    ax.set_ylim(150,370)
    #plt.show()
    print(caseList[i],tt,np.percentile(tr[~np.isnan(tr)],90),np.percentile(tr[~np.isnan(tr)],50))

  trAll=np.array(trList)
  plt.tight_layout()
  # color bar
  fig.subplots_adjust(right=0.85)

  # color bar of topo
  #cax_topo=fig.add_axes([0.77, 0.1, 0.03, 0.8])
  #cbar_topo=plt.colorbar(cs_topo, cax=cax_topo, orientation='vertical')
  #cbar_topo.set_label('elevation(m)',fontsize=40)

  # color bar of var
  cax_var=fig.add_axes([0.88, 0.1, 0.03, 0.8])
  cbar_var=plt.colorbar(c1, cax=cax_var,ticks=np.linspace(0,1,21),orientation='vertical')
  cbar_var.set_label('NOx (ppb)',fontsize=40)
  
  plt.savefig('tr30/NOx.%d.png'%tt,dpi=300)


