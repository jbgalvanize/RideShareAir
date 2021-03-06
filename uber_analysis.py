import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

class UberAnalysis(object):
    """
    Cleans parsed Uber data
    """
    def __init__(self, filename):
        """
        Input: Parsed Uber Data
        Output: Uber DataFrame
        """
        self.filename = filename
        self.df = pd.read_csv(self.filename, error_bad_lines=False)
        self._organize_df()

    def _organize_df(self):
        """
        Output: Cleans the dataframes and restructures the dataframe for analysis
        """
        self.df.rename(columns = {'estimate_y':'price_estimate', 'estimate_x':'pickup_estimate', 'duration':'trip_duration', 'distance':'trip_distance', 'price_details.base':'base_price', 'price_details.minimum':'base_minimum_price', 'price_details.cost_per_minute':'cost_per_minute', 'price_details.cost_per_distance':'cost_per_distance', 'price_details.distance_unit':'distance_unit', 'price_details.cancellation_fee':'cancellation_fee', 'price_details.currency_code':'currency_code', 'price_details.service_fees':'service_fees', 'minimum':'surge_minimum_price'}, inplace=True)
        self.df['record_time'] = pd.to_datetime(self.df['record_time'], unit='s')
        self.df['avg_price_est'] = (self.df['low_estimate'] + self.df['high_estimate']) / 2.
        self.df['service_fees_type'] = self.df['service_fees'].apply(lambda x: eval(x) if type(x) == str else 0).apply(lambda x: 'None' if not x else x[0]['name'])
        self.df['service_fees'] = self.df['service_fees'].apply(lambda x: eval(x) if type(x) == str else 0).apply(lambda x: 0 if not x else x[0]['fee'])
        self.df = self.df[['record_time','city','display_name','price_estimate',
        'low_estimate','avg_price_est','high_estimate','trip_duration','trip_distance','surge_multiplier','surge_minimum_price','pickup_estimate','capacity','base_price','base_minimum_price','cost_per_minute','cost_per_distance','distance_unit','cancellation_fee','currency_code','service_fees','service_fees_type','image','description','start_latitude','start_longitude','stop_latitude','stop_longitude','start_address','stop_address','product_id']]
        self._merge_display_names()
        self.df.to_csv('data/organized_uber_{}.csv'.format(filename.split('.')[0].split('_')[-1]), index=False)
        print "organized uber data to {}".format(filename.split('.')[0].split('_')[-1])
        return self.df

    def _merge_display_names(self):
        """
        Output: dataframe

        Merges slight variations of uber car types
        """
        print self.df['display_name'].value_counts()
        for city in self.df['city'].unique():
            print city, self.df.query("city == @city")['display_name'].unique()
        self.df['display_name'].replace(['UberBLACK','UberSUV','UberSELECT','uberT','Yellow WAV','ASSIST','PEDAL','For Hire','#UberTAHOE','uberCAB','WarmUpChi'],
                           ['uberBLACK','uberSUV','uberSELECT','uberTAXI','uberWAV','uberASSIST','uberPEDAL','uberTAXI','uberTAHOE','uberTAXI','uberWARMUP'], inplace=True)
        print self.df['display_name'].value_counts()
        for city in self.df['city'].unique():
            print city, self.df.query("city == @city")['display_name'].unique()

    def run_analysis(self):
        """
        Input: Cleaned dataframe
        Output: EDA plots
        """
        self.df['hour'] = self.df.record_time.dt.hour
        self.df['day'] = self.df.record_time.dt.day
        self.df['date'] = self.df.record_time.dt.date
        self.df['dayofweek'] = self.df.record_time.dt.dayofweek
        self.df['minute'] = self.df.record_time.dt.minute
        self.df.set_index('record_time', inplace=True)

        self.make_uberx_hours_den_plot()
        self.make_uberx_week_plot()
        self.plot_uberx_prices_cities()

    def make_uberx_hours_den_plot(self):
        """
        Output: EDA Plot
        """
        plt.cla()
        dates = ['2016-02-16','2016-02-17','2016-02-18','2016-02-19','2016-02-20','2016-02-21']
        dofwk = ['Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        for i,date in enumerate(dates):
            self.df[(self.df['display_name'] == 'uberX') & (self.df['city'] == 'denver')]. \
            ix[date].groupby('hour').mean()['avg_price_est'].plot(marker='o', figsize=(12,8), label='{} - {}'.format(date,dofwk[i]))
        plt.xlabel('Hour')
        plt.ylabel('Average Price')
        plt.axvline(8, ls='--', color='k', alpha=0.3)
        plt.legend(loc='best')
        plt.title('Fluctuation in UberX Pricing Within 24 Hours in Denver For a Week')
        plt.savefig('uberx_hours_denver.png')

    def make_uberx_week_plot(self):
        """
        Output: EDA Plot
        """
        plt.cla()
        dates = ['2016-02-16','2016-02-17','2016-02-18','2016-02-19','2016-02-20','2016-02-21']
        dofwk = ['Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        for i,date in enumerate(dates):
            self.df[(self.df['display_name'] == 'uberX') & (self.df['city'] == 'denver')]. \
            ix[date].groupby('hour').mean()['avg_price_est'].plot(marker='o', figsize=(12,8), label='{} - {}'.format(date,dofwk[i]))
        plt.xlabel('Hour')
        plt.ylabel('Average Price')
        plt.axvline(8, ls='--', color='k', alpha=0.3)
        plt.legend(loc='best')
        plt.title('Fluctuation in UberX Pricing Within 24 Hours in Denver For a Week')
        plt.savefig('uberx_denver_week.png')

    def plot_uberx_prices_cities(self):
        """
        Output: EDA Plot
        """
        plt.cla()
        for city in self.df['city'].unique():
            self.df[(self.df['display_name'] == 'uberX') & (self.df['city'] == city)].ix['2016-02-16G  ':'2016-02-19'].groupby('hour').mean()['avg_price_est'].plot(marker='o', figsize=(12,8), label='{}'.format(city))
        plt.xlabel('Hour')
        plt.ylabel('Average Price')
        # plt.axvline(8, ls='--', color='k', alpha=0.3)
        plt.legend(loc='best')
        plt.title('Fluctuation in UberX Pricing Within 24 Hours in Different Cities on Weekdays')
        plt.savefig('uberx_cities.png')

if __name__ == "__main__":
    filename = sys.argv[1]
    ua = UberAnalysis(filename=filename)
