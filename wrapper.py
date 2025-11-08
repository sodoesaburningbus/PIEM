### This object provides a wrapper for the Iowa Enviromental Mesonet (IEM).
### Notably, IEM maintains an API for accessing the ASOS network, which is the
### focus of this wrapper.
###
### Christopher Phillips
### Valparaiso University

# Import required packages
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

### The wrapper object
### Inputs:
###   start_date, datetime object, UTC, the earliest date in the download.
###   end_date, datetime object, UTC, the latest date in the download. Defaults to the start date.
###   station, optional string, name of the station to download. If blank, downloads all.
###   special, optional boolean (False), whether to download special METAR observations as well.
###   Flags for which variables to include default to False except, temperature, dewpoint, wind dir., wind speed, and MSLP.
###     I consider these the bare minimum for a station plot.
###     Setting all=True will download all variables regardless of individual flags.
###
### Attributes:
###   obs, pandas dataframe containing the observations
###   api_call, the origianl api call
###
class api:

    ### The initialization function
    ### This creates the API call and pulls the data
    def __init__(self, start_date, end_date=None, tmpf=True, dwpf=True, drct=True, sknt=True, mslp=True, ave_wind_speed_kts=False, ave_wind_drct=False,
                 relh=False, p01i=False, alti=False, vsby=False, gust=False, skyc1=False, skyc2=False, skyc3=False, skyc4=False,
                 skyl1=False, skyl2=False, skyl3=False, skyl4=False, wxcodes=False, ice_accretion_1hr=False,
                 ice_accretion_3hr=False, ice_accretion_6hr=False, peak_wind_gust=False, peak_wind_drct=False,
                 peak_wind_time=False, feel=False, metar=False, snowdepth=False, special=False, all=False, station=None):

        # List of valid names for the variables
        args = locals()
        valid_names = ['tmpf', 'dwpf', 'drct', 'sknt', 'mslp', 'relh', 'p01i', 'alti', 'vsby', 'gust', 'skyc1', 'skyc2', 'skyc3', 'skyc4', 'skyl1', 'skyl2',
                       'skyl3', 'skyl4', 'wxcodes', 'ice_accretion_1hr', 'ice_accretion_3hr', 'ice_accretion_6hr', 'peak_wind_gust', 'peak_wind_drct',
                       'peak_wind_time', 'feel', 'metar', 'snowdepth', 'ave_wind_speed_kts', 'ave_wind_drct']
        
        # Sort out data flags
        if (all):
            data_flags = ['all']
        else:
            data_flags = list([v for v in valid_names if args[v]])

        if (station==None):
            station_str = ''
        else:
            station_str = f'&station={station}'

        if (special):
            report_type='3&report_type=4'
        else:
            report_type='3'

        if (end_date == None):
            end_date = start_date

        # Build the URL for the api call
        self.api_call = f'https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?&data={data_flags}&year1={start_date.year}&month1={start_date.month}&day1={start_date.day}\
            &year2={end_date.year}&month2={end_date.month}&day2={end_date.day}&tz=UTC&format=onlycomma&latlon=yes&elev=yes&missing=M&direct=no&report_type={report_type}'\
            +station_str
        self.api_call = self.api_call.replace('[','').replace(']', '').replace(' ','').replace("'","")

        # Call the API and fill missing values with Nans
        self.obs = pd.read_csv(self.api_call)
        self.obs.replace('M', np.nan, inplace=True)
        
        # Attempt to convert everything to floats
        for name in self.obs.columns:
            try:
                self.obs[name] = np.array(self.obs[name], dtype=float)
            except:
                pass

    ### Function to extract a specific UTC hour
    ### Rounds observations to nearest hour and subsets the dataframe
    def extract_hour(self, hour):

        # Locate valid hours
        inds = []
        for i, datestr in enumerate(self.obs['valid']):
            h = int(datestr[-5:-3])
            m = int(datestr[-2:])
            if (m >= 30):
                h = h+1
            if (h == hour):
                inds.append(i)

        # Subset the dataframe
        subset = self.obs.iloc[inds]

        return subset
    
    ### Function to convert cloud cover text to eights
    ### Inputs:
    ###  cloud_text, array containing text for cloud cover
    ###    text must be stadnard, 'SKC', 'FEW', 'SCT', etc.
    ###
    ### Outputs:
    ###   sky cover array in integer eigths
    ###
    def cloud_eigths(self, cloud_text):

        cloud_cover = np.zeros(cloud_text.size, dtype=int)
        codes = ['SKC','NSC','FEW','SCT','BKN','OVC']
        vals = [0, 0, 1, 3, 6, 8]
        for c, v in zip(codes, vals):
            cloud_cover[cloud_text == c] = v

        return cloud_cover