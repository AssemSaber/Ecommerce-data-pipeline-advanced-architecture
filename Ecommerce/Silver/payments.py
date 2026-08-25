import os 
import sys
import pandas as pd
from datetime import datetime
sys.path.append("H:\\Atos\\RootPackage")
from DataQuality.Check_Keys import *
from DataQuality.numbericValues import checkPositiveValues,checkRangeValues
from Extraction.database import read_table_from_sql_server
from Loading.database import insert_into_sql_server,insert_into_sql_server_atomic,writeMergeAtomic
from metadata.incremental_loading import addTimeToSilverTable
from DataQuality.numbericValues import checkLowCardinalityValues
from Connections.database import create_connection_sql_server


def checkColumnsNull(df): 

    first_df=checkNullKeys(df,'order_id','rejected_payments','Primary Key Missing Value')
    second_df=checkNullKeys(first_df,'payment_installments','rejected_payments','payment_installments Missing Value')
    thrid_df=checkNullKeys(second_df,'payment_type','rejected_payments','payment_type Missing Value')
    fourth_df=checkNullKeys(thrid_df,'payment_value','rejected_payments','payment_value Missing Value')
    return fourth_df



payment_query="""
SELECT
    b.order_id,
    b.payment_sequential,
    b.payment_type,
    b.payment_installments,
    b.payment_value

FROM bronze.payments AS b
LEFT JOIN silver.payments AS s
    ON b.order_id = s.order_id
WHERE
    s.order_id IS NULL
    --- it's just append row and No modification here
"""

order_query="""
    select order_id
     from silver.orders
"""

order_query="""
    select order_id
     from silver.orders
"""

main_columns_of_orders=[
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value"
        ]

valid_payment_type = [
"credit_card",
"debit_card",
"boleto",
"voucher"
]

start = datetime.now()
print("Before:", start)

df_payments = read_table_from_sql_server(payment_query)

if not df_payments.empty:
    df_payments_not_null=checkColumnsNull(df_payments)
    df_orders = read_table_from_sql_server(order_query)
    # print(df_orders,df_customers)
    df_payments_reference_customer= checkColumnsReference(
        df_payments_not_null,
        'order_id',
        df_orders,
        'order_id',
        main_columns_of_orders,
        'rejected_payments')

    validPaymentType=checkLowCardinalityValues(df_payments_reference_customer,"payment_type",valid_payment_type,"rejected_payments","Not Exptected payment type")
    final_df_payments=addTimeToSilverTable(validPaymentType)
    try:
        engine = create_connection_sql_server() # atomic transaction(we send the same connection)
        with engine.begin() as conn:
            insert_into_sql_server_atomic(conn,final_df_payments,'silver','payments',"append")
            # writeMergeAtomic(conn,stage_silver_query)
            end = datetime.now()
            print("After:", end)
            print("Difference:", end - start)
    except Exception as e:
        print(f"We find error to load the order table into silver{e}")

else:
    print("payment table is up to dated")