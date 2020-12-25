from django.shortcuts import render
from django.http import HttpResponse
from scipy import stats
from statistics import mean
import requests
import pandas as pd
import numpy as np
import json
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
	'OneYearPriceReturn',
	'OneYearReturnPercentile',
	'SixMonthPriceReturn',
	'SixMonthReturnPercentile',
	'ThreeMonthPriceReturn',
	'ThreeMonthReturnPercentile',
	'OneMonthPriceReturn',
	'OneMonthReturnPercentile',
	'HQMScore'
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
	'OneYear',
	'SixMonth',
	'ThreeMonth',
	'OneMonth'
	]
	final_dataframe.sort_values('OneYearPriceReturn', ascending = False, inplace = True)
	hqm_dataframe = final_dataframe.mask(final_dataframe.astype(object).eq('None')).dropna()

	for row in hqm_dataframe.index:
		for time_period in time_periods:
			change_column = f'{time_period}PriceReturn'
			percentile_column = f'{time_period}ReturnPercentile'
			hqm_dataframe.loc[row, percentile_column] = stats.percentileofscore(hqm_dataframe[change_column], hqm_dataframe.loc[row, change_column]) / 100

	for row in hqm_dataframe.index:
		momentum_percentiles = []
		for time_period in time_periods:
			momentum_percentiles.append(hqm_dataframe.loc[row, f'{time_period}ReturnPercentile'])
			hqm_dataframe.loc[row, 'HQMScore'] = mean(momentum_percentiles)

	hqm_dataframe.sort_values('HQMScore', ascending = False, inplace = True)

	json_records = hqm_dataframe.reset_index().to_json(orient ='records') 
	data = [] 
	data = json.loads(json_records)
	print(data)
	context = {'d': data}

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

	# htmltable = hqm_dataframe.to_html()
	# return HttpResponse(htmltable)

	return render(request, 'quant_momentum/momentum.html', context)
	

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]