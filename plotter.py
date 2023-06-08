import numpy as np

from enum import Enum

class Index(Enum):
    NASDAQ = ('^NDX', 'TQQQ', 'SQQQ')
    SP500 = ('^GSPC', 'UPRO', 'SPXU')
    DJIA = ('^DJI', 'UDOW', 'SDOW')
    RUSSELL2000 = ('^RUT', 'URTY', 'SRTY')


def backtest_strategy(start_date: str, end_date: str, index: Index, ideal_stop_loss: float=None):
    # Download historical data
    index_data = yf.download(index.value[0], start=start_date, end=end_date)['Close']
    leveraged_etf_data = yf.download(index.value[1], start=start_date, end=end_date)[['Close', 'Open']]
    inverse_leveraged_etf_data = yf.download(index.value[2], start=start_date, end=end_date)[['Close', 'Open']]

    # Initialize portfolio with cash only
    portfolio = [1.0]
    position = None  # can be 'Long' or 'Short'

    # Use the degree of freedom for the t-distribution, typically a small integer value
    df = 3

    # Iterate over each day in the data
    for i in range(1, len(index_data)):
        # Sell position at the end of the day if we have one
        if position is not None:
            # Compute the day's return
            prev_close = leveraged_etf_data['Close'][i-1] if position == 'Long' else inverse_leveraged_etf_data['Close'][i-1]
            open_price = leveraged_etf_data['Open'][i] if position == 'Long' else inverse_leveraged_etf_data['Open'][i]
            close_price = leveraged_etf_data['Close'][i] if position == 'Long' else inverse_leveraged_etf_data['Close'][i]

            # Randomize the actual stop loss around the ideal stop loss using a Student's t-distribution
            if ideal_stop_loss is not None:
                actual_stop_loss = ideal_stop_loss + np.random.standard_t(df) * 0.01
                if actual_stop_loss < ideal_stop_loss: 
                    actual_stop_loss = ideal_stop_loss 

                if open_price < prev_close * (1 - actual_stop_loss):
                    daily_return = open_price / prev_close
                elif close_price / prev_close < (1 - actual_stop_loss):
                    daily_return = (1 - actual_stop_loss)
                else:
                    daily_return = close_price / prev_close
            else:
                daily_return = close_price / prev_close

            # Update portfolio
            portfolio_value = portfolio[-1] * daily_return

            # Sell position
            position = None
        else:
            portfolio_value = portfolio[-1]

        # Determine whether to buy TQQQ or SQQQ based on whether NASDAQ Composite went up or down
        if index_data[i] < index_data[i-1]:
            position = 'Long'
        else:
            position = 'Short'
        
        portfolio.append(portfolio_value)

    # Convert the list of portfolio values to a pandas Series with the same index as the price data
    portfolio_series = pd.Series(portfolio, index=index_data.index)

    return portfolio_series


stop_losses = [0.01, 0.02, 0.05, 0.1, None]
portfolio_values = []
indexes = [Index.NASDAQ, Index.SP500, Index.DJIA, Index.RUSSELL2000]

# Set the figure size: (width, height)
plt.figure(figsize=(20, 20))  # increased size for better visibility
plt.subplots_adjust(hspace=0.3)  # adjust spacing between plots

for i, index in enumerate(indexes, start=1):
    plt.subplot(4, 1, i)
    plt.grid(True)

    # Run backtest for each stop loss level and plot the portfolio values
    for stop_loss in stop_losses:
        portfolio = backtest_strategy('2022-01-01', '2023-06-01', index, stop_loss)
        portfolio_values.append(portfolio)
        plt.plot(portfolio.index, portfolio, label=f'Stop loss: {stop_loss if stop_loss else "None"}')  # note the .index here
    
    plt.title(f'Portfolio Value Over Time for {index.name} from 2022-01-01 to 2023-06-01 \nInitial portfolio value: $1')
    plt.xlabel('Time')
    plt.ylabel('Portfolio Value')
    plt.legend()

    # Format x-axis to show dates in 'YYYY-MM-DD' format
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())  # to locate year intervals
    plt.gcf().autofmt_xdate()  # to rotate date labels for better readability

plt.show()
