from datetime import datetime
import pymongo
import pandas as pd
import json
from json_response import JSONResponse
from common_function import *
import time
d = datetime.strptime("2199-10-13T10:53:53.000Z", "%Y-%m-%dT%H:%M:%S.000Z")
# ----stock data calculation-----------

def format_number(number):
    # Convert the number to an integer and use string formatting to add commas for thousands separator
    return "{:,.0f}".format(number)

def format_float(number):
    # Convert the number to a float and use string formatting to add commas for thousands separator and 2 decimal places
    return "{:,.2f}".format(number)


def stock_data_calculation(google_df,start_date,end_date):

    

    start_date = datetime.strptime(start_date.strftime("%d-%m-%Y"), "%d-%m-%Y")
    end_date = datetime.strptime(end_date.strftime("%d-%m-%Y"), "%d-%m-%Y")

    df = google_df.aggregate(
        [
            {
        '$project': { 
            'Symbol': 1, 
            'Price': 1, 
            'Open': 1,
            'High':1,
            'Low':1,
            'Vol':1,
            "_id": 0,
                    "Date": {
                        "$convert": {
                            "input": "$Date",
                            "to": "date",
                            "onError": d,
                            "onNull": d,
                        }
                    },
                }
            },
            {"$match": {"Date": {"$gte": start_date, "$lt": end_date}}},
        ]
    )
    df = tuple(df)
    df1 = pd.DataFrame(df)
    return df1



def format_float(value):
    
    return float(value) if isinstance(value, (int, float)) else 0.0


import pandas as pd

def report_calculation(df, start_date, end_date):
    # Filter data within the date range
    price = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    # Get the starting price for each symbol on start_date
    start_price_df = price[price['Date'] == start_date].groupby('Symbol').agg({
        'Date': 'first',
        'Open': 'first',
        'High': 'first',
        'Low': 'first',
        'Price': 'first',
        'Vol': 'first'
    }).reset_index()

    # Get the maximum price for each symbol within the date range
    max_price_df = price.loc[price.groupby('Symbol')['Price'].idxmax()].reset_index(drop=True)

    # Format Date as 'YYYY-MM-DD'
    start_price_df['Date'] = start_price_df['Date'].dt.strftime('%Y-%m-%d')
    max_price_df['Date'] = max_price_df['Date'].dt.strftime('%Y-%m-%d')

    # Generate last 10 years date
    last_10_years_dates = [start_date - pd.DateOffset(years=i) for i in range(1, 11)]

    # Convert to DataFrame if you want a nice tabular view
    years_df = pd.DataFrame({'Year': range(start_date.year - 1, start_date.year - 11, -1),
                             'Date': last_10_years_dates})

    # Calculate last 10 years' start price and max price for each symbol
    last_10_years_start_price = []
    last_10_years_max_price = []

    for i in range(1, 11):
        year_start_date = years_df.loc[i-1, 'Date']
        year_end_date = year_start_date + pd.DateOffset(years=1)

        year_price = df[(df['Date'] >= year_start_date) & (df['Date'] < year_end_date)]

        # Get the first available date within the year for each symbol
        year_start_price_df = year_price.groupby('Symbol').apply(lambda x: x.loc[x['Date'].idxmin()]).reset_index(drop=True)

        # Get the maximum price within the year for each symbol
        year_max_price_df = year_price.loc[year_price.groupby('Symbol')['Price'].idxmax()].reset_index(drop=True)

        year_start_price_df['Date'] = year_start_price_df['Date'].dt.strftime('%Y-%m-%d')
        year_max_price_df['Date'] = year_max_price_df['Date'].dt.strftime('%Y-%m-%d')

        year_start_price_df['Year'] = years_df.loc[i-1, 'Year']
        year_max_price_df['Year'] = years_df.loc[i-1, 'Year']

        last_10_years_start_price.append(year_start_price_df.to_dict(orient='records'))
        last_10_years_max_price.append(year_max_price_df.to_dict(orient='records'))

    return {
        "start_price": start_price_df.to_dict(orient='records'),
        "max_price": max_price_df.to_dict(orient='records'),
        "last_10_years_start_price": last_10_years_start_price,
        "last_10_years_max_price": last_10_years_max_price
    }