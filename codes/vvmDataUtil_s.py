import matplotlib
import numpy as np
import pandas as pd
import datetime,matplotlib
import xarray as xr
import sys,os,glob
from matplotlib import pyplot as plt
Cp=1004.0
g=9.8
Lv=2264760.0
R=8.314
#vvmDir='/home/mileshsieh/VVM/DATA'
vvmDir='/data2/VVM/taiwanvvm_s_winter_era5'

varFn={'qc':'%s.L.Thermodynamic-%06d.nc',
       'qr':'%s.L.Thermodynamic-%06d.nc',
       'qv':'%s.L.Thermodynamic-%06d.nc',
       'qi':'%s.L.Thermodynamic-%06d.nc',
       'th':'%s.L.Thermodynamic-%06d.nc',
       'qrim':'%s.L.Thermodynamic-%06d.nc',
       'ni':'%s.L.Thermodynamic-%06d.nc',
       'u':'%s.L.Dynamic-%06d.nc',
       'v':'%s.L.Dynamic-%06d.nc',
       'w':'%s.L.Dynamic-%06d.nc',
       'zeta':'%s.L.Dynamic-%06d.nc',
       'tr01':'%s.L.Tracer-%06d.nc',
       'tr02':'%s.L.Tracer-%06d.nc',
       'tr03':'%s.L.Tracer-%06d.nc',
       'tr04':'%s.L.Tracer-%06d.nc',
       'tr05':'%s.L.Tracer-%06d.nc',
       'tr06':'%s.L.Tracer-%06d.nc',
       'tr07':'%s.L.Tracer-%06d.nc',
       'tr08':'%s.L.Tracer-%06d.nc',
       'tr09':'%s.L.Tracer-%06d.nc',
       'tr10':'%s.L.Tracer-%06d.nc',
       'tr11':'%s.L.Tracer-%06d.nc',
       'tr12':'%s.L.Tracer-%06d.nc',
       'tr13':'%s.L.Tracer-%06d.nc',
       'tr14':'%s.L.Tracer-%06d.nc',
       'tr15':'%s.L.Tracer-%06d.nc',
       'tr16':'%s.L.Tracer-%06d.nc',
       'tr17':'%s.L.Tracer-%06d.nc',
       'tr18':'%s.L.Tracer-%06d.nc',
        }

def getData(dataDir,var,case,tt,s=False):
  if var in varFn.keys():
  #if var in ['qc','qv','qr','qi','th','qrim','ni','u','v','w','tr01','tr02','tr03','tr04','tr05','tr06']:
    varData=xr.open_dataset(dataDir+'/archive/'+varFn[var]%(case,tt))[var].values.squeeze()
  else:
    return None
  #return varData.filled(np.nan)
  if s:
    return np.roll(np.roll(varData,128,axis=-1),128,axis=-2)
  else:
    return varData

def getZC(dataDir,case):
  #nc_f=dataDir+'/archive/%s.L.Dynamic-000000.nc'%case
  zc=xr.open_dataset(dataDir+'/archive/%s.L.Thermodynamic-000000.nc'%case).zc.values.squeeze()
  return zc

def getTOPO(dataDir,enlarge=False):
  ds=xr.open_dataset(dataDir+'/TOPO.nc')
  topo=ds['height'].values.squeeze()
  lat=ds['lat'].values.squeeze()
  lon=ds['lon'].values.squeeze()
  if enlarge:
    return np.roll(np.roll(topo,128,axis=0),128,axis=1),lon-(lon[128]-lon[0]),lat-(lat[128]-lat[0])
  else:
    return topo,lon,lat

def getTOPO_idx(dataDir,enlarge=False):
  ds=xr.open_dataset(dataDir+'/TOPO.nc')
  idxtopo=ds['topo'].values.squeeze().astype(int)

  ny,nx=idxtopo.shape
  idxutopo=np.array([np.maximum(idxtopo[j,:],np.roll(idxtopo[j,:],-1))for j in range(ny)])
  idxvtopo=np.array([np.maximum(idxtopo[:,i],np.roll(idxtopo[:,i],-1))for i in range(nx)]).T

  #return topo.filled(0.0),lon,lat
  if enlarge:
    return np.roll(np.roll(idxtopo,128,axis=0),128,axis=1),np.roll(np.roll(idxutopo,128,axis=0),128,axis=1),\
           np.roll(np.roll(idxvtopo,128,axis=0),128,axis=1)
  else:
    return idxtopo,idxutopo,idxvtopo

