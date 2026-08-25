import os 
import sys
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from Connections.database import create_connection_sql_server
from sqlalchemy import text

def insert_data_to_sql_server(df, table_name,type='replace'):
    try:
        engine = create_connection_sql_server()
        df.to_sql(table_name, con=engine, if_exists=type, index=False,chunksize=1000)
    except Exception as e:
        print(f"Error inserting data: {e}")


def insert_into_sql_server(df,schema,table_name,type='replace'):
    try:
        engine = create_connection_sql_server()
        df.to_sql(name=table_name,schema=schema, con=engine, if_exists=type, index=False,chunksize=1000)
    except Exception as e:
        print(f"Error inserting data: {e}")
    return 1

def insert_into_sql_server_atomic(conn,df,schema,table_name,type='replace'):
    try:
        # engine = create_connection_sql_server()
        df.to_sql(name=table_name,schema=schema, con=conn, if_exists=type, index=False,chunksize=1000)
    except Exception as e:
        print(f"Error inserting data: {e}")
    

def writeMergeAtomic(conn,merge_query):
    try:
        # engine = create_connection_sql_server()

        # with engine.begin() as conn:
        conn.execute(text(merge_query))

    except Exception as e:
        print(f"Error executing merge: {e}")

def deleteOldOrders(conn,order_ids):

    if not order_ids:
        return

    ids = ",".join(f"'{x}'" for x in order_ids)

    query = f"""
        DELETE FROM gold.fact_orders
        WHERE order_id IN ({ids})
    """
    
    conn.exec_driver_sql(query)