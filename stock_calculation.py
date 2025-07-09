from datetime import datetime
import pymongo
import pandas as pd
import numpy as np
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



# def report_calculation(all_data_df, date_filtered_df, start_date, end_date):
#     """
#     Main reporting function.
#     - Builds main date-range table.
#     - For each Symbol, also attaches last 10 years data from all_data_df.
#     """

#     # Make sure dates are timestamps
#     date_filtered_df = date_filtered_df.copy()
#     date_filtered_df['Date'] = pd.to_datetime(date_filtered_df['Date'], errors='coerce')
#     all_data_df['Date'] = pd.to_datetime(all_data_df['Date'], errors='coerce')

#     # Filter for user-requested date range
#     in_range = date_filtered_df[
#         (date_filtered_df['Date'] >= start_date) &
#         (date_filtered_df['Date'] <= end_date)
#     ].copy()

#     if in_range.empty:
#         return []

#     # Get Start price = price on start_date
#     start_df = in_range[in_range['Date'] == start_date].copy()
#     start_df = start_df.groupby('Symbol').agg({
#         'Date': 'first',
#         'Price': 'first'
#     }).reset_index().rename(columns={'Price': 'StartPrice'})

#     # Get Max price in range
#     max_df = in_range.loc[in_range.groupby('Symbol')['Price'].idxmax()].copy()
#     max_df = max_df[['Symbol', 'Price']].rename(columns={'Price': 'MaxPrice'})

#     # Merge
#     result = pd.merge(start_df, max_df, on='Symbol', how='inner')
#     result['Date'] = result['Date'].dt.strftime('%Y-%m-%d')

#     # Ensure numeric
#     result['StartPrice'] = pd.to_numeric(result['StartPrice'], errors='coerce')
#     result['MaxPrice'] = pd.to_numeric(result['MaxPrice'], errors='coerce')

#     # Avoid division by zero
#     result['Percentage'] = np.where(
#         result['StartPrice'] > 0,
#         ((result['MaxPrice'] - result['StartPrice']) / result['StartPrice'] * 100).round(2).astype(str) + '%',
#         '0%'
#     )

#     # Add placeholder counts (or compute your thresholds here if you want)
#     for col in ['Value_lt_8','Value_lt_10','Value_lt_12','Value_lt_14','Value_lt_16','Value_lt_18','Value_lt_20',
#                 'Value_gt_8','Value_gt_10','Value_gt_12','Value_gt_14','Value_gt_16','Value_gt_18','Value_gt_20']:
#         result[col] = 0

#     # Convert main table to records
#     main_table = result.to_dict(orient='records')

#     # Add last 10 years data for each symbol
#     last_10_years_data = {}
#     for symbol in result['Symbol'].unique():
#         history = get_last_10_year_data(all_data_df, symbol, start_date)
#         last_10_years_data[symbol] = history

#     # Return both to template
#     return {
#         'main_table': main_table,
#         'last_10_years': last_10_years_data
#     }


# import pandas as pd
# import numpy as np

# def get_last_10_year_data(all_data_df, symbol, start_date):
#     """
#     For a single symbol, return last 10 years of 'closest or next available' start_date-like data.
#     """
#     results = []
#     # Ensure datetime
#     all_data_df['Date'] = pd.to_datetime(all_data_df['Date'], errors='coerce')
#     symbol_df = all_data_df[all_data_df['Symbol'] == symbol].copy()

#     for i in range(1, 11):
#         target_year = start_date.year - i
#         # Handle edge cases like Feb 29
#         try:
#             target_date = start_date.replace(year=target_year)
#         except ValueError:
#             target_date = start_date.replace(day=start_date.day - 1, year=target_year)

#         # All data in that year
#         df_year = symbol_df[symbol_df['Date'].dt.year == target_year]

#         if df_year.empty:
#             results.append({
#                 'Year': target_year,
#                 'Date': None,
#                 'Price': None
#             })
#             continue

#         # Get first date >= target_date in that year
#         df_valid = df_year[df_year['Date'] >= target_date]
#         if not df_valid.empty:
#             nearest = df_valid.sort_values('Date').iloc[0]
#             results.append({
#                 'Year': target_year,
#                 'Date': nearest['Date'].strftime('%Y-%m-%d'),
#                 'Price': nearest['Price']
#             })
#         else:
#             # If none on or after, try any earliest in that year
#             nearest = df_year.sort_values('Date').iloc[0]
#             results.append({
#                 'Year': target_year,
#                 'Date': nearest['Date'].strftime('%Y-%m-%d'),
#                 'Price': nearest['Price']
#             })

