import os 
import sys
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from DataQuality.Check_Keys import *
from DataQuality.numbericValues import checkPositiveValues,checkRangeValues
from Extraction.database import read_table_from_sql_server
from Loading.database import insert_into_sql_server,insert_into_sql_server_atomic,writeMergeAtomic
from metadata.incremental_loading import addTimeToSilverTable
from Connections.database import create_connection_sql_server

def checkColumnsNull(df): 

    first_df=checkNullKeys(df,'customer_id','rejected_customers','Primary Key Missing Value')
    second_df=checkNullKeys(df,'customer_zip_code_prefix','rejected_customers','Foreign Key for zip code prefix Missing Value')
    return second_df


#  we get the delta (insertion && updates)
customer_query="""
    SELECT
        b.customer_id,
        b.customer_unique_id,
        b.customer_zip_code_prefix,
        b.customer_city,
        b.customer_state
    FROM bronze.customers AS b
    LEFT JOIN silver.customers AS s
        ON b.customer_id = s.customer_id
    WHERE
        s.customer_id IS NULL
        OR ISNULL(b.customer_unique_id, '') <> ISNULL(s.customer_unique_id, '')
        OR ISNULL(b.customer_zip_code_prefix, -1) <> ISNULL(s.customer_zip_code_prefix, -1)
        OR ISNULL(b.customer_city, '') <> ISNULL(s.customer_city, '')
        OR ISNULL(b.customer_state, '') <> ISNULL(s.customer_state, '');
"""

stage_silver_query="""
MERGE INTO silver.customers AS target
USING stage.customers AS source
    ON target.customer_id = source.customer_id

WHEN MATCHED AND (
    ISNULL(target.customer_unique_id, '') <> ISNULL(source.customer_unique_id, '')
    OR ISNULL(target.customer_zip_code_prefix, '') <> ISNULL(source.customer_zip_code_prefix, '')
    OR ISNULL(target.customer_city, '') <> ISNULL(source.customer_city, '')
    OR ISNULL(target.customer_state, '') <> ISNULL(source.customer_state, '')
)
THEN
    UPDATE SET
        target.customer_unique_id = source.customer_unique_id,
        target.customer_zip_code_prefix = source.customer_zip_code_prefix,
        target.customer_city = source.customer_city,
        target.customer_state = source.customer_state,
        target.load_timestamp = source.load_timestamp

WHEN NOT MATCHED BY TARGET
THEN
    INSERT (
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,
        load_timestamp
    )
    VALUES (
        source.customer_id,
        source.customer_unique_id,
        source.customer_zip_code_prefix,
        source.customer_city,
        source.customer_state,
        source.load_timestamp
    );
"""


main_columns_of_customers=["customer_id","customer_unique_id","customer_zip_code_prefix","customer_city","customer_state"]

df_customers = read_table_from_sql_server(customer_query)

if not df_customers.empty:

    df_customers_not_null=checkColumnsNull(df_customers)

    df_NocheckDuplicateKeys=checkDuplicateKeys(df_customers_not_null,'customer_id','rejected_customers','Duplicate Primary Key Found')

    final_df_customers=addTimeToSilverTable(df_NocheckDuplicateKeys)
    try:
        engine = create_connection_sql_server() # atomic transaction(we send the same connection)
        with engine.begin() as conn:
            insert_into_sql_server_atomic(conn,final_df_customers,'stage','customers') # load the delta (changes or updates) into stage
            writeMergeAtomic(conn,stage_silver_query)
        # insert_into_sql_server(load_delta_into_silver,'silver','customers','append') # upsert the stage with silver
    except Exception as e:
        print(f"We find error to load the customer table into silver {e}")

else:
    print("Customer table is up to dated")