def getNT(dataDir):
  fList=glob.glob(dataDir+'/archive/*Thermodynamic*.nc')
  nt=len(fList)
  return nt

def getDimension(case,dataDir):
  ds=xr.open_dataset(dataDir+'/archive/%s.L.Thermodynamic-000000.nc'%case)
  zc=ds.zc.values.squeeze()
  varData=ds['qv'].values.squeeze()
  return varData.shape,zc

def getFort98Info(dataDir,case,var):
  #get corresponding header
  if var=='ZZ':
      hdr='K, ZZ(K),ZT(K),FNZ(K),FNT(K)'
      cols=['K', 'ZZ', 'ZT', 'FNZ', 'FNT']
  else:
      hdr='K, RHO(K),THBAR(K),PBAR(K),PIBAR(K),QVBAR(K)'
      cols=['K', 'RHO', 'THBAR', 'PBAR', 'PIBAR', 'QVBAR']

  with open(f"{dataDir}/fort.98", 'r') as f:
    lines = f.readlines()

  # Find the starting line
  start_line = None
  for i, line in enumerate(lines):
    if hdr in line:
      start_line = i + 2  # Skip header and separator line
      break
  #print(f"Data starts at line: {start_line}")
  # Read the data using pandas
  df = pd.read_csv(f"{dataDir}/fort.98",sep=r'\s+',skiprows=start_line,nrows=35,  # Read 35 levels
                   names=cols)
  rho=df[var].values
  #print(rho.shape)
  return rho

def calcLWP(dataDir,case,tt,s,ztop_m=5000):
    qcld=getData(dataDir,'qc',case,tt,s)+getData(dataDir,'qr',case,tt,s)
    zz=getFort98Info(dataDir,case,'ZZ')
    idx_zz_top=np.where(zz>=ztop_m)[0][0]
    dz=(zz[2:idx_zz_top]-zz[1:idx_zz_top-1]).reshape(-1,1,1)
    nlyr=dz.shape[0]
    rho=getFort98Info(dataDir,case,'RHO')[1:nlyr+1].reshape(-1,1,1)
    lwp=np.sum(qcld[1:nlyr+1,:,:]*rho*dz,axis=0)

    return lwp

def calcPseAbd(lwp):
  tau=0.19*np.power(lwp,5.0/6.0)*np.power(50.0,1.0/3.0)
  pseudoAlbedo=tau/(tau+6.8)
  return pseudoAlbedo

def getSfcWind_intp(dataDir,case,tp,utp,vtp,tt,s):
  topo=tp.copy()
  utopo=utp.copy()
  vtopo=vtp.copy()
  utopo[utopo<1.0]=1.0
  vtopo[vtopo<1.0]=1.0
  topo[topo<1.0]=1.0
  idx_topo=topo.astype(np.int)
  idx_utopo=utopo.astype(np.int)
  idx_vtopo=vtopo.astype(np.int)
  ny,nx=utopo.shape
  x2d,y2d=np.meshgrid(np.arange(nx),np.arange(ny))
  result=np.zeros((ny,nx))
  uData=getData(dataDir,'u',case,tt,s)
  for k in range(idx_utopo.max()+1):
    uData[k,:,:]=np.where(idx_utopo>k,np.nan,uData[k,:,:])
  uData=np.nanmean([uData,np.roll(uData,-1,axis=2)],axis=0)

  vData=getData(dataDir,'v',case,tt,s)
  for k in range(idx_vtopo.max()+1):
    vData[k,:,:]=np.where(idx_vtopo>k,np.nan,vData[k,:,:])
  vData=np.nanmean([vData,np.roll(vData,-1,axis=1)],axis=0)

  usfc=uData[idx_utopo,y2d,x2d]
  vsfc=vData[idx_vtopo,y2d,x2d]
  return usfc,vsfc

