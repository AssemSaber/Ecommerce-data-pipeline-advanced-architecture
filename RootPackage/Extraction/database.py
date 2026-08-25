import os 
import sys
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from Connections.database import create_connection_sql_server


def read_table_from_sql_server(query):
    try:
        engine = create_connection_sql_server()
        return pd.read_sql(query, con=engine)
    except Exception as e:
        print(f"Error reading table: {e}")
        return None
    