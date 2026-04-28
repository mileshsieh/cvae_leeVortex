import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path

# Read folder names from case.txt
foldpath = '/data2/VVM/taiwanvvm_s_winter_era5/'
ncase=1476
with open(f'/data/mileshsieh/cvae_leeVortex/data/caseList.{ncase}.txt', 'r') as f:
    folders = [line.strip() for line in f if line.strip()]

print(f"Found {len(folders)} folders to process\n")

# Base directory path (adjust this to your actual base path)
base_path = Path(foldpath)  # Change this to your data directory
results = []
for folder in folders:
    folder_path = base_path / folder
    #print(folder_path)
    # Look for NetCDF files in the folder
    try:
        if not folder_path.exists():
            print(f"⚠️  Folder not found: {folder}")
            continue

        with open(f"{folder_path}/fort.98", 'r') as f:
            lines = f.readlines()
    
        # Find the starting line
        start_line = None
        for i, line in enumerate(lines):
            if 'K, RHO(K),THBAR(K),PBAR(K),PIBAR(K),QVBAR(K)' in line:
                start_line = i + 2  # Skip header and separator line
                break

        print(f"Data starts at line: {start_line}")

        # Find the line where RHOZ starts
        rhoz_start = None
        for i, line in enumerate(lines):
            if 'K, RHOZ(K)' in line:
                rhoz_start = i + 2
                break

        # Read the data using pandas
        df = pd.read_csv(f"{folder_path}/fort.98", 
                         sep=r'\s+',
                         skiprows=start_line,
                         nrows=35,  # Read 35 levels
                         names=['K', 'RHO', 'THBAR', 'PBAR', 'PIBAR', 'QVBAR'])

        # Read RHOZ data
        rhoz_df = pd.read_csv(f"{folder_path}/fort.98",
                          sep=r'\s+',
                          skiprows=rhoz_start,
                          nrows=34,
                          names=['K', 'RHOZ'],
                          engine='python')

        # Extract THBAR and PBAR
        THBAR = df['THBAR'].values
        PBAR = df['PBAR'].values
        rho = rhoz_df['RHOZ'].values

        # Calculate LTS
        theta_surface = THBAR[0]
        p_surface = PBAR[0]

        # Find level closest to 700 hPa (70000 Pa)
        target_p = 70000
        idx_700 = np.argmin(np.abs(PBAR - target_p))
        theta_700 = THBAR[idx_700]
        p_700 = PBAR[idx_700]

        # Calculate LTS
        LTS = theta_700 - theta_surface
        # Find level closest to 925 hPa (92500 Pa)
        target_p = 92500
        idx_925 = np.where(PBAR<target_p)[0][0]

        # Find NetCDF files (.nc extension) #ish_20190404.L.Thermodynamic-000144.nc
        ncf1 = (f"{folder_path}/archive/{folder}.L.Thermodynamic-000000.nc")
        ncf2 = (f"{folder_path}/archive/{folder}.L.Dynamic-000000.nc")
        #ncf1 = list(folder_path.glob('archive/*Thermodynamic*-000000.nc'))
        #ncf2 = list(folder_path.glob('archive/*Dynamic-000000.nc'))

        if not ncf1:
            print(f"⚠️  No NetCDF files in: {folder}")
            continue

        # Process the first NetCDF file found (or adjust logic as needed)
        #nc_file = nc_files[0]

        # Open NetCDF file with xarray
        ds = xr.open_dataset(ncf1)
        ds2 = xr.open_dataset(ncf2)
        #print(ds)
        # Check if 'qc' variable exists
        if 'qv' in ds.data_vars or 'qv' in ds.coords:
            zc = ds['zc']
            dz = zc.copy()
            dz[0:-1] = zc[1::].values-zc[0:-1].values
            qv = ds['qv']
            u = ds2['u']
            v = ds2['v']
            wspd = np.sqrt(u*u+v*v)
            wd = (270 - np.degrees(np.arctan2(v, u))) % 360
            ivt = qv*(dz*rho).values.reshape(1,-1,1,1)*wspd
            ivt_sum = np.sum(ivt[:,0:14,:,:], axis = 1)
            # Find level closest to 925 hPa (92500 Pa)
            target_p = 92500
            idx_925 = np.argmin(np.abs(PBAR - target_p))

            value = np.array(ivt_sum[0,0,0])
            #calculate vertical shear between surface and 925 in terms of WD/WS
            ws = np.array([np.sqrt(u[0,k,0,0]*u[0,k,0,0]+v[0,k,0,0]*v[0,k,0,0]) for k in range(1,idx_925)])
            wd = np.array([(270 - np.degrees(np.arctan2(v[0,k,0,0], u[0,k,0,0]))) % 360 \
                           for k in range(1,idx_925)])
            dws925 = ws[-1] - ws[0]
            dwd925 = wd[-1] - wd[0]
            #calculate mean TH and dTH below 925
            dth925 = THBAR[idx_925-1]-THBAR[1]
            th925 = np.mean(THBAR[1:idx_925])
            #calculate mean qv and dqv below 925
            dqv925 = qv[0,idx_925-1,0,0]-qv[0,1,0,0]
            qv925 = np.mean(qv[0,1:idx_925,0,0])
            #calculate mean wind below 925
            u925 = np.mean(u[0,1:idx_925,0,0])
            v925 = np.mean(v[0,1:idx_925,0,0])
            ws925 = np.sqrt(u925*u925+v925*v925)
            wd925 = (270 - np.degrees(np.arctan2(v925, u925))) % 360

            #print(f"{folder}", value)
            results.append([folder, value, u925.item(), v925.item(), \
                            ws925.item(), wd925.item(), LTS, \
                            dws925.item(), dwd925.item(), dth925.item(), th925.item(),\
                            dqv925.item(), qv925.item(),])

        else:
            available_vars = list(ds.data_vars.keys())
            print(f"⚠️  {folder}: 'qc' variable not found. Available: {available_vars}")

        print(f"{folder}", np.array(ivt_sum[0,0,0]), LTS)

        # Optional: Save to file
        #np.save('/data/hhlee/inputdata/'+folder+'_qc_5000m2.npy', qc_m2sum)
        #qc_xr.to_netcdf('/data/hhlee/'+folder+'_qc_m2.nc')

        # Close the dataset
        ds.close()
    except Exception as e:
        print(f"❌ Error processing {folder}: {str(e)}")
        
# Save to CSV
df = pd.DataFrame(results, columns=['caseName', 'IVT', 'U925','V925','WS925','WD925', 'LTS',\
        'dWS925', 'dWD925', 'dTH925', 'TH925', 'dqv925','qv925'])
df.to_csv(f'../data/synoptic.{ncase}.csv', index=False)
print(f"\nSaved to: ../data/synoptic.{ncase}.csv")

