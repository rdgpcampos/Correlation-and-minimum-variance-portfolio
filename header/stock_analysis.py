import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import math
from heatmap import corrplot

class Stock:
    def __init__(self, ticker: str, mean: np.float64, variance: float, 
                 position: float):
        self.ticker = ticker
        self.mean = mean
        self.variance = variance
        self.position = position
      
    def __str__(self):
        return "{}: Mean = {}, Variance = {}, Position = {}".format(
            self.ticker,str(self.mean),str(self.variance),str(self.position))

    def __repr__(self):
        return "{}: Mean = {}, Variance = {}, Position = {}".format(
            self.ticker,str(self.mean),str(self.variance),str(self.position))


def get_returns( data: pd.DataFrame , ticker_strings: list , 
                stock_list: list, max_price: float):

    returns = []
    
    i = 0
    for ticker in ticker_strings:
        if data[ticker]['Close'].iloc[-1] > max_price:
            continue # Remove expensive stocks
        # if all values are nan, skip
        all_nan = 1
        for price in data[ticker]['Close']:
            if not math.isnan(price):
                all_nan *= 0
        if all_nan == 1:
            continue
        stock_list.append(Stock(ticker, 0.0, 0.0, 0.0))
        returns.append([])
        closing_price_old = data[ticker]['Close'][0]
        for closing_price_curr in data[ticker]['Close'][1:]:
            returns[i].append((closing_price_curr - closing_price_old)
                              /closing_price_old)
            closing_price_old = closing_price_curr 
        i+=1

    return returns


def stock_average( returns: list, stock_list: list, t_avg: float ):
    
    tmp_returns = []
    tmp_mean = 0.0
    tmp_pymean = 0.0
    for stock in returns:
        tmp_returns.append(stock)

    j = 0    
    for stock in tmp_returns:
        tmp_mean = np.nanmean(stock,dtype = np.float64)*100.0
        tmp_pymean = tmp_mean.item()
        if (not math.isnan(tmp_mean) 
                and tmp_pymean>t_avg-10.0 
                and tmp_pymean<t_avg+10.0):
            stock_list[j].mean = tmp_mean
            j += 1
        else:
            returns.pop(j)
            stock_list.pop(j)

    return 0

def stock_variance( returns: list, stock_list: list ):

    for i,stock in enumerate(returns):
        stock_list[i].variance = np.nanvar(stock,ddof = 1)*100

    return 0

# Get covariance matrix of stocks contained in portfolio
def get_covar( returns: list, stock_list: list ):

    portfolio_cov = []

    for i,e1 in enumerate(stock_list):
        portfolio_cov.append([])
        for j,e2 in enumerate(stock_list):
            cov = 0
            length = len(returns[i])
            for k in range(length):
                if math.isnan(returns[i][k]) or math.isnan(returns[j][k]):
                    length -= 1
                    continue
                cov += (returns[i][k] - e1.mean/100)*(returns[j][k] 
                                                      - e2.mean/100)
            if length > 1:
                cov /= length - 1
            else:
                cov = 0 # Assuming that no data for covariance implies 
                        # no correlation
            portfolio_cov[i].append(cov*100)
    
    return portfolio_cov
    
# normalize 1d vector input
def normalize( a, order=1, axis=-1 ):
    l1 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l1[l1==0] = 1
    return a / np.expand_dims(l1, axis)

# Get minimum variance portfolio by iterating over it with a
# Monte Carlo process
def portfolio_minvar_MC( stock_list: list, t_avg: float, returns: list ):
    portfolio_cov = get_covar(returns, stock_list)
    length = len(portfolio_cov)
    # Percentage of portfolio attributed to each stock    
    position = []

    # Setup initial position
    n_plus = 0
    n_minus = 0
    flag = -1
    delta = []

    for i,stock in enumerate(stock_list):

        delta_curr = stock.mean - t_avg
        
        if delta_curr > 0:
            n_plus += 1
            delta.append(1/delta_curr)
            continue
        if delta_curr < 0:
            n_minus += 1
            delta.append(1/delta_curr)
            continue
        if delta_curr == 0:
            flag = i
            break
    
    if flag == -1:
        for i in range(length):
            if delta[i] > 0:
                position.append(delta[i]/n_plus)
            else:
                position.append(-delta[i]/n_minus)
    else:
        for i in range(length):
            if i != flag:
                position.append(0)
            else:
                position.append(1)
    
    position = normalize(position)[0]
    
    sorted_list = []
    for i in range(len(portfolio_cov)):
        sorted_list.append(i)

    # MC run
    for i in range(100000):
        shift = random.sample(sorted_list,3)
            
        a = np.zeros((1,len(portfolio_cov)))[0]
        
        # Each step is such that the portfolio average return remains constant
        step_length = random.random()/1000
        a[shift[0]] = step_length
        a[shift[1]] = step_length/((stock_list[shift[1]].mean
                                    -stock_list[shift[0]].mean)
                                    /(stock_list[shift[2]].mean
                                    -stock_list[shift[0]].mean)-1)
        a[shift[2]] = -a[shift[0]]-a[shift[1]]

        # ensure all values are positive
        if np.amin(np.add(position,a)) < 0.0:
            continue
        # Accept change if variance decreases;
        change = np.matmul(np.matmul(a,portfolio_cov), 
                           np.transpose(np.add(np.multiply(position,2),a)))
        if np.sum(change) < 0.0: 
            position = position + a

    # Output recommended position
    for i,stock in enumerate(stock_list):
        stock.position = position[i]*100
        
    # Calculate variance of portfolio
    portfolio_var = 0.0
    for i,stock1 in enumerate(stock_list):
        portfolio_var += stock1.variance*position[i]*position[i]
        for j,stock2 in enumerate(stock_list):
            if i != j:
                portfolio_var += portfolio_cov[i][j]*position[i]*position[j]    
    
    return portfolio_var

