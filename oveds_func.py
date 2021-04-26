#-------------------------------------------------------------------------------
# This file contains various COVID-19 data analysis and display functions
# Written by Oved Dahari on September 24, 2020.
# Version 1.7
# 'hue' removed from seaborn.lineplot (see row 101). 23-March-2021
#-------------------------------------------------------------------------

import pandas as pd
from datetime import datetime, timedelta
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
import oveds_accs as oda
    # this for plotting with x-axis as dates:
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

#------------------------------------------------
def print_5rows(df_all):
    """
    This function just prints the first 5 rows of the data,
    as well as various parameters of the DataFrame
    :param df_all: DataFrame
    :return: none
    """
    print('First 5 rows of the combined DataFrame:')
    print('---------------------------------------')
    print(df_all.head(5))
    print(df_all.dtypes)
    print(df_all.describe())


def plot_daily(df_all):
    """
    This method draws 2 plots: time-series of total and daily-change
    for a single parameter for a single country (or Province/State), chosen by the user
    :param df_all: DataFrame
    :return: None
    """
    country = oda.select_country(df_all)                        # select a country (or World)
    province = ''
    if country != 'World':
        province = oda.select_province(df_all, country)         # select a province/region

    option = oda.select_data(country)                           # select the data to display

    if country == 'World':
        w_df = df_all.groupby(['Date']).sum()
        if option == 'Death_Rate':
            w_df[option] = 100 * w_df['Deaths'] / w_df['Confirmed']
        y_data = list(w_df[option])                             # get the y-axis values from DF
        x_data = list(ind for ind in w_df.index)                # set x-axis data from dates
    else:
        if province == '':
            sub_df = df_all.loc[df_all['Country_Region'] == country].groupby(['Date', 'Country_Region']).sum()
        else:
            country_df = df_all.loc[(df_all['Country_Region'] == country) & (df_all['Province_State'] == province)]
            sub_df = country_df.groupby(['Date', 'Province_State']).sum()
        if option == 'Death_Rate':
            sub_df[option] = 100 * sub_df['Deaths'] / sub_df['Confirmed']
        y_data = list(sub_df[option])
        x_data = list(ind[0] for ind in sub_df.index)

    if option != 'Death_Rate':
        title = country + ' ' + province + ': Total ' + option + ' vs. time'
    else:
        title = country + ' ' + province + ' ' + option + ' vs. time (in %)'

    print('--- Close plot to continue ---')
    oda.oveds_plot(x_data, y_data, 'line', title)

        # now plot the daily-chnage data, averaged over 5 days
    if option != 'Death_Rate':
        x_data1 = x_data[3:-2]
        y_data2 = np.diff(y_data)
        filter = np.ones(5) * 0.2                               # delta function over 5 days (sum = 1)
        y_data = np.convolve(y_data2, filter)[4:-4]             # convolve to smooth the data
        title = country + ' ' + province + ': 5-day average of daily ' + option + ' vs. time'
        oda.oveds_plot(x_data1, y_data, 'line', title)

#------------------------------------------------
def plot_all4(df_all):
    """
    Plot time-series the data for a single country or the whole world
    :param df_all: DataFrame (all data)
    :return: None
    """
    country = oda.select_country(df_all)                        # select a country (or World)

        # build a dataframe with multi-index (date-country)
    if country == 'World':
        sub_df = df_all.groupby(['Date']).sum()
    else:
        sub_df = df_all.loc[df_all['Country_Region'] == country].groupby(['Date', 'Country_Region']).sum()

    names = ['Confirmed', 'Deaths', 'Recovered', 'Active']
    sub_df2 = sub_df[names]
    sub_df2.index = sub_df2.index.get_level_values(0)

                                                # plot with Seaborn
    # sb.lineplot(data=sub_df2, hue=names)
    sb.lineplot(data=sub_df2)
    plt.title(country + ': Total cases vs. time')
    plt.annotate('\xa9Oved_Dahari', (sub_df2.index[0], max(sub_df2['Confirmed'] * 0.1)))
    print('--- Close plot continue ---')
    plt.xticks(rotation = 30)
    plt.grid(True)
    plt.show()

#------------------------------------------------

