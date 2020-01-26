#!/usr/bin/python3
import urllib
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
import threading

# logging setup
logging.basicConfig(level=logging.INFO)

# GLOBALS within a CLASS are super confsuing!!
# I'm not sure this is pythionicly correct since this code is outside the class ?
global args
global parser
parser = argparse.ArgumentParser()
parser.add_argument('-v','--verbose', help='verbose error logging', action='store_true', dest='bool_verbose', required=False, default=False)
parser.add_argument('-c','--cycle', help='Ephemerial top 10 every 10 secs for 60 secs', action='store_true', dest='bool_tenten60', required=False, default=False)
parser.add_argument('-t','--tops', help='show top ganers/losers', action='store_true', dest='bool_tops', required=False, default=False)
parser.add_argument('-s','--screen', help='screener logic parser', action='store_true', dest='bool_scr', required=False, default=False)
parser.add_argument('-u','--unusual', help='unusual up & down volume', action='store_true', dest='bool_uvol', required=False, default=False)

#####################################################

class unusual_vol:
    """Class to discover and extract unusual volume data from NASDAQ.com data source"""

    # global accessors
    df0 = ""                # DataFrame - Full list of top gainers
    df1 = ""                # DataFrame - Ephemerial list of top 10 gainers. Allways overwritten
    df2 = ""                # DataFrame - Top 10 ever 10 secs for 60 secs
    up_table_data = ""      # BS4 handle of the <table> with UP vol data
    down_table_data = ""    # BS4 handle of the <table> with UP vol data
    yti = 0                 # Unique instance identifier
    cycle = 0               # class thread loop counter

    def __init__(self, yti):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INSTANTIATE' % cmi_debug )
        # init empty DataFrame with preset colum names
        self.df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', "Vol", 'Vol_pct', 'Time'] )
        self.df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change' "Vol", 'Vol_pct', 'Time'] )
        self.df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change' "Vol", 'Vol_pct', 'Time'] )
        self.yti = yti
        return

# method #1
    def get_up_unvol_data(self):
        """Connect to old.nasdaq.com and extract (scrape) the raw HTML string data from"""
        """the embedded html data table [UP_on_unusual_vol ]. Returns a BS4 handle."""

        cmi_debug = __name__+"::"+self.get_up_unvol_data.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        with urllib.request.urlopen("https://old.nasdaq.com/markets/unusual-volume.aspx") as url:
            s = url.read()
            logging.info('%s - read html stream' % cmi_debug )
            self.soup = BeautifulSoup(s, "html.parser")

        logging.info('%s - save data handle' % cmi_debug )
        self.all_tagid_up = self.soup.find( id="_up" )           # locate the section with ID = '_up' > output RAW htnml
        self.up_table_data = self.all_tagid_up.table             # move into the <table> section > ouput RAW HTML
        self.up_table_rows1 = ( tr_row for tr_row in ( self.up_table_data.find_all( 'tr' ) ) )      # build a generattor of <tr> objects

        # other HTML accessor methods - good for reference
        #self.up_table_rows = self.up_table_data.find_all( "tr")
        #self.up_table_rows = self.up_table_data.tr
        #self.up_table_rows2 = self.up_table_data.td

        logging.info('%s - close url handle' % cmi_debug )
        url.close()
        return

# method #2
    def build_df0(self):
        """Build-out a fully populated Pandas DataFrame containg all the"""
        """extracted/scraped fields from the html/markup table data"""
        """Wrangle, clean/convert/format the data correctly."""

        args = vars(parser.parse_args())    # ensure CMDLine args are accessible within this class:method
        cmi_debug = __name__+"::"+self.build_df0.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Drop all rows from DF0' % cmi_debug )
        self.df0.drop(self.df0.index, inplace=True)

        x = 1    # row counter Also leveraged for unique dataframe key
        col_headers = next(self.up_table_rows1)     # ignore the 1st TR row object, which is column header titles

        for tr_data in self.up_table_rows1:     # genrator object
            #global args
            extr_strings = tr_data.stripped_strings
            co_sym = next(extr_strings)
            co_name = next(extr_strings)
            price = next(extr_strings)
            price_net = next(extr_strings)
            arrow_updown = next(extr_strings)
            price_pct = next(extr_strings)
            vol_abs = next(extr_strings)
            vol_pct = next(extr_strings)

            # wrangle & clean the data
            co_sym_lj = np.char.ljust(co_sym, 6)       # use numpy to left justify TXT in pandas DF
            co_name_lj = np.char.ljust(co_name, 20)    # use numpy to left justify TXT in pandas DF
            price_cl = (re.sub('[ $]', '', price))
            price_pct_cl = (re.sub('[%]', '', price_pct))
            vol_abs_cl = (re.sub('[,]', '', vol_abs))
            vol_pct_cl = (re.sub('[%]', '', vol_pct))

            self.data0 = [[ \
                       x, \
                       co_sym_lj, \
                       co_name_lj, \
                       np.float(price_cl), \
                       np.float(price_net), \
                       np.float(price_pct_cl), \
                       np.float(vol_abs_cl), \
                       np.float(vol_pct_cl), \
                       time_now ]]

            self.temp_df0 = pd.DataFrame(self.data0, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', "Vol", 'Vol_pct', 'Time' ], index=[x] )
            self.df0 = self.df0.append(self.temp_df0)    # append this ROW of data into the REAL DataFrame
            # DEBUG
            if args['bool_verbose'] is True:        # DEBUG
                print ( "================================", x, "======================================")
                print ( co_sym, co_name, price_cl, price_net, price_pct_cl, vol_abs_cl, vol_pct_cl )

            x += 1
        logging.info('%s - populated new DF0 dataset' % cmi_debug )
        return x        # number of rows inserted into DataFrame (0 = some kind of #FAIL)
                        # sucess = lobal class accessor (y_toplosers.df0) populated & updated

# method #4
    def up_unvol_listall(self):
        """Print the full DataFrame table list of NASDAQ unusual UP volumes"""
        """Sorted by % Change"""
        logging.info('ins.#%s.up_unvol_listall() - IN' % self.yti )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.df0.sort_values(by='Pct_change', ascending=False ) )    # only do after fixtures datascience dataframe has been built
        return
