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

	rv_columns = [
    'Ticker',
    'Price', 
    'PricetoEarningsRatio',
    'PEPercentile',
    'PricetoBookRatio',
    'PBPercentile',
    'PricetoSalesRatio',
    'PSPercentile',
    'EVdEBITDA',
    'EVdEBITDAPercentile',
    'EVdGP',
    'EVdGPPercentile',
    'RVScore'
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

	for column in ['PricetoEarningsRatio', 'PricetoBookRatio','PricetoSalesRatio', 'EVdEBITDA','EVdGP']:
		rv_dataframe[column].fillna(rv_dataframe[column].mean(), inplace = True)

	metrics = {
			'PricetoEarningsRatio': 'PEPercentile',
			'PricetoBookRatio':'PBPercentile',
			'PricetoSalesRatio': 'PSPercentile',
			'EVdEBITDA':'EVdEBITDAPercentile',
			'EVdGP':'EVdGPPercentile'
			}

	for row in rv_dataframe.index:
		for metric in metrics.keys():
			rv_dataframe.loc[row, metrics[metric]] = stats.percentileofscore(rv_dataframe[metric], rv_dataframe.loc[row, metric])/100

	for row in rv_dataframe.index:
		value_percentiles = []
		for metric in metrics.keys():
			value_percentiles.append(rv_dataframe.loc[row, metrics[metric]])
		rv_dataframe.loc[row, 'RVScore'] = mean(value_percentiles)
	
	rv_dataframe.sort_values('RVScore', ascending = False, inplace = True)

	# htmltable = rv_dataframe.to_html()
	# return HttpResponse(htmltable)
	json_records = rv_dataframe.reset_index().to_json(orient ='records') 
	data = [] 
	data = json.loads(json_records)
	context = {'d': data}

	return render(request, 'quant_value/value.html', context)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]