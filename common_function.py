from datetime import datetime, timedelta
import pytz
import numpy as np
import pandas as pd
d = datetime.strptime("2199-10-13T10:53:53.000Z", "%Y-%m-%dT%H:%M:%S.000Z")



def get_utc_date():
    # Get the current UTC time
    utc_now = datetime.utcnow()

    # Define the target time zone
    target_timezone = pytz.timezone("Asia/Kolkata")  # UTC+05:30

    # Convert UTC time to the target time zone
    localized_time = utc_now.replace(tzinfo=pytz.utc).astimezone(target_timezone)

    # Format the localized time as a string in dd-mm-yyyy hh:mm:ss am/pm format
    formatted_time = localized_time.strftime("%d-%m-%Y %I:%M:%S %p")
    return formatted_time

def convert_date_column(df, column_name, date_formats,expcted_format):
    for date_format in date_formats:
        try:
            df[column_name] = pd.to_datetime(df[column_name], format=date_format).dt.strftime(expcted_format)
            break  # Break the loop if conversion is successful
        except ValueError:
            pass  # Continue to the next date format if conversion fails
    else:
        raise ValueError(f"The '{column_name}' column contains dates in multiple formats. All dates should be in a single format: {date_formats}.")
