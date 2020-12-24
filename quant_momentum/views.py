from django.shortcuts import render
from django.http import HttpResponse
import requests
import pandas as pd
# import numpy as py
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

	my_columns = ['Ticker', 'Price']
	final_dataframe = pd.DataFrame(columns = my_columns)
	price_list = []
	for symbol in stocks['Ticker']:
		api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
		data = requests.get(api_url).json()
		final_dataframe = final_dataframe.append(
			pd.Series([symbol,
				data['latestPrice']],
				index = my_columns),
			ignore_index = True)

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
	htmltable = final_dataframe.to_html()
	return HttpResponse(htmltable)
	