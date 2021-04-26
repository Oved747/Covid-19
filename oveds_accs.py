#-------------------------------------------------------------------------------
# This library has some accessories for the Covid-19 package
# Written by Oved Dahari on Nov 7, 2020.
# Version 1.6a (corrected for NaN countries)
# Version 1.7 (23-March-2021): New name 'Incident_rate" converted to old 'Incidence_Rate'
#-------------------------------------------------------------------------
import pandas as pd
from datetime import datetime, timedelta, date
import pickle
import oveds_func as ovf
import matplotlib.pyplot as plt
import sys

def load_raw():
    """
    Read the latest COVID-19 data from the GitHub website, and dump to a file using pickle
    The program load only dates that have not been loaded before
    :return: Boolean (new data found)
    """
    cov_data_dict = {}
    today = datetime.today().date()
    # today = temp.('%m-%d-%Y')
    print('today =', today)

    try:
        with open('raw_data.p', 'rb') as file:
            cov_data_dict = pickle.load(file)                      # load from disk
        latest = max(cov_data_dict.keys()) + timedelta(1)           # the first date to load
        print('first date to load =', latest)
    except:
        # latest = datetime.strptime('22-01-2020', '%d-%m-%Y')        # start at 22-Jan-20
        latest = date(2020, 1, 22)
        print('Starting from: ', latest)
        # cov_data_dict = {}

    mypath = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/' \
            'csse_covid_19_daily_reports/'

    cov_df = pd.DataFrame()
    nfound = 0

#    while latest != datetime.today().date():               # load up to yesterday
    while latest != today:  # load up to yesterday
        print('latest =', latest)
        try:
            date_name = latest.strftime('%m-%d-%Y') + '.csv'
            cov_df = pd.read_csv(mypath + date_name)
            cov_data_dict[latest] = cov_df                  # add to dictionary
            print('found:', latest)
            latest += timedelta(1)
            nfound += 1
        except:
            print('last found:', latest)

    ndates = len(cov_data_dict)
    print('Total dates:', ndates, ', found new:', nfound)
    if nfound > 0:
        #print(sorted(cov_data_dict.keys()))
        with open('raw_data.p', 'wb') as file:                  # dump to a pickle file
            pickle.dump(cov_data_dict, file)
        return True
    else:
        return False

#---------------------------------------------------

def clean_data():
    """
    Read to raw data from (pickle) file, than "clean it" and
    combine all data to a single unified dataFrame
    :return: None
    """
    with open('raw_data.p', 'rb') as file:                                      # read from file
        df_dict = pickle.load(file)


#    for col in df_dict.columns:
#        print(col)
#     print(df_dict.columns)
# clist = sorted(list(pd.unique(df_dict['Country/Region'])))
# for item in clist:
       #  print(item)

    # sys.exit()

    column_dict = {'Province/State': 'Province_State',                          # columns with multiple names
                'Country/Region': 'Country_Region',
                'Last Update': 'Last_Update',
                'Long_': 'Longitude',
                'Lat': 'Latitude',
                'Incident_Rate': 'Incidence_Rate'
                }

    country_dict = {'Bahamas, The': 'Bahamas',                                  # countries with multiple names
                    'The Bahamas': 'Bahamas',
                    'Gambia, The': 'Gambia',
                    'Hong Kong SAR': 'Hong Kong',
                    'Iran (Islamic Republic of)': 'Iran',
                    'Macao SAR': 'Macao',
                    'Mainland China': 'China',
                    'Republic of Ireland': 'Ireland',
                    'Republic of Korea': 'South Korea',
                    'Korea, South': 'South Korea',
                    'Republic of Moldova': 'Moldova',
                    'Republic of the Congo': 'Congo',
                    'Russian Federation': 'Russia',
                    'Saint Martin:': 'St. Martin',
                    'The Gambia': 'Gambia',
                    'Taiwan*': 'Taiwan',
                    'United Kingdom': 'UK',
                    'Holy See': 'Vatican City',
                    'Viet Nam': 'Vietnam',
                    'occupied Palestinian territory': 'Palestine',
                    ' Azerbaijan': 'Azerbaijan',
                    'West Bank and Gaza': 'Palestine',
                    'Taipei and environs': 'Taiwan',
                    'Congo (Brazzaville)': 'Congo',
                    'Congo (Kinshasa)': 'Congo',
                    'Cabo Verde': 'Cape Verde',
                    'Czechia': 'Czech Republic',
                    'Timor-Leste': 'East Timor'
                    }

    df_list = []
    for the_date in df_dict:                                                    # clean the data
        tdf = df_dict[the_date]
        tdf.rename(columns = column_dict, inplace = True)                       # rename column names to current
        tdf['Country_Region'] = tdf['Country_Region'].replace(country_dict)     # update country names
        tdf['Date'] = [the_date for ii in range(tdf.shape[0])]                  # add a column of the date
        tdf2 = tdf[tdf['Country_Region'].notna()]                               # drop when country == None
        df_list.append(tdf2)

    comb = pd.concat(df_list, sort = True)                                      # create a single DataFrame

    cruise_ships = ['Cruise Ship', 'Diamond Princess', 'MS Zaandam']
    comb1 =  comb[comb['Country_Region'].isin(cruise_ships) == False]           # drop the cruise ships, and 'Others'

    proc_df = comb1[['Country_Region', 'Province_State', 'Admin2',               # use only relevant colummns
                    'Confirmed', 'Deaths', 'Recovered', 'Active', 'Case-Fatality_Ratio',
                    'Incidence_Rate', 'Date', 'Latitude', 'Longitude']]

    with open('cleaned_data.p', 'wb') as file:                                  # write to a pickle file
        pickle.dump(proc_df, file)