#     return results


# def report_calculation(all_data_df, date_filtered_df, start_date, end_date):
#     ### Part 1: For user date range
#     price = date_filtered_df.copy()

#     start_price_df = price[price['Date'] == start_date].groupby('Symbol').agg({
#         'Date': 'first',
#         'Open': 'first',
#         'High': 'first',
#         'Low': 'first',
#         'Price': 'first',
#         'Vol': 'first'
#     }).reset_index()

#     max_price_df = price.loc[price.groupby('Symbol')['Price'].idxmax()].reset_index(drop=True)

#     start_price_df['Date'] = start_price_df['Date'].dt.strftime('%Y-%m-%d')
#     max_price_df['Date'] = max_price_df['Date'].dt.strftime('%Y-%m-%d')


#     ### Part 2: 10-year analysis on FULL DATA
#     last_10_years_dates = [start_date - pd.DateOffset(years=i) for i in range(1, 11)]
#     years_df = pd.DataFrame({
#         'Year': range(start_date.year - 1, start_date.year - 11, -1),
#         'Date': last_10_years_dates
#     })

#     all_data_df['Date'] = pd.to_datetime(all_data_df['Date'], errors='coerce')

#     last_10_years_start_price = []
#     last_10_years_max_price = []

#     for i in range(1, 11):
#         year_start_date = years_df.loc[i-1, 'Date']
#         year_end_date = year_start_date + pd.DateOffset(years=1)

#         year_price = all_data_df[
#             (all_data_df['Date'] >= year_start_date) &
#             (all_data_df['Date'] < year_end_date)
#         ]

#         if year_price.empty:
#             last_10_years_start_price.append([])
#             last_10_years_max_price.append([])
#             continue

#         # Get first date in that year per symbol
#         year_start_price_df = (
#             year_price
#             .groupby('Symbol')
#             .apply(lambda x: x.loc[x['Date'].idxmin()])
#             .reset_index(drop=True)
#         )

#         # Get max price in that year per symbol
#         year_max_price_df = (
#             year_price
#             .loc[year_price.groupby('Symbol')['Price'].idxmax()]
#             .reset_index(drop=True)
#         )

#         year_start_price_df['Date'] = year_start_price_df['Date'].dt.strftime('%Y-%m-%d')
#         year_max_price_df['Date'] = year_max_price_df['Date'].dt.strftime('%Y-%m-%d')

#         year_start_price_df['Year'] = years_df.loc[i-1, 'Year']
#         year_max_price_df['Year'] = years_df.loc[i-1, 'Year']

#         last_10_years_start_price.append(year_start_price_df.to_dict(orient='records'))
#         last_10_years_max_price.append(year_max_price_df.to_dict(orient='records'))


#     return {
#         "start_price": start_price_df.to_dict(orient='records'),
#         "max_price": max_price_df.to_dict(orient='records'),
#         "last_10_years_start_price": last_10_years_start_price,
#         "last_10_years_max_price": last_10_years_max_price
#     }

