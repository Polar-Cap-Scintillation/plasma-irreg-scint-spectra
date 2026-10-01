# calculate_conjunctions.py
# Calculate conjunctions between In Situ LEO satellites and GNSS

import numpy as np
import datetime as dt
import pymap3d as pm
import csv
import argparse
import sys
sys.path.append('/Users/e30737/Desktop/Research/PolarCapScintillation/conjunctions')
from satellite_conjunction import SatConj
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

#receiver_name = 'res'

# Get gnss receiver site from command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('receiver_site')
args = parser.parse_args()
receiver_name = args.receiver_site

with open('CHAINsites.txt', 'r') as cf:
    chain_data = csv.reader(cf)
    for row in chain_data:
        if row[1] == receiver_name:
            receiver_site = [float(row[2]), float(row[3]), 0.]

output_file = f'insitu_gnss_conj_{receiver_name}.txt'

starttime = dt.datetime(2024,1,1, tzinfo=dt.timezone.utc)
endtime = dt.datetime(2024,1,2, tzinfo=dt.timezone.utc)

elev_cutoff = 30.
tstep = 60.

# Swarm A, B, C; LLITED A, B
insitu_sats = [{'name': 'Swarm A', 'NORAD': 39452, 'start': dt.datetime(2013,12,2, tzinfo=dt.timezone.utc), 'end': dt.datetime.now(tz=dt.timezone.utc)},
               {'name': 'Swarm B', 'NORAD': 39451, 'start': dt.datetime(2013,12,2, tzinfo=dt.timezone.utc), 'end': dt.datetime.now(tz=dt.timezone.utc)},
               {'name': 'Swarm C', 'NORAD': 39453, 'start': dt.datetime(2013,12,2, tzinfo=dt.timezone.utc), 'end': dt.datetime.now(tz=dt.timezone.utc)},
               {'name': 'LLITED A', 'NORAD': 56219, 'start': dt.datetime(2023,4,15, tzinfo=dt.timezone.utc), 'end': dt.datetime(2024,8,28, tzinfo=dt.timezone.utc)},
               {'name': 'LLITED B', 'NORAD': 56220, 'start': dt.datetime(2023,4,15, tzinfo=dt.timezone.utc), 'end': dt.datetime(2024,8,28, tzinfo=dt.timezone.utc)}]

# Generate list of all GPS satellites and their vaild time ranges from IGS file
with open('igs_satellite_metadata.snx', 'r', encoding='iso-8859-1') as f:
    # Skip to SATELLITE/IDENTIFIER block
    for line in f:
        try:
            if line.split()[0] == '+SATELLITE/IDENTIFIER':
                break
        except IndexError:
            pass
    # Skip heading
    for _ in range(3):
        f.readline()
    # Read block into dictionary
    svn_norad = dict()
    for line in f:
        try:
            svn_norad[line.split()[0]] = line.split()[2]
        except IndexError:
            break
    # Skip to SATELLITE/PRN block
    for line in f:
        try:
            if line.split()[0] == '+SATELLITE/PRN':
                break
        except IndexError:
            pass
    # Skip heading
    for _ in range(3):
        f.readline()
    # Read block into dictionary
    gnss_catalog = list()
    for line in f:
        try:
            fields = line.split()
            sd = dt.datetime.strptime(fields[1][:8],'%Y:%j').replace(tzinfo=dt.timezone.utc)
            try:
                ed = dt.datetime.strptime(fields[2][:8],'%Y:%j').replace(tzinfo=dt.timezone.utc)
            except ValueError:
                ed = dt.datetime.now(tz=dt.timezone.utc)
            gnss_catalog.append({'SVN':fields[0], 'NORAD':svn_norad[fields[0]], 'start':sd, 'end':ed, 'PRN':fields[3]})
        except IndexError:
            break

# Restrict to ONLY GPS satellites within time frame of interest
gnss_catalog = [entry for entry in gnss_catalog if entry['SVN'].startswith('G')]
gnss_sats = [entry for entry in gnss_catalog if (entry['start']<endtime and entry['end']>starttime)]


# Generate lists of all passes for in situ satellites
print('Finding passes for In Situ...')
passes_insitu = list()
for sat in insitu_sats:
    print(sat['name'], 'NORAD ID:', sat['NORAD'])
    # Initialize conjunction object
    insitu = SatConj(*receiver_site, sat['NORAD'], tolerance=90.-elev_cutoff, deltime=tstep)
    # Find correct time bounds
    if starttime > sat['start']:
        st = starttime.replace(tzinfo=None)
    else:
        st = sat['start'].replace(tzinfo=None)
    if endtime < sat['end']:
        et = endtime.replace(tzinfo=None)
    else:
        et = sat['end'].replace(tzinfo=None)
    # Calculate conjunctions with ground site
    passes_insitu.append(insitu.conjunctions(st, et))

