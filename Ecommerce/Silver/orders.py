import os 
import sys
import pandas as pd
from datetime import datetime
sys.path.append("H:\\Atos\\RootPackage")
from DataQuality.Check_Keys import *
from DataQuality.numbericValues import checkPositiveValues,checkRangeValues
from Extraction.database import read_table_from_sql_server
from Loading.database import insert_into_sql_server,insert_into_sql_server_atomic,writeMergeAtomic
from DataQuality.numbericValues import checkLowCardinalityValues
from metadata.incremental_loading import addTimeToSilverTable
from Connections.database import create_connection_sql_server




def checkColumnsNull(df): 
    first_df=checkNullKeys(df,'order_id','rejected_orders','Primary Key Missing Value')
    second_df=checkNullKeys(df,'customer_id','rejected_orders','Foreign Key for customer_id Missing Value')
    second_df=checkNullKeys(df,'order_status','rejected_orders','order_status Missing Value')
    return second_df



order_query="""
    SELECT
        b.order_id,
        b.customer_id,
        b.order_status,
        b.order_purchase_timestamp,
        b.order_approved_at,
        b.order_delivered_carrier_date,
        b.order_delivered_customer_date,
        b.order_estimated_delivery_date
    FROM bronze.orders AS b
    LEFT JOIN silver.orders AS s
        ON b.order_id = s.order_id
   WHERE
    s.order_id IS NULL

    OR ISNULL(b.customer_id, '') <> ISNULL(s.customer_id, '')

    OR ISNULL(b.order_status, '') <> ISNULL(s.order_status, '')

    OR ISNULL(
        TRY_CONVERT(DATETIME2, b.order_purchase_timestamp, 103),
        '1900-01-01'
    ) <> ISNULL(
        s.order_purchase_timestamp,
        '1900-01-01'
    )

    OR ISNULL(
        TRY_CONVERT(DATETIME2, b.order_approved_at, 103),
        '1900-01-01'
    ) <> ISNULL(
        s.order_approved_at,
        '1900-01-01'
    )

    OR ISNULL(
        TRY_CONVERT(DATETIME2, b.order_delivered_carrier_date, 103),
        '1900-01-01'
    ) <> ISNULL(
        s.order_delivered_carrier_date,
        '1900-01-01'
    )

    OR ISNULL(
        TRY_CONVERT(DATETIME2, b.order_delivered_customer_date, 103),
        '1900-01-01'
    ) <> ISNULL(
        s.order_delivered_customer_date,
        '1900-01-01'
    )

    OR ISNULL(
        TRY_CONVERT(DATETIME2, b.order_estimated_delivery_date, 103),
        '1900-01-01'
    ) <> ISNULL(
        s.order_estimated_delivery_date,
        '1900-01-01'
    );
"""

stage_silver_query="""
MERGE INTO silver.orders AS target
USING stage.orders AS source
    ON target.order_id = source.order_id

WHEN MATCHED AND (
    ISNULL(target.customer_id, '') <> ISNULL(source.customer_id, '')

    OR ISNULL(target.order_status, '') <> ISNULL(source.order_status, '')

    OR ISNULL(target.order_purchase_timestamp, '1900-01-01') <> ISNULL(source.order_purchase_timestamp, '1900-01-01')

    OR ISNULL(target.order_approved_at, '1900-01-01') <> ISNULL(source.order_approved_at, '1900-01-01')

    OR ISNULL(target.order_delivered_carrier_date, '1900-01-01') <> ISNULL(source.order_delivered_carrier_date, '1900-01-01')

    OR ISNULL(target.order_delivered_customer_date, '1900-01-01') <> ISNULL(source.order_delivered_customer_date, '1900-01-01')

    OR ISNULL(target.order_estimated_delivery_date, '1900-01-01') <> ISNULL(source.order_estimated_delivery_date, '1900-01-01')
)
THEN
    UPDATE SET
        target.customer_id = source.customer_id,
        target.order_status = source.order_status,
        target.order_purchase_timestamp = source.order_purchase_timestamp,
        target.order_approved_at = source.order_approved_at,
        target.order_delivered_carrier_date = source.order_delivered_carrier_date,
        target.order_delivered_customer_date = source.order_delivered_customer_date,
        target.order_estimated_delivery_date = source.order_estimated_delivery_date,
        target.is_updated=1,
        target.load_timestamp = source.load_timestamp

WHEN NOT MATCHED BY TARGET
THEN
    INSERT (
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp,
        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date,
        load_timestamp
    )
    VALUES (
        source.order_id,
        source.customer_id,
        source.order_status,
        source.order_purchase_timestamp,
        source.order_approved_at,
        source.order_delivered_carrier_date,
        source.order_delivered_customer_date,
        source.order_estimated_delivery_date,
        source.load_timestamp
    );
"""

customer_query="""
    select customer_id
     from silver.customers
"""

main_columns_of_orders=[
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
        ]

valid_order_status = [
    "approved",
    "delivered",
    "created",
    "invoiced",
    "processing",
    "unavailable",
    "canceled",
    "shipped"
]

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

start = datetime.now()
print("Before:", start)

df_orders = read_table_from_sql_server(order_query)

if not df_orders.empty:
    for col in date_columns:
        df_orders[col] = pd.to_datetime(
            df_orders[col],
            format="%d/%m/%Y %H:%M",
            errors="coerce"
        )
        
    df_orders_not_null=checkColumnsNull(df_orders)
    df_NocheckDuplicateKeys=checkDuplicateKeys(df_orders_not_null,'order_id','rejected_orders','Duplicate Primary Key Found')
    
    df_customers = read_table_from_sql_server(customer_query)
    # print(df_orders,df_customers)
    df_orders_reference_customer= checkColumnsReference(
        df_NocheckDuplicateKeys,
        'customer_id',
        df_customers,
        'customer_id',
        main_columns_of_orders,
        'rejected_orders')

    validOrderStatus=checkLowCardinalityValues(df_orders_reference_customer,"order_status",valid_order_status,"rejected_orders","Not Exptected order status")
    final_df_orders=addTimeToSilverTable(validOrderStatus)
    try:
        engine = create_connection_sql_server() # atomic transaction(we send the same connection)
        with engine.begin() as conn:
            insert_into_sql_server_atomic(conn,final_df_orders,'stage','orders')
            writeMergeAtomic(conn,stage_silver_query)
            end = datetime.now()
            print("After:", end)
            print("Difference:", end - start)
    except Exception as e:
        print(f"We find error to load the order table into silver{e}")

else:
    print("order table is up to dated")