def report_calculation(all_data_df, date_filtered_df, start_date, end_date):
    all_data_df = all_data_df.copy()
    date_filtered_df = date_filtered_df.copy()

    all_data_df['Date'] = pd.to_datetime(all_data_df['Date'], errors='coerce')
    date_filtered_df['Date'] = pd.to_datetime(date_filtered_df['Date'], errors='coerce')

    unified_rows = []
    last_10_years_percentages = {}
    yearwise_data = {}

    ### Part 1: Selected User Date Range ###
    price = date_filtered_df[
        (date_filtered_df['Date'] >= start_date) & (date_filtered_df['Date'] <= end_date)
    ].copy()

    if not price.empty:
        start_df = price[price['Date'] == start_date].groupby('Symbol').agg({
            'Date': 'first',
            'Price': 'first'
        }).reset_index().rename(columns={'Price': 'StartPrice'})

        max_df = price.loc[price.groupby('Symbol')['Price'].idxmax()].reset_index(drop=True)
        max_df = max_df[['Symbol', 'Price']].rename(columns={'Price': 'MaxPrice'})

        result = pd.merge(start_df, max_df, on='Symbol', how='inner')
        result['Date'] = result['Date'].dt.strftime('%Y-%m-%d')
        result['Year'] = start_date.year
        result['Source'] = 'Selected Range'

        result['StartPrice'] = pd.to_numeric(result['StartPrice'], errors='coerce').fillna(0)
        result['MaxPrice'] = pd.to_numeric(result['MaxPrice'], errors='coerce').fillna(0)
        result['Percentage'] = np.where(
            result['StartPrice'] > 0,
            ((result['MaxPrice'] - result['StartPrice']) / result['StartPrice'] * 100).round(2),
            0
        )

        unified_rows.extend(result.to_dict(orient='records'))

    ### Part 2: Last 10 Years History ###
    last_10_years_dates = [start_date - pd.DateOffset(years=i) for i in range(1, 11)]
    years_df = pd.DataFrame({
        'Year': [start_date.year - i for i in range(1, 11)],
        'Date': last_10_years_dates
    })

    for i in range(10):
        year_start_date = years_df.loc[i, 'Date']
        year_end_date = year_start_date + pd.DateOffset(years=1)

        year_price = all_data_df[
            (all_data_df['Date'] >= year_start_date) &
            (all_data_df['Date'] < year_end_date)
        ]

        if year_price.empty:
            continue

        # Get first date in year per symbol
        year_start_df = year_price.groupby('Symbol').apply(
            lambda x: x.loc[x['Date'].idxmin()]
        ).reset_index(drop=True)
        year_start_df['StartPrice'] = pd.to_numeric(year_start_df['Price'], errors='coerce').fillna(0)

        # Get max price in that year per symbol
        year_max_df = year_price.loc[
            year_price.groupby('Symbol')['Price'].idxmax()
        ].reset_index(drop=True)
        year_max_df['MaxPrice'] = pd.to_numeric(year_max_df['Price'], errors='coerce').fillna(0)

        # Merge
        merged = pd.merge(
            year_start_df[['Symbol', 'Date', 'StartPrice']],
            year_max_df[['Symbol', 'MaxPrice']],
            on='Symbol',
            how='inner'
        )

        # Compute percentage safely
        merged['Percentage'] = np.where(
            merged['StartPrice'] > 0,
            ((merged['MaxPrice'] - merged['StartPrice']) / merged['StartPrice'] * 100).round(2),
            0
        )

        merged['Date'] = merged['Date'].dt.strftime('%Y-%m-%d')
        merged['Year'] = years_df.loc[i, 'Year']
        merged['Source'] = 'Last 10 Years'

        for row in merged.itertuples(index=False):
            symbol = row.Symbol
            year = row.Year
            pct = row.Percentage if hasattr(row, 'Percentage') else 0

            # Store yearwise
            yearwise_data.setdefault(symbol, {})
            yearwise_data[symbol][year] = {
                "StartPrice": row.StartPrice,
                "MaxPrice": row.MaxPrice,
                "Percentage": pct
            }

            last_10_years_percentages.setdefault(symbol, []).append(pct)

        unified_rows.extend(merged.to_dict(orient='records'))

    ### Part 3: Count bins
    count_bins = [8, 10, 12, 14, 16, 18, 20]

    for row in unified_rows:
        symbol = row['Symbol']
        pct_list = last_10_years_percentages.get(symbol, [])
        for b in count_bins:
            row[f'Count_lt_{b}'] = sum((p < b) for p in pct_list)
            row[f'Count_gt_{b}'] = sum((p > b) for p in pct_list)

    for symbol in yearwise_data:
        pct_list = last_10_years_percentages.get(symbol, [])
        for b in count_bins:
            yearwise_data[symbol][f'Count_lt_{b}'] = sum((p < b) for p in pct_list)
            yearwise_data[symbol][f'Count_gt_{b}'] = sum((p > b) for p in pct_list)

    return unified_rows, yearwise_data
def lst_yrd_10_df(google_collection):
    df = google_collection.aggregate(
        [
            {
        '$project': { 
            'Date':1,
            'Symbol': 1, 
            'Price': 1, 
            'Open': 1,
            'High':1,
            'Low':1,
            'Vol':1,
            "_id": 0,
                }
            },
        ]
    )
    df = tuple(df)
    df1 = pd.DataFrame(df)
    return df1