#------------------------------------------------------------------
def select_data(country):
    """
    Present the names of the 4 data columns, and return the selected option
    :param: country: string
    :return: string (option chosen)
    """
    options = {'1': 'Confirmed', '2': 'Deaths', '3': 'Death_Rate', '4': 'Recovered', '5': 'Active'}
    valid = False
    chosen = ''
    while not valid:
        if country == 'US':
            print('Available data options:\n',
                  '-----------------------\n',
                  '1: Confirmed\n',
                  '2: Deaths\n',
                  '3: Death Rate\n')
        else:
            print('Available data options:\n',
                  '-----------------------\n',
                  '1: Confirmed\n',
                  '2: Deaths\n',
                  '3: Death_Rate\n '
                  '4: Recovered\n',
                  '5: Active\n',
                  )

        chosen = input('Choose an option: ')

        if country == 'US':
            poss = '1 2 3'.split(' ')
        else:
            poss = '1 2 3 4 5'.split(' ')

        if chosen in poss:
            valid = True
        else:
            print('select a proper number...')

    return options[chosen]

def exit_option(df_all):
    sys.exit()

#-----------------------------------------------------------------

def select_option():
    """
    Select an option of data plot/print
    :return: String (function to be performed)
    """
    opt_dict = {'0': exit_option, '1': ovf.plot_daily, '2': ovf.plot_all4, '3': ovf.stats_for_all_over,
                '4': ovf.world_per_region, '5': ovf.by_province_region, '6': ovf.top_countries, '7': ovf.print_5rows,
                '8': ovf.no_recover, '9': ovf.all_died, '10': ovf.all_recovered}

    print('\n The options in this program are::\n',
          ' -----------------------------------\n',
          '0: exit\n',
          '1: Plot Time-series of selected country/province/datay or the World (Total and Daily)\n',
          '2: Plot time-series of all data for a single-country (on a single plot)\n',
          '3: Plot selected data (total and per million) for all countries with total deaths > selected\n',
          '4: Print Confirmed and Deaths for all world regions/states\n',
          '5: Plot selected latest data for all states/regions in a country\n',
          '6: Plot top countries in selected latest data (total, and per million)\n',
          '7: Print the first 5 rows of the data, along with various parameters\n',
          '8: Print data for countries with no Recovered cases\n',
          '9: Print data for countries where all Confirmed cases died\n',
          '10: Print countries where all confirmed cases recovered\n',
          )
    while True:
        inp = input('Enter option number:')
        if inp.isnumeric() and int(inp) < 11:
            return opt_dict[inp]
        else:
            print('Try again...')

#-----------------------------------------------------------------------------
def select_country(df_all):
    """
    Returns a country (or the whole World) selected by the user
    :param: DataFrame (the whole data)
    :return: string (country name)
    """
    country = ''
    while True:
        clist = sorted(list(pd.unique(df_all['Country_Region'])))
        country = input('Enter country name, or World (all --> print list):')
        if country == 'all':
            for cc in clist:
                print(cc)
        elif country in clist or country == 'World':
            return country
        else:
            print('try again...')

def select_province(df_all, country):
    """
    Select a province/state for a given country
    :param df_all: DataFrame (all data)
    :param country: String
    :return: String
    """
    # province = ''
    latest = df_all['Date'].max()
    tdf = df_all.loc[df_all['Country_Region'] == country]
    prov_df = tdf.loc[tdf['Date'] == latest].groupby(['Province_State']).sum()
    prov_list = sorted(list(prov_df.index))
    print('Province/State list for ' + country + ':')
    print('----------------------------------')
    prov_dict = {}
    for ii in range(1, len(prov_list) +1):
        prov_dict[str(ii)] = prov_list[ii-1]
    for ii in prov_dict:
        print(ii, prov_dict[ii])

    found = False
    sel = ''
    while not found:
        sel = input('Select a province/state by number (or <CR> for the whole country):')
        if sel == '':
            return ''             # return empty string
        if sel.isnumeric() and int(sel) < len(prov_list) + 1:
            found = True
        else:
            print('try again...')
    return prov_dict[sel]

#----------------------------------------------------------------------------------

import matplotlib.dates as mdates
def oveds_plot(x_data, y_data, typ, title):
    """
    Plot the data, with various inputs
    :param x_data: DF series or numpy array
    :param y_data: same
    :param typ: string
    :param title: string
    :return: none
    """
    if typ == 'line':                                                       # plot a simple graph
        plt.title(title)
        plt.plot(x_data, y_data)
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%B-%d'))      # set x-axis ticks
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=14))
        plt.xticks(rotation = 30)

    elif typ == 'bar':
        fig, ax = plt.subplots()                                           # plot a bar-plot
        ax.set_title(title)
        ax.bar(x = x_data, height = y_data)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")             # make the x-axis tick labels readable
        plt.grid(True, axis = 'y')                                          # plot horizontal grid

    else:
        print('Plot type invalid')
        return

    plt.annotate('\xa9Oved_Dahari', (x_data[0], max(y_data) * 0.95))        # enter logo
    plt.show()

#-------------------------------- main (for testing) -------------------------

def main():

    # with open('cleaned_data.p', 'rb') as file:
    #    df_all = pickle.load(file)                                    # load from disk

#     print('Today =', make_GH_date(0))
#     print('Yesterday =', make_GH_date(1))
    # print('You selected option', select_option())
    # load_raw()
    clean_data()
    # print(select_province(df_all, 'Canada'))

if __name__ == '__main__':
    main()
