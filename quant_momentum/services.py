# import numpy as np 
# import pandas as pd 
# import requests
# import math
# from scipy import stats

# api_key = FPG90HGRKDM572Q4

# def get_price():
# 	symbol = 'IBM'
# 	url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
# 	data = requests.get(api_url).json()
# 	price = data['05. price']

# def create_data_frame():
# 	my_columns = ['Ticker', 'Stock Price']
# 	final_dataframe = pd.DataFrame(columns = my_columns)
# 	final_dataframe.append(pd.Series([symbol, price], index = my_columns), ignore_index = True)
