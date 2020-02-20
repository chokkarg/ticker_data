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

#####################################################

class y_newsfilter:
    """Class to extract a specific stock's News from finance.yahoo.com"""

    # global accessors
    n_df0 = ""          # DataFrame - Full list of top gainers
    n_df1 = ""          # DataFrame - Ephemerial list of top 10 gainers. Allways overwritten
    n_df2 = ""          # DataFrame - Top 10 ever 10 secs for 60 secs
    tag_dataset = ""      # BS4 handle of the <tr> extracted data
    inst_uid = 0
    cycle = 0           # class thread loop counter
    symbol = ""         # Unique company symbol

    def __init__(self, i, symbol, global_args):
        # WARNING: There is/can-be NO checking to ensure this is a valid/real symbol
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INIT inst' % cmi_debug )
        # init empty DataFrame with present colum names
        self.n_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.n_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.n_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.inst_uid = i
        self.symbol = symbol
        return

# method #1
    def get_news_data(self):
        """Connect to finance.yahoo.com and extract (scrape) the raw data out of"""
        """the complex webpage [Stock:News ] html data table. Returns a BS4 handle."""

        cmi_debug = __name__+"::"+self.get_news_data.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        news_url = "https://finance.yahoo.com/quote/" + self.symbol + "/news?p=" + self.symbol      # form the correct URL
        logging.info('%s - URL:' % (cmi_debug) )
        print ( f"News URL: {news_url}" )
        with urllib.request.urlopen(news_url) as url:
            s = url.read()
            logging.info('%s - read html stream' % cmi_debug )
            self.soup = BeautifulSoup(s, "html.parser")
        # ATTR style search. Results -> Dict
        # <tr tag in target merkup line has a very complex 'class=' but the attributes are unique. e.g. 'simpTblRow' is just one unique attribute
        logging.info('%s - save data object handle' % cmi_debug )
        #self.tag_dataset = self.soup.find_all(attrs={"class": "C(#959595)"} )        # the section in the HTML page we focus-in on
        self.tag_dataset = self.soup.find(attrs={"class": "My(0) Ov(h) P(0) Wow(bw)"} )
        # <div class="C(#959595) Fz(11px) D(ib) Mb(6px)">
        logging.info('%s - close url handle' % cmi_debug )
        url.close()
        return

