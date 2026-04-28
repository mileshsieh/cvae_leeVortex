import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import matplotlib.colors as mc
import matplotlib
from mpl_toolkits.axes_grid1 import AxesGrid
import matplotlib.ticker as ticker

def plotStreamLine(ax,topo,vardata,title,rtitle,ltitle):
    ny,nx=topo.shape
    xx,yy=np.meshgrid(np.arange(nx),np.arange(ny))
    ax.contour(topo,levels=[0.05,],colors=['k'])
    #ax.contour(topo,levels=[0.05,0.2],colors=['k'])
    ws=np.sqrt(vardata[0,:,:]**2+vardata[1,:,:]**2)
    #print(ws.min(),ws.max())
    strm=ax.streamplot(xx,yy,vardata[0,:,:],vardata[1,:,:],
            color=ws,cmap='YlGnBu',norm=mc.Normalize(vmin=0.0,vmax=7.0),linewidth=2,density=0.8,zorder=3,arrowsize=1.5)
    #ax.plot([xstart,xend,xend,xstart,xstart],[ystart,ystart,yend,yend,ystart],lw=2,ls='--')
    ax.contourf(topo,levels=[0.2,5.0],colors=['darkgreen'],zorder=5)
    ax.set_xlim(0,nx)
    ax.set_ylim(0,ny)
    ax.xaxis.set_major_locator(ticker.NullLocator())
    ax.yaxis.set_major_locator(ticker.NullLocator())
    ax.set_title(rtitle,fontsize=10,loc='right')
    ax.set_title(ltitle,fontsize=10,loc='left')
    ax.set_title(title,fontsize=18,loc='center')
    return strm

if __name__=='__main__':
    ys=103
    ye=423
    xs=155
    xe=315
    ts=24
    te=ts+48

    cases=['ish20070409s_chem','ish20111227s_chem','ish20161001s_chem',\
               'ish20101129s_chem','ish20110430s_chem','ish20100323s_chem']
    dataList=[]
    for c in cases:
        dataList.append(np.array([np.load('../data/%s_data.%s.npy'%(var,c)) for var in ['u','v']]))
    sfcWind=np.array(dataList)
    step=15
    topo=np.load('../data/tw_s_topo.npy')
    lon=np.load('../data/tw_s_lat.npy')
    lat=np.load('../data/tw_s_lat.npy')
    print(lon.shape,lat.shape,topo.shape,sfcWind.shape)

    x=np.arange(lon.shape[0])
    y=np.arange(lat.shape[0])
    plt.close()
    xx,yy=np.meshgrid(x,y)
    step=10
    plt.quiver(xx[::step,::step],yy[::step,::step],sfcWind[0,0,20,::step,::step],sfcWind[0,1,20,::step,::step])
    plt.contour(x,y,topo,levels=[0.5,])
    plt.plot([xs,xe,xe,xs,xs],[ys,ys,ye,ye,ys],'r-')
    '''
    nsample=len(cases)
    plt.close()
    #fig=plt.figure(figsize=(20,16),layout='constrained')
    fig=plt.figure(figsize=(20,12))
    grid=AxesGrid(fig,111,nrows_ncols=(3,nsample),axes_pad=(0.1,0.3),share_all=True)

    for irow,tt in enumerate([20,40,60]):
        for icol,c in enumerate(cases):
            strm2=plotStreamLine(grid[irow*nsample+icol],topo,sfcWind[icol,:,tt,:,:],c,'','')
     
    '''
