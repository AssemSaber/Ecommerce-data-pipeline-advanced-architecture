import pandas as pd
import sys
from sqlalchemy import create_engine
sys.path.append("H:\\Atos\\RootPackage")
from metadata.incremental_loading import getLastLoadFromMetaData,writeLastTimeToMetaData
from Loading.database import insert_into_sql_server
from datetime import datetime


start_date=getLastLoadFromMetaData("date")
current_date= pd.Timestamp.today().normalize()
if start_date < current_date:
    dates = pd.date_range(
        start=start_date,
        end=current_date,
        freq="D"
    )

    # Create DataFrame
    dim_date = pd.DataFrame({
        "full_date": dates,
        "year": dates.year,
        "month": dates.month,
        "day": dates.day,
        "quarter": dates.quarter
    })
    try:
        insert_into_sql_server(dim_date,'gold',"dim_date","append")
        writeLastTimeToMetaData('date',current_date)
        print(
            f"Successfully loaded {len(dim_date)} dates "
            f"from {start_date.date()} to {current_date.date()}"
        )
    except Exception as e:
        print(f"Error loading dim_date: {e}")
else:
    print("dim_date is already up to date.")