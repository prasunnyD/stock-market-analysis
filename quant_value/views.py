from django.shortcuts import render
from django.http import HttpResponse
from scipy import stats
from statistics import mean
import requests
import pandas as pd
import numpy as np
import csv
import os

# Create your views here.
def home(request):

	rv_columns = [
    'Ticker',
    'Price', 
    'Price-to-Earnings Ratio',
    'PE Percentile',
    'Price-to-Book Ratio',
    'PB Percentile',
    'Price-to-Sales Ratio',
    'PS Percentile',
    'EV/EBITDA',
    'EV/EBITDA Percentile',
    'EV/GP',
    'EV/GP Percentile',
    'RV Score'
]

	stocks = pd.read_csv('sp_500_stocks.csv')
	IEX_CLOUD_API_TOKEN = os.getenv('IEX_CLOUD_API_TOKEN')

	#Batch API Call S&P500
	symbol_groups = list(chunks(stocks['Ticker'], 100))
	symbol_strings = []
	for i in range(0, len(symbol_groups)):
		symbol_strings.append(','.join(symbol_groups[i]))
	
	rv_dataframe = pd.DataFrame(columns = rv_columns)
	price_list = []

	for symbol_string in symbol_strings:
		batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote,advanced-stats&token={IEX_CLOUD_API_TOKEN}'
		data = requests.get(batch_api_call_url).json()
		for symbol in symbol_string.split(','):
			enterprise_value = data[symbol]['advanced-stats']['enterpriseValue']
			ebitda = data[symbol]['advanced-stats']['EBITDA']
			gross_profit = data[symbol]['advanced-stats']['grossProfit']

			try:
				ev_to_ebitda = enterprise_value/ebitda
			except TypeError:
				ev_to_ebitda = np.NaN

			try:
				ev_to_gross_profit = enterprise_value/gross_profit
			except TypeError:
				ev_to_gross_profit = np.NaN
	            
			rv_dataframe = rv_dataframe.append(
				pd.Series([
					symbol,
					data[symbol]['quote']['latestPrice'],
					data[symbol]['quote']['peRatio'],
					'N/A',
					data[symbol]['advanced-stats']['priceToBook'],
					'N/A',
					data[symbol]['advanced-stats']['priceToSales'],
					'N/A',
					ev_to_ebitda,
					'N/A',
					ev_to_gross_profit,
					'N/A',
					'N/A'
	        ],
				index = rv_columns),
				ignore_index = True
	        )

	for column in ['Price-to-Earnings Ratio', 'Price-to-Book Ratio','Price-to-Sales Ratio',  'EV/EBITDA','EV/GP']:
		rv_dataframe[column].fillna(rv_dataframe[column].mean(), inplace = True)

	metrics = {
			'Price-to-Earnings Ratio': 'PE Percentile',
			'Price-to-Book Ratio':'PB Percentile',
			'Price-to-Sales Ratio': 'PS Percentile',
			'EV/EBITDA':'EV/EBITDA Percentile',
			'EV/GP':'EV/GP Percentile'
			}

	for row in rv_dataframe.index:
		for metric in metrics.keys():
			rv_dataframe.loc[row, metrics[metric]] = stats.percentileofscore(rv_dataframe[metric], rv_dataframe.loc[row, metric])/100

	for row in rv_dataframe.index:
		value_percentiles = []
		for metric in metrics.keys():
			value_percentiles.append(rv_dataframe.loc[row, metrics[metric]])
		rv_dataframe.loc[row, 'RV Score'] = mean(value_percentiles)
	
	rv_dataframe.sort_values('RV Score', ascending = False, inplace = True)

	htmltable = rv_dataframe.to_html()
	return HttpResponse(htmltable)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]