# method #2
    def build_n_df0(self):
        """Build-out a fully populated Pandas DataFrame containg all the"""
        """extracted/scraped fields from the html/markup table data"""
        """Wrangle, clean/convert/format the data correctly."""

        cmi_debug = __name__+"::"+self.build_n_df0.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Drop all rows from DF0' % cmi_debug )
        self.n_df0.drop(self.n_df0.index, inplace=True)
        x = 1    # row counter Also leveraged for unique dataframe key
        # full_dataset = self.tag_dataset
        #li_subset = self.tag_dataset[0].li.find_all(attrs={"class": "C(#959595)"})
        # li_subset = self.tag_dataset[0].li.find_all()
        li_subset = self.tag_dataset.find_all('li')
        # print ( "***li TEST #1 ***" )
        # print ( li_subset )
        #print ( "***li TEST #2 ***" )
        #print ( li_subset.next_element )

        #li_alldataset = self.tag_dataset[0].li.find_all(attrs={"class": "C(#959595)"} )
        #print ( "***li alldataset #3 ***" )
        #print ( li_alldataset )
        for datarow in range(len(li_subset)):
            html_element = str(li_subset[datarow])
            print ( f"================ Row: {x} ====================" )
            #print ( f"Cycle: {x}\nRow: {html_element}" )
            get_soup = BeautifulSoup( html_element, features="html.parser" )
            y = 1
            div1 = get_soup.find(attrs={"class": "C(#959595)"} )
            print ( f"=== full div1 ===\n{div1}")
            # print ( f"Inner loop (div1): {div1.strings}" )
            for e in get_soup.div.next_elements:
                # print ( f"=============== Element {y} =====================" )
                print ( f"==== Element: {y} ====" )
                print ( e )
                y += 1

            #for datarow in self.tag_dataset:
            # BS4 generator object from "extracted strings" BS4 operation (nice)
            #print ( f"News data row: {x} - {datarow}" )
            #extr_strings = datarow.stripped_strings
            #news_outlet = datarow.find_all(attrs={"class": "C(#959595)"} )         # 1st key section within this datarow
            #news_outlet = datarow.find(attrs={"class": "C(#959595)"} )         # 1st key section within this datarow

            #time_ago = datarow.next_element            # 2nd <td> : company name

            # THESE WORK ...
            # soup.div.contents[0]
            # soup.div.string

            #got_you = get_soup.string
            # got_you = get_soup.find(data-reactid==True)

            # print ( f"Cycle: {x} Data row: {my_list[datarow]}" )
            #print ( f"Time of news: {time_ago}" )
            """
            price = next(extr_strings)          # 3rd <td> : price
            change = next(extr_strings)         # 4th <td> : $ change
            pct = next(extr_strings)            # 5th <td> : % change
            vol = next(extr_strings)            # 6th <td> : volume
            avg_vol = next(extr_strings)        # 6th <td> : Avg. vol over 3 months)
            mktcap = next(extr_strings)         # 7th <td> : Market cap
            # 8th <td> : PE ratio (I dont care aboutt this. so ignore/disgard it)


            # co_sym_lj = np.array2string(np.char.ljust(co_sym, 6) )      # left justify TXT in DF & convert to raw string

            # co_name_lj = (re.sub('[\'\"]', '', co_name) )    # remove " ' and strip leading/trailing spaces
            # co_name_lj = np.array2string(np.char.ljust(co_name_lj, 25) )   # left justify TXT in DF & convert to raw string
            # co_name_lj = (re.sub('[\']', '', co_name_lj) )    # remove " ' and strip leading/trailing spaces

            ##co_name_lj = np.array2string(np.char.ljust(co_name, 20) )   # left justify TXT in DF & convert to raw string
            ##co_name_lj = (re.sub('[\'\"]', '', co_name_lj))    # remove " '

            mktcap = (re.sub('[N\/A]', '0', mktcap))   # handle N/A

            TRILLIONS = re.search('T', mktcap)
            BILLIONS = re.search('B', mktcap)
            MILLIONS = re.search('M', mktcap)

            if TRILLIONS:
                mktcap_clean = np.float(re.sub('T', '', mktcap))
                mb = "XT"
                logging.info('%s - Mega Cap/TRILLIONS. set XT' % cmi_debug )

            if BILLIONS:
                mktcap_clean = np.float(re.sub('B', '', mktcap))
                mb = "LB"
                logging.info('%s - Large cap/BILLIONS. set LB' % cmi_debug )

            if MILLIONS:
                mktcap_clean = np.float(re.sub('M', '', mktcap))
                mb = "LM"
                logging.info('%s - Large cap/MILLIONS. set LM' % cmi_debug )

            if not TRILLIONS and not BILLIONS and not MILLIONS:
                mktcap_clean = 0    # error condition - possible bad data
                mb = "LZ"
                logging.info('%s - bad mktcap data. set to L0' % cmi_debug )
                # handle bad data in mktcap html page field

            # note: Pandas DataFrame : top_gainers pre-initalized as EMPYT
            # Data treatment:
            # Data is extracted as raw strings, so needs wrangeling...
            #    price - stip out any thousand "," seperators and cast as true decimal via numpy
            #    change - strip out chars '+' and ',' and cast as true decimal via numpy
            #    pct - strip out chars '+ and %' and cast as true decimal via numpy
            #    mktcap - strio out 'B' Billions & 'M' Millions
            self.data0 = [[ \
                       x, \
                       re.sub('\'', '', co_sym_lj), \
                       co_name_lj, \
                       np.float(re.sub('\,', '', price)), \
                       np.float(re.sub('[\+,]', '', change)), \
                       np.float(re.sub('[\+,%]', '', pct)), \
                       mktcap_clean, \
                       mb, \
                       time_now ]]

            self.df0 = pd.DataFrame(self.data0, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time' ], index=[x] )
            self.n_df0 = self.n_df0.append(self.df0)    # append this ROW of data into the REAL DataFrame
            """
            x+=1
        logging.info('%s - populated new DF0 dataset' % cmi_debug )
        return x        # number of rows inserted into DataFrame (0 = some kind of #FAIL)
                        # sucess = lobal class accessor (y_topgainers.n_df0) populated & updated

# method #3
# Hacking function - keep me arround for a while
    def prog_bar(self, x, y):
        """simple progress dialogue function"""
        if x % y == 0:
            print ( " " )
        else:
            print ( ".", end="" )
        return

# method #4
    def topg_listall(self):
        """Print the full DataFrame table list of Yahoo Finance Top Gainers"""
        """Sorted by % Change"""

        cmi_debug = __name__+"::"+self.topg_listall.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.n_df0.sort_values(by='Pct_change', ascending=False ) )    # only do after fixtures datascience dataframe has been built
        return

# method #5
    def build_top10(self):
        """Get top 15 gainers from main DF (df0) -> temp DF (df1)"""
        """df1 is ephemerial. Is allways overwritten on each run"""

        cmi_debug = __name__+"::"+self.build_top10.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )

        logging.info('%s - Drop all rows from DF1' % cmi_debug )
        self.n_df1.drop(self.n_df1.index, inplace=True)
        logging.info('%s - Copy DF0 -> ephemerial DF1' % cmi_debug )
        self.n_df1 = self.n_df0.sort_values(by='Pct_change', ascending=False ).head(15).copy(deep=True)    # create new DF via copy of top 10 entries
        self.n_df1.rename(columns = {'Row':'ERank'}, inplace = True)    # Rank is more accurate for this Ephemerial DF
        self.n_df1.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential
        return

# method #7
    def print_top10(self):
        """Prints the Top 10 Dataframe"""

        cmi_debug = __name__+"::"+self.print_top10.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.n_df1.sort_values(by='Pct_change', ascending=False ).head(15) )
        return

# method #6
    def build_tenten60(self, cycle):
        """Build-up 10x10x060 historical DataFrame (df2) from source df1"""
        """Generally called on some kind of cycle"""

        cmi_debug = __name__+"::"+self.build_tenten60.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        self.n_df2 = self.n_df2.append(self.n_df1, ignore_index=False)    # merge top 10 into
        self.n_df2.reset_index(inplace=True, drop=True)    # ensure index is allways unique + sequential
        return