def stats_for_all_over(df_all):
    """
    Makes plots of latest data for all countries with total death > input, for data selected by the user
    :param df_all: DataFrame (all data)
    :return: none
    """
    option = oda.select_data('all')                      # select the data for display

    inp_ok = False
    over = 0
    while not inp_ok:
        inp = input('Enter minimum number of deaths:')
        if inp.isnumeric():
            over = int(inp)
            inp_ok = True
        else:
            print('Try again...')

    latest = df_all['Date'].max()                                   # get the date of the latest data
    sub_df1 = df_all.loc[df_all['Date'] == latest]
    sub_df1a = sub_df1.copy()
    sub_df1a['Population'] = sub_df1['Confirmed'] / (sub_df1['Incidence_Rate'] * 10)  # produce a population column
    sub_df2 = sub_df1a.groupby(['Country_Region']).sum()               # group by country
    sub_df = sub_df2.loc[sub_df2['Deaths'] > over]                      # select only those with deaths > input

    print('--- Close plot continue ---')
    title = option + ' as of ' + latest.strftime('%d-%B-%Y') + ' (Deaths >' + str(over) +')'
    if option == 'Death_Rate':
        title = option + ' (in %) as of ' + latest.strftime('%d-%B-%Y') + ' (Deaths >' + str(over) + ')'
        sub_df1 = sub_df.copy()
        sub_df1[option] = 100* sub_df['Deaths'] / sub_df['Confirmed']
        sub_df = sub_df1.copy()

    oda.oveds_plot(sub_df.index, sub_df[option], 'bar', title)
                                          # plot the per-million data
    if option != 'Death_Rate':
        sub_df1 = sub_df.copy()
        # sub_df1['Population'] = sub_df['Confirmed'] / (sub_df['Incidence_Rate'] * 10)  # produce a population column
        sub_df3 = sub_df1[sub_df1['Population'].notnull()]
        title = option + ' per million, as of ' + latest.strftime('%d-%B-%Y') + ' (Deaths >' + str(over) + ')'
        hseries = sub_df3[option] / sub_df3['Population']
        oda.oveds_plot(sub_df3.index, hseries, 'bar', title)

#-------------------------------------------------------------------
def world_per_region(df_all):
    """
    Build a multi-index DF by Country and state/province, and print deaths and recovered
    :param df_all: DataFrame (all processed data)
    :return: none
    """
    latest = df_all['Date'].max()                       # get latest date
    print('\nCovid-19 data as of', latest.strftime("%d-%B-%y"), '\n')
    sub_df1 = df_all.loc[df_all['Date'] == latest]

        # build the MultiIndex dataframe
    sub_df = sub_df1.groupby(['Country_Region', 'Province_State']).sum()

        # set the display option to display all data
    pd.set_option('display.max_rows', sub_df.shape[0] + 1)

        # print the two columns (along with the indexes)
    print(sub_df[['Deaths', 'Recovered', 'Confirmed', 'Active']])

#-------------------------------------------------------------------
def by_province_region(df_all):
    """
    Plot selected data from the latest database for each province/state of input country
    :param df_all: DataFrame (all processed data)
    :return:
    """
    country = oda.select_country(df_all)
    option = oda.select_data(country)

    latest = df_all['Date'].max()                                               # get the date of the latest data
    sub_df1 = df_all.loc[df_all['Date'] == latest]
    sub_df1a = sub_df1.loc[sub_df1['Country_Region'] == country]
    sub_df1 = sub_df1a[sub_df1a['Province_State'].isin(['Recovered', 'Diamond Princess', 'Grand Princess']) == False]            # drop for the US
    sub_df1b = sub_df1.copy()
    sub_df1b['Population'] = sub_df1['Confirmed'] / (sub_df1['Incidence_Rate'] * 10)  # produce a population column
    sub_df = sub_df1b.groupby(['Province_State']).sum()                        # group by state

    title = option + ' for ' + country + ' as of ' + latest.strftime('%d-%B-%Y')
    if option == 'Death_Rate':
        title = option + ' (in %) for ' + country + ' as of ' + latest.strftime('%d-%B-%Y')
        sub_df1 = sub_df.copy()
        sub_df1[option] = 100* sub_df['Deaths'] / sub_df['Confirmed']
        sub_df = sub_df1.copy()

    print('--- close plot to continue ---')
    oda.oveds_plot(sub_df.index, sub_df[option], 'bar', title)

    if option != 'Death_Rate':
        title = option + ' per million for ' + country + ' as of ' + latest.strftime('%d-%B-%Y')
        sub_df3 = sub_df[sub_df['Population'].notnull()]
        hseries = sub_df3[option] / sub_df3['Population']
        oda.oveds_plot(sub_df3.index, hseries, 'bar', title)                        # plot the per-million data

