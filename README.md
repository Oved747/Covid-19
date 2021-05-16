Covid_19

This Python 3 project imports raw Covid statistics daily data from GitHub, arrange it in daily DataFrames, and combine all data in 
a large (160MB, as of April 26, 2021) DataFrame.

The program then anables the user to plot statistics for any country/region. Some print options are also available.

(This project was an exercise in the Data Scientist course at John Bryce academy (Tel Aviv, Israel), lasted from Nov-2019 to Jan-2021.)
 
The program includes three Python files: oveds_main, oveds_acc.py, and oveds_func.py.

To run the program, use Python and run oveds_main.py. Allow the program to upload and process all 
data from GitHub. It will store two files on your frame: raw_data.p and cleaned_data.p.
On your next run, it will just update these files with new data (since your last run).
