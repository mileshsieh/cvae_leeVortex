import os,sys,glob
import time
import numpy as np
import multiprocessing
from scipy.signal import gaussian
from scipy.ndimage import convolve1d

def conv_SFC_Field(npyfile,hr):
  c=npyfile.split('/')[-1].split('.')[1]
  v=npyfile.split('/')[-1].split('.')[0]
  npts=hr*6+1
  wgt=gaussian(npts,hr)
  wgt=wgt/wgt.sum()

  sfcData=np.load(npyfile)
  final=convolve1d(sfcData,wgt,axis=0,mode='constant',cval=0.0)
  np.save(f'../data/conv_dataset/{v}.{c}.conv.{hr}hr.npy',final)
  return c,hr

def saveCaseList():
    caseList=sorted([a.split('/')[-1].split('.')[0] for a in glob.glob('../data/ae_data/*.conv.1hr.npy')])
    with open('../data/caseList_conv.txt','w') as outF:
      for c in caseList:
        print(c,file=outF)

if __name__ == "__main__":
  nProc=32
  pool=multiprocessing.Pool(nProc)
  #for all the runs
  sfcCaseList=[f.split('/')[-1].split('.')[1] for f in glob.glob('../data/input/u_data*.npy')]
  #caseList=['tpe_20080715_at006']

  #skip calcualted cases
  convCaseList=[a.split('/')[-1].split('.')[1] for a in glob.glob('../data/conv_dataset/*conv.3hr.npy')]
  #convCaseList=[]

  tasks=[]
  ncase=0
  for caseName in sfcCaseList:
    if caseName in convCaseList:
      print('skip case:',caseName)
      continue
    else:
      print('convolve case:',caseName)
      ncase=ncase+1
      dataDir='../data/input/'
      #for hr in [1,2,3,6]:
      for hr in [3,6,12,24]:
        tasks.append((f'{dataDir}u_data.{caseName}.npy',hr))
        tasks.append((f'{dataDir}v_data.{caseName}.npy',hr))
        tasks.append((f'{dataDir}lwp_data.{caseName}.npy',hr))

  tStart=time.time()
  print('Calculating using %d processes...'%nProc)
  results=[pool.apply_async(conv_SFC_Field,t) for t in tasks]
  for result in results:
    rc,rhr=result.get()
    #print(f"Result: got {rc} with {rhr} hour convolued")
  tEnd=time.time()
  print('Calculating %d cases using %d processes...It costed %f sec'%(ncase,nProc,tEnd-tStart))
  saveCaseList()
 
