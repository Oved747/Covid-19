#---------------------------------------------------------------------
# This file is the file to run for the Covid-19 project of the JB course
# Written by Oved Dahari, September 24, 2020
# Version 1.6, adapted to Python 3.8 (and Anaconda 2020.2), with modifications for Pandas
# Version 1.7 (small correction in oved_func). 23-March-2021
#---------------------------------------------------------------------

import oveds_accs as acc
import pickle

print('Welcome. You are running Covid-19 data analysis,\nversion 1.7 \xa9Oved_Dahari\n')

new = acc.load_raw()

if new:
    acc.clean_data()

with open('cleaned_data.p', 'rb') as file:
    myDF = pickle.load(file)                                    # load from disk
print('First 10 Confirmed:', myDF['Confirmed'].head(10))
print('First 10 Incidence_Rate:', myDF['Incidence_Rate'].head(10))

option = ''
while option != '0':
    acc.select_option()(myDF)                   # select an option and run it, until 'exit' is selected

#---------- the End -----------------