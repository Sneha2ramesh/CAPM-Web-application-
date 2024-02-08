# Importing libraries
import datetime
import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import capm_functions

# Set page configuration
st.set_page_config(page_title="CAPM",
                   page_icon="chart_with_upwards_trend",
                   layout='wide')
st.title("Capital Asset Pricing Model")

# User input
col1, col2 = st.columns([1, 1])
with col1:
    # Allow the user to select 4 stocks from a predefined list
    stocks_list = st.multiselect("Choose 4 stocks", ('TSLA', 'AAPL', 'NFLX', 'MSFT', 'MGM', 'AMZN', 'NVDA', 'GOOGL'),
                                 ['TSLA', 'AAPL', 'AMZN', 'GOOGL'])
with col2:
    # Allow the user to input the number of years for data analysis
    year = st.number_input("Number of years", 1, 10)

# Downloading data SP500
end = datetime.date.today()
start = datetime.date(datetime.date.today().year - year, datetime.date.today().month, datetime.date.today().day)
SP500 = web.DataReader(["sp500"], 'fred', start, end)

stocks_df = pd.DataFrame()

# Download data for selected stocks
for stock in stocks_list:
    data = yf.download(stock, period=f'{year}y')
    stocks_df[f'{stock}'] = data['Close']

# Merge stock data with SP500 data
stocks_df.reset_index(inplace=True)
SP500.reset_index(inplace=True)
SP500.columns = ['Date', 'sp500']
stocks_df['Date'] = stocks_df['Date'].astype('datetime64[ns]')
stocks_df['Date'] = stocks_df['Date'].apply(lambda x: str(x)[:10])
stocks_df['Date'] = pd.to_datetime(stocks_df["Date"])
stocks_df = pd.merge(stocks_df, SP500, on='Date', how='inner')

# Displaying data
col1, col2 = st.columns([1, 1])
with col1:
    # Display the head of the dataframe
    st.markdown('### Dataframe head')
    st.dataframe(stocks_df.head(), use_container_width=True)
with col2:
    # Display the tail of the dataframe
    st.markdown('### Dataframe tail')
    st.dataframe(stocks_df.tail(), use_container_width=True)

# Plot stock prices
col1, col2 = st.columns([1, 1])
with col1:
    # Display stock prices with an interactive Plotly chart
    st.markdown('### Price of all the Stocks')
    st.plotly_chart(capm_functions.intreractive_plot(stocks_df))
with col2:
    # Display normalized stock prices with an interactive Plotly chart
    st.markdown('### Price of all the Stocks (After Normalizing)')
    st.plotly_chart(capm_functions.intreractive_plot(capm_functions.normalize(stocks_df)))

# Daily returns
stocks_daily_return = capm_functions.daily_return(stocks_df)

# Calculating beta and alpha
beta = {}
alpha = {}

for stock in stocks_daily_return.columns:
    if stock != 'Date' and stock != 'sp500':
        b, a = capm_functions.calculate_beta(stocks_daily_return, stock)
        beta[stock] = b
        alpha[stock] = a

# Display calculated beta values
beta_df = pd.DataFrame(columns=['Stock', 'Beta Value'])
beta_df['Stock'] = beta.keys()
beta_df['Beta Value'] = [round(i, 2) for i in beta.values()]

# Display beta values
with col1:
    st.markdown('### Calculated Beta Value')
    st.dataframe(beta_df, use_container_width=True)

# Risk-free rate and market return
rf = 0
rm = stocks_daily_return['sp500'].mean() * 252

# Calculating expected return using CAPM
return_df = pd.DataFrame()
return_value = []

for stock, value in beta.items():
    # Calculate expected return using CAPM formula
    return_value.append(round(rf + (value * (rm - rf)), 2))

return_df['Stock'] = stocks_list
return_df['Return Value'] = return_value

# Display calculated returns using CAPM
with col2:
    st.markdown('### Calculated Return using CAPM')
    st.dataframe(return_df, use_container_width=True)

