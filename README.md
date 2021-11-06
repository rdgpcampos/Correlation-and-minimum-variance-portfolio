# Correlation-and-minimum-variance-portfolio
This application is meant to help retail investors guide their portfolio building decisions
It performs two jobs:
  (1) Calculate and output the correlation between input stocks
  (2) Output the minimum variance portfolio for a given target average yearly return
The application achieves this by extracting the closing price of each input stock from yahoo finances
using the yfinance package by Ran Aroussi. From the closing price data, corr_minvar.py extracts the
average yearly returns and variance of each input stock, as well as the correlation among these.
It then builds an optimum portfolio using the extracted data, given a target yearly average return.

To use the application, simply type
$ python corr_minvar.py Stocks.csv [t]
in the application's main directory, where Stocks.csv is an input file containing the tickers of all
input stocks. This input file must be of the following format:
---header---
ticker1,...
ticker2,...
ticker3,...
...

The following optional arguments can also be provided:
-span initial_year final_year ........ Initial and final years from which data will be collected (default: 2010 2020)
-max_stock_price P ................... Set maximum price for a stock to be included in the analysis (default: 100.0)
-o_avg True/False .................... Output average yearly return of each stock (default: False)
-o_var True/False .................... Output variance of each stock (default: False)

The data downloaded from yahoo finances is stored in savefiles as a pickled file. That way, as long as
the same tickers (order matters) and span are used, the data will not need to be downloaded again.
For a long list of tickers, such as the S&P500, this can save some time. 

The header/stock_analysis.py module contains the Stock class and the essential functions used by
corr_minvar.py, which are all listed below:

- Stock (class):
  Defines a Stock object with the ticker, mean, variance, and position properties.
  
- get_returns (function):
  Creates a Stock object for each input ticker with last closing price below the value set by -max_stock_price.
  Returns a 2d list containing the daily return of each input stock in the given span.
  
- stock_average (function):
  Sets a value for the mean property of each Stock object.
  It also removes from the analysis any Stock object containing an yearly average return that is nan (lack of data),
  too high or too low (yearly average return 10% above or below the target yearly average return)
  
- stock_variance (function):
  Sets a value for the variance property of each Stock object.
  
- get_covar (function):
  Outputs a 2d list describing the covariance matrix of the Stock objects.
  
- normalize (function):
  Normalize an input vector.
  
- portfolio_minvar_MC (function):
  Finds the positions in each stock in a portfolio constituted by the Stock objects such that the portfolio variance is
  minimum and the average yearly return is equal to the target value. It does so by, first, generating a portfolio with
  average yearly return equal to the target value, and then it repeatedly attempts a small change in the portfolio
  (without changing the portfolio return) and checks whether this change reduces the variance or not. The small change will
  only be accepted and modify the portfolio if it reduces the portfolio variance. Eventually, this process will converge to
  the minimum variance portfolio. The following constraints were assumed during this optimization procedure: the total sum
  of the positions must be 1; the value of each position must be non-negative; the return of the portfolio must remain
  constant. I will include a demonstration for this procedure in the future (just have to write it on latex or smth).
  
- portfolio_minvar_sd (function):
  I tried using a steepest descent optimization algorithm, but I had trouble keeping the portfolio return constant with
  this approach so I dropped it. I might return to it so I left the function in the stock_analysis.py file just in case.
  
- plot_portfolio (function):
  Plots the minimum variance portfolio as a horizontal bar graph and also outputs a csv file named Portfolio.csv.
  
- plot_corr (function):
  Plots the correlation between the Stock objects as a heatmap using the corrplot module by Drazen Zaric.
  
I welcome any comments and ideas regarding this project :)
