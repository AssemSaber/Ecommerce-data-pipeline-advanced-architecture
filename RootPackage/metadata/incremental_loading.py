import os 
import sys
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from Extraction.database import read_table_from_sql_server
from Loading.database import insert_into_sql_server
from Connections.database import create_connection_sql_server
from sqlalchemy import text
from datetime import datetime


def addTimeToSilverTable(df):
    df['load_timestamp'] = pd.Timestamp.now().floor("min")
    return df


def getLastLoadFromMetaData(table_name):
    query=f"""
        select last_load from metadata 
        where table_name='{table_name}'
    """
    df=read_table_from_sql_server(query)
    return df["last_load"].iloc[0]


def getLastLoadFromTable(table_name):
    query=f"""
        select max(load_timestamp) as load_timestamp from silver.{table_name}
    """
    df=read_table_from_sql_server(query)
    return df["load_timestamp"].iloc[0]


def writeLastTimeToMetaData(table_name): 
    lastLoad=getLastLoadFromTable(table_name)

    # it will use the :last_load & :table_name created in the next conn
    query = text("""
        UPDATE metadata
        SET last_load = :last_load
        WHERE table_name = :table_name
    """)

    # it will use last_load & table_name as variables
    engine = create_connection_sql_server() 
    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "last_load": lastLoad,
                "table_name": table_name
            }
        )


def getDiffDataFromTable(columns,table_name):
    last_load_metadata=getLastLoadFromMetaData(table_name)
    selected_columns= ", ".join(columns)
    query=f"""
        select {selected_columns} from silver.{table_name} 
        where load_timestamp > '{last_load_metadata}'
    """
    return read_table_from_sql_server(query)



def writeLastTimeToMetaData(table_name,lastLoad): 

    # it will use the :last_load & :table_name created in the next conn
    query = text("""
        UPDATE metadata
        SET last_load = :last_load
        WHERE table_name = :table_name
    """)

    # it will use last_load & table_name as variables
    engine = create_connection_sql_server() 
    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "last_load": lastLoad,
                "table_name": table_name
            }
        )