#--------------------------------------------------------------------
def top_countries(df_all):
    """
    Plot top countries in a selected category: total, and per million
    :param myCovDF:
    :return: none
    """
    inp_ok = False
    top = 0
    while not inp_ok:
        inp = input('Enter number of top countries:')
        if inp.isnumeric():
            top = int(inp)
            inp_ok = True
        else:
            print('Try again...')

    option = oda.select_data('all')

    latest = df_all['Date'].max()                                   # get the date of the latest data
    sub_df1 = df_all.loc[df_all['Date'] == latest]
    sub_df1a = sub_df1.copy()
    sub_df1a['Population'] = sub_df1['Confirmed'] / (sub_df1['Incidence_Rate'] * 10)       # produce a population column
    sub_df2 = sub_df1a.groupby(['Country_Region']).sum()                                    # group by country

    title = option + ' for top-' + str(top) + ' countries, as of ' + latest.strftime('%d-%B-%Y')
    if option == 'Death_Rate':
        title = option + ' (in %) for top-' + str(top) + ' countries, as of ' + latest.strftime('%d-%B-%Y')
        sub_df1 = sub_df2.copy()
        sub_df1[option] = 100* sub_df2['Deaths'] / sub_df2['Confirmed']
        sub_df2 = sub_df1.copy()

    sub_df = sub_df2.sort_values(option, ascending=False).head(top)                        # sort and select top
    print(sub_df)

    print('--- close plots to continue ---')
    title = option + ' for top-' + str(top) + ' countries, as of ' + latest.strftime('%d-%B-%Y')

    oda.oveds_plot(sub_df.index, sub_df[option], 'bar', title)

    if option != 'Death_Rate':
        sub_df1 = sub_df2[sub_df2['Population'].notnull()]
        sub_df2 = sub_df1.copy()
        sub_df2['per_mil'] = sub_df1[option] / sub_df1['Population']
        sub_df = sub_df2.sort_values('per_mil', ascending = False).head(top)
        title = option + ' per million of top-' + str(top) + ' countries, as of ' + latest.strftime('%d-%B-%Y')
        oda.oveds_plot(sub_df.index, sub_df['per_mil'], 'bar', title)

#--------------------------------------------------------------------------------------
def no_recover(df_all):
    """
    Print data for countries with no recover cases.
    :param df_all: DataFrame (all data)
    :return: none
    """

    latest = df_all['Date'].max()                       # get latest date

    # print header
    print('\nCovid-19 data for countries with no recovered cases, as of', latest.strftime('%d-%B-%Y'), '\n')

    sub_df = df_all.loc[df_all['Date'] == latest].groupby(['Country_Region']).sum()         # sum over per country

        # find those with Recovered = 0
    no_rec = sub_df.loc[sub_df['Recovered'] == 0][['Confirmed', 'Deaths', 'Recovered', 'Active']]
    if len(no_rec) == 0:
        print('No counries found with number of recovered = 0')
    else:
        print(no_rec)                    # print data for these countries

#-----------------------------------------------------------------------
def all_died(df_all):
    """
    Print data for countries where all Confirmed cases died.
    :param df_all: DataFrame (all data)
    :return: none
    """

    latest = df_all['Date'].max()                       # get latest date

    # print header
    print('\nCovid-19 data for countries where all confirmed cases died, as of', latest.strftime('%d-%B-%Y'), '\n')

    sub_df = df_all.loc[df_all['Date'] == latest].groupby(['Country_Region']).sum()         # sum over per country

        # find those with Confirmed = Deaths
    all_dead = sub_df.loc[sub_df['Confirmed'] == sub_df['Deaths']][['Confirmed', 'Deaths', 'Recovered', 'Active']]

    if len(all_dead) == 0:
        print('No counries found with number of deaths = number of confirmed cases')
    else:
        print(all_dead)                    # print data for these countries

#-------------------------------------------------------------------
def all_recovered(df_all):
    """
    Print data for countries where all confirmed cases recovered.
    :param df_all: DataFrame (all data)
    :return: none
    """

    latest = df_all['Date'].max()                       # get latest date

    # print header
    print('\nCovid-19 data for countries where all confirmed cases recovered, as of', latest.strftime('%d-%B-%Y'), '\n')

    sub_df = df_all.loc[df_all['Date'] == latest].groupby(['Country_Region']).sum()         # sum over per country

        # find those with Confirmed = Deaths
    all_rec = sub_df.loc[sub_df['Confirmed'] == sub_df['Recovered']][['Confirmed', 'Deaths', 'Recovered', 'Active']]

    if len(all_rec) == 0:
        print('No counries found where all confirmed cases recovered')
    else:
        print(all_rec)                    # print data for these countries

#------------------------- main (for testing) ----------------------

def main():

    with open('cleaned_data.p', 'rb') as file:
        df_all = pickle.load(file)

    # plot_daily(df_all)
    # plot_all4(df_all)

    stats_for_all_over(df_all)
    # world_per_region(df_all)
    # by_province_region(df_all)
    # top_countries(df_all)
    # print_5rows(df_all)
    # no_recover(df_all)
    # all_died(df_all)
    # all_recovered(df_all)

if __name__ == '__main__':
    main()

#-------------- that's all, falks! ------------