def calcThetaV(th,qv,zc):
  thetaV=th*(1+0.61*qv)
  return zc,thetaV
 
def getLCL(case,th,qv,zc):
  pbar=getFort98Info(dataDir,case,'PBAR')
  e=np.zeros(qv.shape)
  for i in range(zc.shape[0]):
      e[i,:,:]=qv[0,:,:]*pbar[i]/0.622
  print(e.mean(),e.max(),e.min())
  nz,ny,nx=th.shape
  for i in range(zc.shape[0]):
    #print(i, zc[i])
    th[i,:,:]=th[0,:,:]-9.8*(zc[i]-zc[0])/1000.0
  es=np.zeros(th.shape)
  th=th-273.15
  es=0.611*np.exp((17.3*th)/(th+237.3))*1000.0
  print(es.mean(),es.max(),es.min())
  del_e=e-es
  print(del_e.max(),del_e.min())
  cld_3D=np.where(del_e>0,1,0)
  cld_3D_flat=cld_3D.reshape((nz,ny*nx))
  print('cld3d_flat:',cld_3D_flat.shape,cld_3D_flat.max(),cld_3D_flat.min())
  LCL_idx=np.array([np.argmax(cld_3D_flat[:,k],axis=0) for k in range(cld_3D_flat.shape[1])])
  print('LCL_idx:',LCL_idx.shape,LCL_idx.max(),LCL_idx.min())
  LCL=zc[LCL_idx]
  LCL=np.reshape(np.where(np.sum(cld_3D_flat,axis=0)>0,LCL,np.nan),(ny,nx))
  print(LCL.shape,np.nanmean(LCL),np.nanmax(LCL),np.nanmin(LCL))
  return LCL


if __name__ == "__main__":
  for case in ['ish_20111117',]:
    s=True
    dataDir=vvmDir+'/%s'%case
    #case='exp'

    nt=getNT(dataDir)
    (nz,ny,nx),zc=getDimension(case,dataDir)
    topo,lon,lat=getTOPO(dataDir,s)
    topo_idx,uti,vti=getTOPO_idx(dataDir,s)
    print('caseName=%s'%case)
    print('Dimensions: nx=%d, ny=%d, nz=%d'%(nx,ny,nz))
    print('topo:',topo.min(),topo.max())
    print('lat:',lat.min(),lat.max())
    print('lon:',lon.min(),lon.max())
    #print('Puli at ',x,y,lon[x],lat[y],lonlat['Puli'][0],lonlat['Puli'][1],topo[y,x])
    np.save('../data/tw_s_lon.npy',lon)
    np.save('../data/tw_s_lat.npy',lat)
    np.save('../data/tw_s_topo.npy',topo_idx)

    u3D=getData(dataDir,'u',case,24,s)
    usfc,vsfc=getSfcWind_intp(dataDir,case,topo_idx,uti,vti,24,s)

    tt=24
    lwp=calcLWP(dataDir,case,tt,s,5000)
    '''
    xx=252
    yy=200
    rad=15
    plt.close()
    plt.subplot(211)
    plt.plot(topo_idx[yy,xx-rad:xx+rad]-1)
    plt.plot(uti[yy,xx-rad:xx+rad]-1,'r:')
    for ii in range(rad*2):
      u_raw=u3D[:15,yy,xx-rad+ii]
      u_raw=u_raw/u_raw.max()+ii
      plt.plot(u_raw,np.arange(15),'g--')
    plt.grid()
    plt.xlim(0,rad*2)
    plt.subplot(212)
    plt.plot(usfc[yy,xx-rad:xx+rad],'b-',label='interp')
    plt.plot(u3D[topo_idx[yy,xx-rad:xx+rad].astype(int),[yy]*(rad*2),np.arange(xx-rad,xx+rad)],'r-',label='naive')
    plt.xlim(0,rad*2)
    plt.legend()
    plt.grid()
   
    '''
    
    
