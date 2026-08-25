import os 
import sys
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from DataQuality.Check_Keys import *
from DataQuality.numbericValues import checkPositiveValues,checkRangeValues
from Extraction.database import read_table_from_sql_server
from Extraction.files import read_csv
from Loading.database import insert_into_sql_server,insert_into_sql_server_atomic,writeMergeAtomic
from metadata.incremental_loading import addTimeToSilverTable
from Connections.database import create_connection_sql_server

def getMappingProductCategory(df_products):
    mappingTable=read_csv(r'H:\Atos\Ecommerce Dataset\product_category_name_translation.csv')
    df_products = df_products.merge(
    mappingTable,
    on="product_category_name",
    how="left"
    )

    df_products["product_category_name"] = (
    df_products["product_category_name_english"]
    )

    df_products.drop(
    columns=["product_category_name_english"],
    inplace=True
    )
    return df_products

def checkColumnsNull(df): 

    first_df=checkNullKeys(df,'product_id','rejected_products','Primary Key Missing Value')
    return first_df

def checKPositvieNumbers(df):
    main_columns_of_products = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
    ]
    for col in main_columns_of_products:
        checkPositiveValues(df,col,"rejected_products",f"Negative Value in {col}")

    return df


#  we get the delta (insertion && updates)
product_query="""
SELECT
    b.product_id,
    b.product_category_name,
    b.product_name_lenght,
    b.product_description_lenght,
    b.product_photos_qty,
    b.product_weight_g,
    b.product_length_cm,
    b.product_height_cm,
    b.product_width_cm
FROM bronze.products AS b
LEFT JOIN silver.products AS s
    ON b.product_id = s.product_id
WHERE
    s.product_id IS NULL

    OR ISNULL(b.product_category_name, '') <> ISNULL(s.product_category_name, '')

    OR ISNULL(b.product_name_lenght, -1) <> ISNULL(s.product_name_lenght, -1)

    OR ISNULL(b.product_description_lenght, '') <> ISNULL(s.product_description_lenght, '')

    OR ISNULL(b.product_photos_qty, -1) <> ISNULL(s.product_photos_qty, -1)

    OR ISNULL(b.product_weight_g, -1)  <> ISNULL(s.product_weight_g, -1)

    OR ISNULL(b.product_length_cm, -1)  <> ISNULL(s.product_length_cm, -1)

    OR ISNULL(b.product_height_cm, -1)  <> ISNULL(s.product_height_cm, -1)

    OR ISNULL(b.product_width_cm, -1) <> ISNULL(s.product_width_cm, -1);

"""
update_delete_seller="""
UPDATE s
SET
    s.is_delete = 1,
    s.load_timestamp = SYSDATETIME()
FROM silver.products AS s
LEFT JOIN bronze.products AS b
    ON s.product_id = b.product_id
WHERE b.product_id IS NULL
  AND s.is_delete = 0;
"""

stage_silver_query="""
MERGE INTO silver.products AS target
USING stage.products AS source
    ON target.product_id = source.product_id

WHEN MATCHED AND (
        ISNULL(target.product_category_name, '')   <> ISNULL(source.product_category_name, '')

    OR ISNULL(target.product_name_lenght, -1)   <> ISNULL(source.product_name_lenght, -1)

    OR ISNULL(target.product_description_lenght, '')   <> ISNULL(source.product_description_lenght, '')

    OR ISNULL(target.product_photos_qty, -1) <> ISNULL(source.product_photos_qty, -1)

    OR ISNULL(target.product_weight_g, -1)  <> ISNULL(source.product_weight_g, -1)

    OR ISNULL(target.product_length_cm, -1) <> ISNULL(source.product_length_cm, -1)

    OR ISNULL(target.product_height_cm, -1) <> ISNULL(source.product_height_cm, -1)

    OR ISNULL(target.product_width_cm, -1) <> ISNULL(source.product_width_cm, -1)
)
THEN
    UPDATE SET
        target.product_category_name = source.product_category_name,
        target.product_name_lenght = source.product_name_lenght,
        target.product_description_lenght = source.product_description_lenght,
        target.product_photos_qty = source.product_photos_qty,
        target.product_weight_g = source.product_weight_g,
        target.product_length_cm = source.product_length_cm,
        target.product_height_cm = source.product_height_cm,
        target.product_width_cm = source.product_width_cm,
        target.load_timestamp = source.load_timestamp

WHEN NOT MATCHED BY TARGET
THEN
    INSERT (
        product_id,
        product_category_name,
        product_name_lenght,
        product_description_lenght,
        product_photos_qty,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm,
        load_timestamp
    )
    VALUES (
        source.product_id,
        source.product_category_name,
        source.product_name_lenght,
        source.product_description_lenght,
        source.product_photos_qty,
        source.product_weight_g,
        source.product_length_cm,
        source.product_height_cm,
        source.product_width_cm,
        source.load_timestamp
    );
"""


main_columns_of_products = [
    "product_id",
    "product_category_name",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

engine = create_connection_sql_server()
with engine.begin() as conn:
    writeMergeAtomic(conn,update_delete_seller) # for is_delete=1 for the deleted records

df_products = read_table_from_sql_server(product_query)
print("siver delta",df_products)

if not df_products.empty:

    df_products_not_null=checkColumnsNull(df_products)
    # df_mapping=getMappingProductCategory(df_products_not_null)
    print(df_products_not_null.columns)
    df_positivNumbers=checKPositvieNumbers(df_products_not_null)
    df_NocheckDuplicateKeys=checkDuplicateKeys(df_positivNumbers,'product_id','rejected_products','Duplicate Primary Key Found')

    final_df_products=addTimeToSilverTable(df_NocheckDuplicateKeys)
    try:
        engine = create_connection_sql_server() # atomic transaction(we send the same connection)
        with engine.begin() as conn:
            insert_into_sql_server_atomic(conn,final_df_products,'stage','products') # load the delta (changes or updates) into stage
            writeMergeAtomic(conn,stage_silver_query) # for setting updates and get the new records
    except Exception as e:
        print(f"We find error to load the customer table into silver {e}")
else:
    print("Products table is up to dated")