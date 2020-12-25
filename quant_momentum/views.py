from django.shortcuts import render
from django.http import HttpResponse
from scipy import stats
import requests
import pandas as pd
import numpy as np
import csv
import os

# Create your views here.
def home(request):
	#symbol = 'IBM'
	stocks = pd.read_csv('sp_500_stocks.csv')
	IEX_CLOUD_API_TOKEN = os.getenv('IEX_CLOUD_API_TOKEN')

	# with open('sp_500_stocks.csv', newline = '') as f:
	# 	reader = csv.reader(f)
	# 	symbols = list(reader)

	# my_columns = ['Ticker', 'Price']

	#Single API Call
	#final_dataframe = pd.DataFrame(columns = my_columns)
	# for symbol in stocks['Ticker']: 
	# 	api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
	# 	data = requests.get(api_url).json()
	# 	final_dataframe = final_dataframe.append(pd.Series([symbol, data['latestPrice']], index = my_columns), ignore_index = True)

	#Batch API Call S&P500
	# symbol_groups = list(chunks(stocks['Ticker'], 100))
	# symbol_strings = []
	# for i in range(0, len(symbol_groups)):
	# 	symbol_strings.append(','.join(symbol_groups[i]))
	
	# final_dataframe = pd.DataFrame(columns = my_columns)
	# price_list = []

	# for symbol_string in symbol_strings:
	# 	batch_api_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
	# 	data = requests.get(batch_api_url).json()
	# 	for symbol in symbol_string.split(','):
	# 		final_dataframe = final_dataframe.append(
	# 			pd.Series([symbol,
	# 				data[symbol]['quote']['latestPrice']],
	# 				index = my_columns),
	# 			ignore_index = True)


	symbol_groups = list(chunks(stocks['Ticker'], 100))
	symbol_strings = []
	for i in range(0, len(symbol_groups)):
		symbol_strings.append(','.join(symbol_groups[i]))
	
	my_columns = [
	'Ticker',
	'Price',
	'One-Year Price Return',
	'One-Year Return Percentile',
	'Six-Month Price Return',
	'Six-Month Return Percentile',
	'Three-Month Price Return',
	'Three-Month Return Percentile',
	'One-Month Price Return',
	'One-Month Return Percentile',
	'HQM Score'
	]

	final_dataframe = pd.DataFrame(columns = my_columns)
	for symbol_string in symbol_strings:
		batch_api_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
		data = requests.get(batch_api_url).json()
		for symbol in symbol_string.split(','):
			final_dataframe = final_dataframe.append(
				pd.Series([symbol,
					data[symbol]['quote']['latestPrice'],
					data[symbol]['stats']['year1ChangePercent'],
					'N/A',
					data[symbol]['stats']['month6ChangePercent'],
					'N/A',
					data[symbol]['stats']['month3ChangePercent'],
					'N/A',
					data[symbol]['stats']['month1ChangePercent'],
					'N/A',
					'N/A'
					],
					index = my_columns),
				ignore_index = True)

	time_periods = [
	'One-Year',
	'Six-Month',
	'Three-Month',
	'One-Month'
	]
	final_dataframe.sort_values('One-Year Price Return', ascending = False, inplace = True)
	hqm_dataframe = final_dataframe.mask(final_dataframe.astype(object).eq('None')).dropna()

	for row in hqm_dataframe.index:
		for time_period in time_periods:
			change_column = f'{time_period} Price Return'
			percentile_column = f'{time_period} Return Percentile'
			hqm_dataframe.loc[row, percentile_column] = stats.percentileofscore(hqm_dataframe[change_column], hqm_dataframe.loc[row, change_column]) / 100

	
	#final_dataframe.drop(final_dataframe[final_dataframe['One-Year Price Return'].index == 'None'], inplace = True)
	# return render(request, 'quant_momentum/momentum.html', {
	# 	'dataframe': final_dataframe,
	# 	})
	# symbol = 'IBM'
	# api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
	# data = requests.get(api_url).json()
	# #print(data)
	# final_dataframe = final_dataframe.append(
	#  	pd.Series([symbol,
	#  		data['latestPrice']],
	# 		index = my_columns),
	#  	ignore_index = True)
	htmltable = hqm_dataframe.to_html()
	return HttpResponse(htmltable)
	

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]