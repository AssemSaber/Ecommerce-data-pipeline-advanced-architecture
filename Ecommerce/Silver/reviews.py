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

    first_df=checkNullKeys(df,'review_id','rejected_customers','review_id Missing Value')
    second_df=checkNullKeys(df,'review_score','rejected_customers','review_score Missing Value')
    return second_df



review_query="""
SELECT
        b.review_id,
        b.order_id,
        b.review_score,
        b.review_creation_date,
        b.review_answer_timestamp
    FROM bronze.reviews AS b
    LEFT JOIN silver.reviews AS s
        ON b.review_id = s.review_id
    WHERE
        s.review_id IS NULL;
"""
order_query="""
    select order_id
     from silver.orders
"""


main_columns_of_reviews = [
    "review_id",
    "order_id",
    "review_score",
    "review_creation_date",
    "review_answer_timestamp"
]

df_reviews = read_table_from_sql_server(review_query)

if not df_reviews.empty:
    date_columns = [
    "review_creation_date",
    "review_answer_timestamp"
    ]
    for col in date_columns:
        df_reviews[col] = pd.to_datetime(
            df_reviews[col],
            format="%d/%m/%Y %H:%M",
            errors="coerce"
        )

    df_reviews_not_null=checkColumnsNull(df_reviews)
    positiveReviews=checkPositiveValues(df_reviews_not_null,"review_score","rejected_reviews","Negative review score")
    df_orders = read_table_from_sql_server(order_query)
    df_reviews_reference_customer= checkColumnsReference(
        df_reviews_not_null,
        'order_id',
        df_orders,
        'order_id',
        main_columns_of_reviews,
        'rejected_reviews')
    final_df_reviews=addTimeToSilverTable(df_reviews_reference_customer)
    try:
        engine = create_connection_sql_server() # atomic transaction(we send the same connection)
        with engine.begin() as conn:
            insert_into_sql_server_atomic(conn,final_df_reviews,'silver','reviews','append') 
    except Exception as e:
        print(f"We find error to load the customer table into silver {e}")

else:
    print("Customer table is up to dated")