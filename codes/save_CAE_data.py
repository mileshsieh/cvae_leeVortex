#!/home/mileshsieh/anaconda3/bin/python
import matplotlib
import numpy as np
import pandas as pd
import datetime,matplotlib
import sys,os,glob,time
import vvmDataUtil_s as vvm
import multiprocessing

def calcAll(tt,case,dataDir,topo_idx,uti,vti,s):
  print("\tCalculating timestep %03d"%tt)
  usfc,vsfc=vvm.getSfcWind_intp(dataDir,case,topo_idx,uti,vti,tt,s)
  lwp=vvm.calcLWP(dataDir,case,tt,s,5000)
  return tt,usfc,vsfc,lwp

if __name__ == "__main__":
  #vvmDir='/data/mileshsieh/TaiwanVVM_2km'
  baseDir={'era5':'/data2/VVM/taiwanvvm_s_winter_era5','snd':'/data2/VVM/taiwanvvm_s_winter'}
  ini='era5'
  vvmDir=baseDir[ini]
  nProc=32

  #get universal setting
  case='ish_20080328'
  s=True
  dataDir=vvm.vvmDir+'/%s'%case
  nt=vvm.getNT(dataDir)
  (nz,ny,nx),zc=vvm.getDimension(case,dataDir)
  topo,lon,lat=vvm.getTOPO(dataDir,s)
  topo_idx,uti,vti=vvm.getTOPO_idx(dataDir,s)
  #np.save('../data/topo_s.npy',topo)
  #np.save('../data/lon_s.npy',lon)
  #np.save('../data/lat_s.npy',lat)

  #put all data into training data
  caseList=[]
  #initialize data stroage of all simulations
  dirList=glob.glob(vvmDir+'/ish_*')
  for d in dirList:
    case=d.split('/')[-1]
    dataDir=vvm.vvmDir+'/%s'%case
    nt=vvm.getNT(dataDir)
    print(case,nt)
    if nt<145:
      continue
    else:
      caseList.append(case)
  print(len(caseList),nt)
  ncase=len(caseList)

  #skip calcualted cases
  sfcCaseList=[a.split('/')[-1].split('.')[1][:-5] for a in glob.glob('../data/input/u_data*.npy')]

  with open(f'../data/caseList.{ncase}.txt', 'w') as file:
    file.write('\n'.join(sorted(caseList)))

  pool=multiprocessing.Pool(nProc)

  for case in caseList:
  #for case in ['ish_20080328']:
    if case in sfcCaseList:
        print(f'skip calculated case {case}')
        continue
    print('case=%s'%case)
    tStart=time.time()
    print('Calculating %d timesteps using %d processes...'%(nt,nProc))
    dataDir=f'{vvmDir}/{case}'
    #put the arguments into tasks list
    tasks=[]
    for tt in range(nt):
      tasks.append((tt,case,dataDir,topo_idx,uti,vti,s))

    results=[pool.apply_async(calcAll,t) for t in tasks]
    u3D=np.zeros((nt,ny,nx))
    v3D=np.zeros((nt,ny,nx))
    lwp3D=np.zeros((nt,ny,nx))

    for result in results:
      rt,u,v,lwp=result.get()
      u3D[rt,:,:]=u
      v3D[rt,:,:]=v
      lwp3D[rt,:,:]=lwp
      print("Result: got timestep %03d "%rt)

    np.save(f'../data/input/u_data.{case}_{ini}.npy',np.array(u3D,dtype=np.float32))
    np.save(f'../data/input/v_data.{case}_{ini}.npy',np.array(v3D,dtype=np.float32))
    np.save(f'../data/input/lwp_data.{case}_{ini}.npy',np.array(lwp3D,dtype=np.float32))
    tEnd=time.time()
    print('Calculating %d timesteps using %d processes...It costed %f sec'%(nt,nProc,tEnd-tStart))
