from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pandas as pd

def create_connection_sql_server():
    try:
        conn_str = quote_plus(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"          
            "DATABASE=Atos;"       
            "Trusted_Connection=yes;"
        )

        return create_engine(
            f"mssql+pyodbc:///?odbc_connect={conn_str}",
            fast_executemany=True # it says like bulk insert
        )
    except Exception as e:
        print(f"Error creating connection: {e}")
        return None