# Generate lists of all passes for GNSS satellites
print('Finding passes for GNSS...')
passes_gnss = list()
for sat in gnss_sats:
    print('PRN', sat['PRN'], 'NORAD ID:', sat['NORAD'])
    # Initalize conjunction object
    gnss = SatConj(*receiver_site, sat['NORAD'], tolerance=90.-elev_cutoff, deltime=tstep)
    # Find the correct time bounds
    if starttime > sat['start']:
        st = starttime.replace(tzinfo=None)
    else:
        st = sat['start'].replace(tzinfo=None)
    if endtime < sat['end']:
        et = endtime.replace(tzinfo=None)
    else:
        et = sat['end'].replace(tzinfo=None)
    # Calculate conjunctions with ground site
    passes_gnss.append(gnss.conjunctions(st, et))


# Calculate intersections between all passes
map_proj = ccrs.AzimuthalEquidistant(central_longitude=receiver_site[1], central_latitude=receiver_site[0])
print('Calculating conjunctions...')
with open(output_file, 'w') as out:
    total_conjunctions = 0
    out.write('InSitu Sat     InSitu NORAD   GNSS PRN       GNSS NORAD     Time                   Ang Sep        InSitu Az      InSitu El      GNSS Az        GNSS El        \n')
    for isat, passes1 in zip(insitu_sats, passes_insitu):
        sat_conj = 0
        for gsat, passes2 in zip(gnss_sats, passes_gnss):
            for pass1 in passes1:
                for pass2 in passes2:
                    conj = np.argwhere(pass1['time'][:,None]==pass2['time'][None,:])
                    for c in conj:
                        a1, e1, r1 = pm.ecef2aer(*pass1['position'][c[0],:], *receiver_site)
                        a2, e2, r2 = pm.ecef2aer(*pass2['position'][c[1],:], *receiver_site)
                        p1 = np.deg2rad(e1)
                        p2 = np.deg2rad(e2)
                        l1 = np.deg2rad(a1)
                        l2 = np.deg2rad(a2)
                        dist = 2*np.arcsin(np.sqrt(np.sin((p2-p1)/2.)**2 + np.cos(p1)*np.cos(p2)*np.sin((l2-l1)/2.)**2))
                        if np.rad2deg(dist) < 10.:
                            out.write(f'{isat['name']:<15}{isat['NORAD']:<15}{gsat['PRN']:<15}{gsat['NORAD']:<15}{pass1['time'][c[0]]:%Y-%m-%d %H:%M:%S}    {np.rad2deg(dist):<15.2f}{a1:<15.4f}{e1:<15.4f}{a2:<15.4f}{e2:<15.4f}\n')
                            
                            # Generate conjunction plots for confirmation
                            #fig = plt.figure()
                            #az1, el1, _ = pm.ecef2aer(*pass1['position'].T, *receiver_site)
                            #az2, el2, _ = pm.ecef2aer(*pass2['position'].T, *receiver_site)
                            #lat1, lon1, _ = pm.ecef2geodetic(*pass1['position'].T)
                            #lat2, lon2, _ = pm.ecef2geodetic(*pass2['position'].T)
                            #ax = fig.add_subplot(121, projection='polar')
                            #ax.plot(np.deg2rad(az1), np.cos(np.deg2rad(el1)))
                            #ax.plot(np.deg2rad(az2), np.cos(np.deg2rad(el2)))
                            #ax.set_theta_zero_location("N")
                            #ax.set_theta_direction(-1)
                            #ax = fig.add_subplot(122, projection=map_proj)
                            #ax.scatter(receiver_site[1], receiver_site[0], s=50, marker='^', transform=ccrs.Geodetic())
                            #ax.plot(lon1, lat1, transform=ccrs.Geodetic())
                            #ax.plot(lon2, lat2, transform=ccrs.Geodetic())
                            #ax.gridlines(draw_labels=True)
                            #ax.coastlines()
                            #fig.suptitle(f'{pass1['time'][c[0]]:%Y-%m-%d %H:%M:%S}      {isat['name']}      {gsat['PRN']}')
                            #outplot = f'{pass1['time'][c[0]]:%Y%m%d_%H%M%S}_{isat['name'].replace(' ','')}_{gsat['PRN']}.png'
                            #fig.savefig(outplot)


                            total_conjunctions +=1
                            sat_conj += 1
        print(isat['name'], sat_conj)

print('Total Conjunctions:', total_conjunctions)
                