def portfolio_minvar_sd( stock_list: list, t_avg: float, returns: list ):
    portfolio_cov = get_covar(returns, stock_list)
    length = len(portfolio_cov)
    # Percentage of portfolio attributed to each stock    
    position = []

    # Setup initial position
    n_plus = 0
    n_minus = 0
    flag = -1
    delta = []

    for i,stock in enumerate(stock_list):

        delta_curr = stock.mean - t_avg
        
        if delta_curr > 0:
            n_plus += 1
            delta.append(1/delta_curr)
            continue
        if delta_curr < 0:
            n_minus += 1
            delta.append(1/delta_curr)
            continue
        if delta_curr == 0:
            flag = i
            break
    
    if flag == -1:
        for i in range(length):
            if delta[i] > 0:
                position.append(delta[i]/n_plus)
            else:
                position.append(-delta[i]/n_minus)
    else:
        for i in range(length):
            if i != flag:
                position.append(0)
            else:
                position.append(1)
    
    position = normalize(position)[0]
    mean_0 = [x.mean for x in stock_list]
    mean = normalize(mean_0)[0]
    p_old = p_curr = position
    err = 100.0
    alpha = 0.1
    n_attempts = 0
    while (err > 0.000001):
        print("Average: ",np.dot(mean_0,np.transpose(position)))
        p_old = position
        res = -np.matmul(portfolio_cov,np.transpose(position))
        a = np.subtract(res,np.dot(mean,res)*mean)
        alpha = (np.matmul(res,np.transpose(res))
                 /np.matmul(res,np.matmul(portfolio_cov,np.transpose(res))))
        print(alpha)
        position = normalize(position + a*alpha)[0]
        p_curr = position
        err = np.amax(np.abs(np.add(p_curr,- p_old)))
        n_attempts += 1
        if n_attempts > 1000:
            break
        
    for i,stock in enumerate(stock_list):
        stock.position = position[i]*100
        
    portfolio_var = 0.0
    for i,stock1 in enumerate(stock_list):
        portfolio_var += stock1.variance*position[i]*position[i]
        for j,stock2 in enumerate(stock_list):
            if i != j:
                portfolio_var += portfolio_cov[i][j]*position[i]*position[j]    

    print("Average: ",np.dot(mean_0,np.transpose(position)))
    
    return portfolio_var
    
def plot_portfolio( stock_list: list, plot_flag: str, ofile: str ):
    plt.rcdefaults()
    fig, ax = plt.subplots()
    
    stock_names = [stock.ticker for stock in stock_list]
    positions = [stock.position for stock in stock_list]
    stock_names_sorted = [x for y,x in sorted(zip(positions,stock_names))]
    positions_sorted = sorted(positions)[::-1]
    stock_names_sorted = stock_names_sorted[::-1]
    
    # removing from plot stocks with too low position
    plot_pos = []
    plot_names = []
    
    for i,pos in enumerate(positions_sorted):
        if pos < 1.0:
            break
        plot_pos.append(pos)
        plot_names.append(stock_names_sorted[i])
    
    y_pos = np.arange(len(plot_names))    
    if plot_flag == "hbar":
        ax.barh(y_pos, plot_pos, align='center')
        ax.set_axisbelow(True)
        ax.grid(axis='x')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(plot_names, fontsize=10)
        ax.invert_yaxis()
        ax.set_xlabel('Position')
        ax.set_title('Recommended position in each stock')
        
    if plot_flag == "pie":
        print('Are you sure you want a pie plot? ',
              'There likely are better ways to plot data.')
        confirmation = input('y/n?')
        if confirmation == 'n':
            plot_portfolio(stock_list, "hbar")
        elif confirmation != 'y':
            print('Please input "y" or "n".')
        ax.pie(plot_pos,labels=plot_names,autopct='%1.1f%%',startangle=90)
        ax.axis('equal')

    stock_data = []
    for i,stock in enumerate(stock_list):
        stock_data.append([])
        stock_data[i].append(stock.mean)
        stock_data[i].append(stock.variance)
        stock_data[i].append(stock.position)
    
    df_stock = pd.DataFrame(stock_data,index=stock_names)

    with open(ofile,'w') as output_file:
        df_stock.to_csv(output_file)

    plt.show()

def plot_corr( stock_list: list, returns: list, ofile: str):
    # get covariance data
    portfolio_cov = get_covar(returns, stock_list)

    # get correlation from covariance data
    portfolio_corr = []
    
    for i,row in enumerate(portfolio_cov):
        portfolio_corr.append([])
        for j,cov in enumerate(row):
            corr = cov/math.sqrt(stock_list[i].variance
                                 * stock_list[j].variance)
            portfolio_corr[i].append(corr)
    
    stock_names = [stock.ticker for stock in stock_list]
    df_corr = pd.DataFrame(portfolio_corr,columns=stock_names,
                           index=stock_names)
    # output to file
    with open(ofile,'w') as output_file:
        df_corr.to_csv(output_file,columns=stock_names)
    
    # plot (nice) heatmap
    corrplot(df_corr, size_scale=1800/len(stock_list))
    
    return portfolio_corr
