import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path
import vvmDataUtil_s as vvm
from matplotlib import pyplot as plt

# Read folder names from case.txt
#foldpath = '/home/hhlee/taiwanvvm_s_winter/'
#with open('/data/hhlee/case.txt', 'r') as f:
#    folders = [line.strip() for line in f if line.strip()]
#
#print(f"Found {len(folders)} folders to process\n")
foldpath = '/data2/VVM/taiwanvvm_s_winter_era5/'
folders=['ish_20111117',]

# Base directory path (adjust this to your actual base path)
base_path = Path(foldpath)  # Change this to your data directory

for folder in folders:
    folder_path = base_path / folder
    print(folder_path)
    # Look for NetCDF files in the folder
    try:
        if not folder_path.exists():
            print(f"⚠️  Folder not found: {folder}")
            continue

        with open(f"{folder_path}/fort.98", 'r') as f:
            lines = f.readlines()

        # Find the line where RHOZ starts
        rhoz_start = None
        for i, line in enumerate(lines):
            if 'K, RHOZ(K)' in line:
                rhoz_start = i + 2
                break

        # Read RHOZ data
        rhoz_df = pd.read_csv(f"{folder_path}/fort.98",
                          sep=r'\s+',
                          skiprows=rhoz_start,
                          nrows=34,
                          names=['K', 'RHOZ'],
                          engine='python')

        rho = rhoz_df['RHOZ'].values

        # Find NetCDF files (.nc extension) #ish_20190404.L.Thermodynamic-000144.nc
        nc_files = list(folder_path.glob('archive/*Thermodynamic*.nc'))

        if not nc_files:
            print(f"⚠️  No NetCDF files in: {folder}")
            continue

        # Process the first NetCDF file found (or adjust logic as needed)
        #nc_file = nc_files[0]

        # Open NetCDF file with xarray
        ds = xr.open_mfdataset(nc_files)
        #print(ds)
        # Check if 'qc' variable exists
        if 'qc' in ds.data_vars or 'qc' in ds.coords:
            zc = ds['zc'][0]
            dz = zc.copy()
            dz[0:-1] = zc[1::].values-zc[0:-1].values
            qc = ds['qc']+ds['qr']
            qc_m2 = qc*dz*rho.reshape(1,-1,1,1)
            qc_m2sum = np.sum(qc_m2[:,0:17,:,:], axis = 1)
            print(f"✓ {folder}: qc shape = {qc.shape}, dtype = {qc.dtype}")
            
            # Optionally print attributes and coordinates
            # print(f"  Coordinates: {list(qc.coords.keys())}")
            # print(f"  Attributes: {qc.attrs}")
        else:
            available_vars = list(ds.data_vars.keys())
            print(f"⚠️  {folder}: 'qc' variable not found. Available: {available_vars}")

        print("\nQC_M2 added to dataset", folder)

        # Optional: Save to file
        #np.save('/data/hhlee/'+folder+'_qc_5000m2.npy', qc_m2sum)
        #qc_xr.to_netcdf('/data/hhlee/'+folder+'_qc_m2.nc')

        # Close the dataset
        ds.close()

    except Exception as e:
        print(f"❌ Error processing {folder}: {str(e)}")

#my calculation
s=True
case='ish_20111117'
dataDir=f'{foldpath}/{case}'
case='ish_20111117'
tt=24
lwp=vvm.calcLWP(dataDir,case,tt,s,5000)
plt.subplot(121)
plt.contourf(qc_m2sum[tt,:256,:256])
plt.colorbar()
plt.subplot(122)
plt.contourf(lwp[128:128+256,128:128+256])
plt.colorbar()


