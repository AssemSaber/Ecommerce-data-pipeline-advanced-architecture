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

    first_df=checkNullKeys(df,'seller_id','rejected_sellers','Primary Key Missing Value')
    second_df=checkNullKeys(first_df,'seller_zip_code_prefix','rejected_sellers','seller_zip_code_prefix Missing Value')
    third_df=checkNullKeys(second_df,'seller_city','rejected_sellers','seller_city Missing Value')
    return third_df



seller_query="""
SELECT
    b.seller_id,
    b.seller_zip_code_prefix,
    b.seller_city,
    b.seller_state
FROM bronze.sellers AS b
LEFT JOIN silver.sellers AS s
    ON b.seller_id = s.seller_id
WHERE
    s.seller_id IS NULL

    OR ISNULL(b.seller_zip_code_prefix, '') <> ISNULL(s.seller_zip_code_prefix, '')
    OR ISNULL(b.seller_city, '')  <> ISNULL(s.seller_city, '')
    OR ISNULL(b.seller_state, '') <> ISNULL(s.seller_state, '');

"""
update_delete_seller="""
UPDATE s
SET
    s.is_delete = 1,
    s.load_timestamp = SYSDATETIME()
FROM silver.sellers AS s
LEFT JOIN bronze.sellers AS b
    ON s.seller_id = b.seller_id
WHERE b.seller_id IS NULL
  AND s.is_delete = 0;
"""

stage_silver_query="""
MERGE INTO silver.sellers AS target
USING stage.sellers AS source
    ON target.seller_id = source.seller_id

WHEN MATCHED AND (
    ISNULL(target.seller_zip_code_prefix, '') <> ISNULL(source.seller_zip_code_prefix, '')
    OR ISNULL(target.seller_city, '') <> ISNULL(source.seller_city, '')
    OR ISNULL(target.seller_state, '') <> ISNULL(source.seller_state, '')
)
THEN
    UPDATE SET
        target.seller_zip_code_prefix = source.seller_zip_code_prefix,
        target.seller_city = source.seller_city,
        target.seller_state = source.seller_state,
        target.load_timestamp = source.load_timestamp

WHEN NOT MATCHED BY TARGET
THEN
    INSERT (
        seller_id,
        seller_zip_code_prefix,
        seller_city,
        seller_state,
        load_timestamp
    )
    VALUES (
        source.seller_id,
        source.seller_zip_code_prefix,
        source.seller_city,
        source.seller_state,
        source.load_timestamp
    );
"""


main_columns_of_sellers = [
    "seller_id",
    "seller_zip_code_prefix",
    "seller_city",
    "seller_state"
]

engine = create_connection_sql_server()
with engine.begin() as conn:
    writeMergeAtomic(conn,update_delete_seller) # for is_delete=1 for the deleted records

df_sellers = read_table_from_sql_server(seller_query)

if not df_sellers.empty:

    df_sellers_not_null=checkColumnsNull(df_sellers)

    df_NocheckDuplicateKeys=checkDuplicateKeys(df_sellers_not_null,'seller_id','rejected_sellers','Duplicate Primary Key Found')

    final_df_sellers=addTimeToSilverTable(df_NocheckDuplicateKeys)
    try:
        engine = create_connection_sql_server() # atomic transaction(we send the same connection)
        with engine.begin() as conn:
            insert_into_sql_server_atomic(conn,final_df_sellers,'stage','sellers') # load the delta (changes or updates) into stage
            writeMergeAtomic(conn,stage_silver_query) # for setting updates and get the new records
    except Exception as e:
        print(f"We find error to load the customer table into silver {e}")

else:
    print("Customer table is up to dated")