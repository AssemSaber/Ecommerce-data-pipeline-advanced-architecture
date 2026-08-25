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
    main_columns_of_products = [
    "product_id",
    "order_id",
    "seller_id"
    ]
    for col in main_columns_of_products:
        checkNullKeys(df,col,'rejected_order_items',f'{col} Missing Value')
        
    return df

def checkPositiveNumbers(df):
    exptectPositvieColumns = [
    "freight_value",
    "price"
    ]
    for col in exptectPositvieColumns:
        checkPositiveValues(df,col,"rejected_order_items",f"Negative Value in {col}")
    return df

def checkReferences(df_order_items,main_columns_of_order_items):
    product_query="""
    select product_id
     from silver.products
    """
    order_query="""
        select order_id
        from silver.orders
    """
    seller_query="""
        select seller_id
        from silver.sellers
    """
        # check reference from product_id to (products) product_id
    df_products = read_table_from_sql_server(product_query)
    validReferenceItemsToProducts= checkColumnsReference(
        df_order_items,
        'product_id',
        df_products,
        'product_id',
        main_columns_of_order_items,
        'rejected_order_items')

    df_orders = read_table_from_sql_server(order_query)
    validReferenceItemsToOrders= checkColumnsReference(
        validReferenceItemsToProducts,
        'order_id',
        df_orders,
        'order_id',
        main_columns_of_order_items,
        'rejected_order_items')

    df_sellers = read_table_from_sql_server(seller_query)
    validReferenceItemsToSellers= checkColumnsReference(
        validReferenceItemsToOrders,
        'seller_id',
        df_sellers,
        'seller_id',
        main_columns_of_order_items,
        'rejected_order_items')

    return validReferenceItemsToSellers
#  we get the delta (insertion)
order_items_query = """

    SELECT
        b.order_id,
        b.order_item_id ,
        b.product_id,
        b.seller_id,
        b.shipping_limit_date,
        b.price,
        b.freight_value
    FROM bronze.order_items AS b
    LEFT JOIN silver.order_items AS s
        ON b.order_id = s.order_id
        AND b.order_item_id = s.order_item_id
    WHERE
        s.order_id IS NULL

"""


main_columns_of_order_items = [
    "order_id",
    "order_item_id",
    "product_id",
    "seller_id",
    "shipping_limit_date",
    "price",
    "freight_value"
]


df_order_items = read_table_from_sql_server(order_items_query)

if not df_order_items.empty:
    df_order_items['shipping_limit_date'] = pd.to_datetime(
            df_order_items['shipping_limit_date'],
            format="%d/%m/%Y %H:%M",
            errors="coerce"
        )
    df_order_items_not_null=checkColumnsNull(df_order_items)
    withValidReferences=checkReferences(df_order_items_not_null,main_columns_of_order_items)
    withPositiveNumbers=checkPositiveNumbers(withValidReferences)
    final_df_order_items=addTimeToSilverTable(withPositiveNumbers)
    try:
        engine = create_connection_sql_server() # atomic transaction(we send the same connection)
        with engine.begin() as conn:
            insert_into_sql_server_atomic(conn,final_df_order_items,'silver','order_items','append') # load the delta (changes or updates) into stage
            # writeMergeAtomic(conn,stage_silver_query)
        # insert_into_sql_server(load_delta_into_silver,'silver','customers','append') # upsert the stage with silver
    except Exception as e:
        print(f"We find error to load the customer table into silver {e}")

else:
    print("Customer table is up to dated")