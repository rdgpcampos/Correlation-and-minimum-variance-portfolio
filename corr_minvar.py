#!/usr/bin python

import yfinance as yf
from csv import reader
import argparse
import os
import sys
import pandas
fpath = os.path.join(os.path.dirname(__file__),'header')
sys.path.append(fpath)
import stock_analysis as sa


#------- Read input csv file ---------

# Parse command line for input file, output file and target average returns
parser = argparse.ArgumentParser(
    description='Read necessary inputs for portfolio choice.'
)

parser.add_argument(
    'input_file',
    metavar = 'Stocks.csv',
    help = 'Input csv file containing stock tickers in the first column'
)
parser.add_argument(
    'target_return',type = float,
    nargs='?', metavar = 't',
    help = 'Desired average yearly return'
)
parser.add_argument(
    '-span',
    nargs = 2,
    default = ['2010','2020'],
    metavar = 'Year',
    help = 'Year span for the data gathering'
) 
parser.add_argument(
    '-max_stock_price',
    nargs = '?',
    type = float,
    default = 100.0,
    const = 100.0,
    metavar = 'P',
    help = 'Maximum price of stock'
)
parser.add_argument(
    '-o_avg',
    nargs = '?',
    choices = ['True', 'False'],
    default = 'False',
    metavar = 'True/False',
    help = 'Output average yearly return for stock data'
)
parser.add_argument(
    '-o_var',
    nargs = '?',
    choices = ['True', 'False'],
    default = 'False',
    metavar = 'True/False',
    help = 'Output standard deviation for stock data'
)


args = parser.parse_args()
ifile = args.input_file
ofile1 = 'Portfolio.txt'
ofile2 = 'Correlation.txt'
t_avg = args.target_return
initial_year = args.span[0]
final_year = args.span[1]
max_price = args.max_stock_price
avg_output_flag = args.o_avg
var_output_flag = args.o_var


# ticker list used to read stock data from yahoo finances
ticker_strings = []

# append ticker data from input file to ticker_strings
# input file has to be a csv file with a one-line header
with open(ifile, 'r') as read_obj:
    csv_reader = reader(read_obj)
    # skip header
    next(csv_reader,None)
    for row in csv_reader:
        ticker_strings.append(row[0])

# yahoo finances input
ticker_s = ""
for ticker in ticker_strings:
    ticker_s = ticker_s+ticker+" "
# remove last spacebar
ticker_s = ticker_s[:-1]

# get data from yahoo finance + pre-processing
initial_year = initial_year + "-01-02"
final_year = final_year + "-01-01"

# check whether stock list and period are stored in a cached file
# this is done by opening a catalogue text file which contains the 
# (1) initial year, final year, and stock tickers (order matters), 
# and the (2) name of the cache file containing the (pickled) stock data
cache = {}
with open("./savefiles/catalogue.txt",'r+') as cache_file:
    for line in cache_file:
        key, value = str(line.split(':::::')[0]),\
                        str(line.split(':::::')[1][:-1])
        cache[key] = value

input_string = initial_year+","+final_year+","+ticker_s
if cache.get(input_string) is None:
    # download stock data and write it in a cache file for future use
    data_pre = yf.download(
                ticker_s,
                start=initial_year,
                end=final_year,
                group_by="ticker"
                )
    catalogue = "./savefiles/catalogue.txt"
    with open(catalogue,'a') as cache_file:
        cache_file.write(input_string+':::::'
                         +'./savefiles/'
                         +str(len(cache)).zfill(10)+'.pkl'+'\n')
    data_pre.to_pickle("./savefiles/"+str(len(cache)).zfill(10)+".pkl")
else:
    # read cache file
    data_pre = pandas.read_pickle(cache[input_string])

# convert index to column in dataframe
data = data_pre.reset_index()

# get initial year
year_old = data['Date'][0].year 

# remove unnecessary days from dataframe
for i, date in enumerate(data['Date'][1:]):
    if date.year == year_old:
        data = data.drop(index=[i+1])
    else:
        year_old = date.year

#------------ Get measures from data -------------

# List that will gather all relevant data regarding each stock
stock_list = []

# Remove expensive stocks and get returns from closing price data

returns = sa.get_returns(data, ticker_strings, stock_list, max_price)

# Get average yearly returns

avg_returns =  sa.stock_average( returns, stock_list, t_avg )

if avg_output_flag == 'True':
    print("---------- Average yearly return ---------")
    for i in range(len(returns)):
        print(stock_list[i].ticker,": ",stock_list[i].mean)

# Get variance

sa.stock_variance( returns, stock_list )
    
if var_output_flag == 'True':
    print("---------- Average variance ---------")
    for i in range(len(returns)):
        print(stock_list[i].ticker,": ",stock_list[i].variance)

print("variance of portfolio: ",
      sa.portfolio_minvar_MC(stock_list, t_avg, returns))

sa.plot_portfolio(stock_list, "hbar", ofile1)
portfolio_corr = sa.plot_corr(stock_list, returns, ofile2)



#print('--------------- Portfolio average ---------------')
#print(np.dot(minvar_port,np.reshape(avg_returns, (len(stock_list),1)))[0][0]/100)

#ind = np.argpartition(minvar_port,-10)[-10:]
#for index in ind:
#    print("Indexation in dictionary: {}, Weight in portfolio: {}".format(index,minvar_port[index]))
    
#with open('portfolio_data.txt','w') as f:
#    print(portfolio, file=f)

#with open('minvar_portfolio.txt','w') as f:
#    print(minvar_port, file=f)
    
