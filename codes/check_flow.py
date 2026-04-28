import matplotlib.colors as mc
from matplotlib import pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
from mpl_toolkits.axes_grid1 import AxesGrid
import matplotlib.ticker as ticker
import matplotlib
matplotlib.rc('xtick',labelsize=20)
matplotlib.rc('ytick',labelsize=20)

def plotStreamLine(ax,topo,vardata,title,rtitle,ltitle,step=10):
    ny,nx=topo.shape
    ptopo=np.where(topo>0,topo,np.nan)
    xx,yy=np.meshgrid(np.arange(nx),np.arange(ny))
    ax.contour(topo,levels=[0.05,],colors=['k'])
    ax.contourf(ptopo,levels=np.linspace(0,4,9),cmap='Greens')
    #ax.contour(topo,levels=[0.05,0.2],colors=['k'])
    ws=np.sqrt(vardata[0,:,:]**2+vardata[1,:,:]**2)
    #print(ws.min(),ws.max())
    norm = plt.Normalize(vmin=0.0, vmax=8.0)
    #strm=ax.streamplot(xx,yy,vardata[0,:,:],vardata[1,:,:],
    #        color=ws,cmap='YlGnBu',norm=mc.Normalize(vmin=0.0,vmax=7.0),linewidth=2,density=0.8,zorder=3,arrowsize=1.5)
    q1=ax.quiver(xx[::step,::step],yy[::step,::step],vardata[0,::step,::step],vardata[1,::step,::step],\
                 ws[::step,::step],cmap='jet_r',norm=norm,\
                 scale=150,scale_units='width',angles='xy',zorder=4,color='k')
    #ax.plot([xstart,xend,xend,xstart,xstart],[ystart,ystart,yend,yend,ystart],lw=2,ls='--')
    #ax.contourf(topo,levels=[0.2,5.0],colors=['darkgreen'],zorder=5)
    ax.set_xlim(100,280)
    ax.set_ylim(20,250)
    ax.xaxis.set_major_locator(ticker.NullLocator())
    ax.yaxis.set_major_locator(ticker.NullLocator())
    ax.set_title(rtitle,fontsize=10,loc='right')
    ax.set_title(ltitle,fontsize=10,loc='left')
    ax.set_title(title,fontsize=18,loc='center')
    #return strm
    return q1

ys=135
ye=451
xs=20
xe=336
ts=6
te=ts+72

if __name__=='__main__':
  dd='20080328'
  cname={'HW24':f'ish{dd}s_chem','SND':f'ish_{dd}_snd','ERA5':f'ish_{dd}_era5'}
  mList=cname.keys()
  data={}
  for m in mList:
      data[m]=np.array([np.load(f'../data/u_data.{cname[m]}.npy')[:,ys:ye,xs:xe],\
              np.load(f'../data/v_data.{cname[m]}.npy')[:,ys:ye,xs:xe]])

  topo=np.load(f'../data/topo_s.npy')[ys:ye,xs:xe]
  lon=np.load(f'../data/lon_s.npy')[xs:xe]
  lat=np.load(f'../data/lat_s.npy')[ys:ye]
  dt=20 #min
  stime=np.datetime64('%s-%s-%s 06:00:00'%(dd[:4],dd[4:6],dd[6:]))


  nmodel=len(mList)
  nsample=1
  for tt in range(ts,te):
  #for tt in [24,]:
    a=stime+np.timedelta64(dt*tt,'m')
    hhmm=pd.to_datetime(str(a)).strftime('%H:%M')
    print(hhmm)

    plt.close()
    #fig=plt.figure(figsize=(20,16),layout='constrained')
    fig=plt.figure(figsize=(20,8))
    #grid=AxesGrid(fig,111,nrows_ncols=(nsample,nmodel),axes_pad=(0.1,0.3),share_all=True)

    for icol,m in enumerate(mList):
      print(m)
      #strm2=plotStreamLine(grid[icol],topo,data[m][:,tt,:,:],m,'','')
      #q1=plotStreamLine(grid[icol],topo,data[m][:,tt,:,:],m,'','')
      ax=plt.subplot(1,3,icol+1)
      q1=plotStreamLine(ax,topo,data[m][:,tt,:,:],m,'','')

    plt.tight_layout()
    fig.subplots_adjust(right=0.9,top=0.8)
    ax_cb = fig.add_axes([0.92, 0.04, 0.03, 0.70])
    #cbar=plt.colorbar(strm2.lines,cax=ax_cb,extend='max')
    cbar=plt.colorbar(q1,cax=ax_cb,extend='max')
    cbar.set_label('Wind Speed (m/s)',fontsize=20)
    qk=plt.quiverkey(q1,0.8,0.95, 10, '10 m/s', labelpos='E',coordinates='figure',fontproperties={'size':30},zorder=10)
    plt.suptitle(f'{dd} [{hhmm}]',fontsize=35)
    plt.savefig(f'../figures/check_{tt:02}.png')

