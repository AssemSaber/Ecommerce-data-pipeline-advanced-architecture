import os 
import sys
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from metadata.incremental_loading import getDiffDataFromTable,getLastLoadFromTable,getLastLoadFromMetaData,writeLastTimeToMetaData
from Extraction.database import read_table_from_sql_server
from Loading.database import insert_into_sql_server,deleteOldOrders,insert_into_sql_server_atomic
from Connections.database import create_connection_sql_server
from sqlalchemy import text
from datetime import datetime, date

# gold
# id c1 c2 c3 ...cn >> updates>>> id c1 c2  c3 ... cn 
#   1  3   4                      10    20  30   same values
#silver
#   c1 c2 c3  >> mapping>> c1 c2 c3  
#   1- 3- 43-              10  20  30
# create mapping for the dates only in silver 
# update all values of dates in gold with values of date 

def mergeOldNewOrders(df_oldOrders,df_new_mapping_date):
    merged = df_oldOrders.merge(
        df_new_mapping_date,
        on="order_id",
        how="inner",
        suffixes=("_old", "_new")
    )
    return merged

def updateDifferentDates(mergedOldNewOrders):
    date_columns = [
        "order_purchase_date_sk",
        "order_approved_date_sk",
        "order_delivered_carrier_date_sk",
        "order_delivered_customer_date_sk",
        "order_estimated_delivery_date_sk"
    ]

    # drop the date_old and keep date_new
    old_columns = [f"{col}_old" for col in date_columns]
    updatedDateOrders = mergedOldNewOrders.drop(
        columns=old_columns
    )
    # rename them to get rid of _new
    rename_columns = {
        f"{col}_new": col
        for col in date_columns
    }
    updatedDateOrders = updatedDateOrders.rename(columns=rename_columns)
    # reorder the columns 
    updatedDateOrders=updatedDateOrders[[
        "order_id",
        "customer_sk",
        "product_sk",
        "seller_sk",
        "payment_sk",
        "order_purchase_date_sk",
        "order_approved_date_sk",
        "order_delivered_carrier_date_sk",
        "order_delivered_customer_date_sk",
        "order_estimated_delivery_date_sk",
        "price",
        "freight_value",
        "review_score",
    ]]
    # print(updatedDateOrders.columns)
    return updatedDateOrders



def mappingUpdatesFactTable(denormalizedTable):
    dim_date="""
        select 
            date_sk,
            full_date
            from gold.dim_date
    """
    gold_date = read_table_from_sql_server(dim_date)
    gold_date["full_date"] = pd.to_datetime(
        gold_date["full_date"],
        errors="coerce"
    ).dt.normalize()
    tables_primary_keys = {
 
        "order_purchase": {
            "dataframe": gold_date,
            "primary_key": "full_date",
            "foreign_key_in_other_table": "order_purchase_timestamp",
            "surrogate_key": "order_purchase_date_sk",
        },

        "order_approved": {
            "dataframe": gold_date,
            "primary_key": "full_date",
            "foreign_key_in_other_table": "order_approved_at",
            "surrogate_key": "order_approved_date_sk",
        },

        "order_delivered_carrier_date": {
            "dataframe": gold_date,
            "primary_key": "full_date",
            "foreign_key_in_other_table": "order_delivered_carrier_date",
            "surrogate_key": "order_delivered_carrier_date_sk",
        },

        "order_delivered_customer_date": {
            "dataframe": gold_date,
            "primary_key": "full_date",
            "foreign_key_in_other_table": "order_delivered_customer_date",
            "surrogate_key": "order_delivered_customer_date_sk",
        },

        "order_estimated_delivery_date": {
            "dataframe": gold_date,
            "primary_key": "full_date",
            "foreign_key_in_other_table": "order_estimated_delivery_date",
            "surrogate_key": "order_estimated_delivery_date_sk",
        },
    }

    
    gold_date["full_date"] = pd.to_datetime( # convert to date
                gold_date["full_date"],
                errors="coerce"
            ).dt.normalize()
    
    for table_name, config in tables_primary_keys.items():
        
        left_key = config["foreign_key_in_other_table"]

        denormalizedTable[left_key] = pd.to_datetime( # convert to date
                denormalizedTable[left_key],
                errors="coerce"
            ).dt.normalize()


        denormalizedTable = denormalizedTable.merge(
                config["dataframe"],
                right_on=config["primary_key"],
                left_on=config["foreign_key_in_other_table"],
                how='left'
            )
            # we rename the target date_sk to another meaningful name
        denormalizedTable = denormalizedTable.rename(
                    columns={ "date_sk": config["surrogate_key"] }
            )

        denormalizedTable.drop(
                columns=[config["foreign_key_in_other_table"],config["primary_key"]],
                inplace=True
            )

    # print(denormalizedTable.columns)
    # print(denormalizedTable)
    return denormalizedTable
# --- end functions

def getOldOrders(order_ids_list):
    order_ids = ",".join(
        f"'{order_id}'"
        for order_id in order_ids_list
    )
    # print(order_ids)
    old_order_query=f"""
    select 
        order_id ,
        customer_sk ,
        product_sk ,
        seller_sk  ,
        payment_sk ,
        order_purchase_date_sk ,
        order_approved_date_sk ,
        order_delivered_carrier_date_sk  ,
        order_delivered_customer_date_sk ,
        order_estimated_delivery_date_sk ,
        price,
        freight_value,
        review_score 
        from gold.fact_orders
        where order_id in ({order_ids})
    """
    return read_table_from_sql_server(old_order_query)


def DeltaTableSteps(table,columns,metdata_info):
    """
        - read the delta tables from silver layer
    """
    LastLoadFromMetaData=getLastLoadFromMetaData(table)
    LastLoadFromTable=getLastLoadFromTable(table)
    print(LastLoadFromTable,LastLoadFromMetaData)
    metdata_info[table] = {
        table: {
            "LastLoadFromMetaData": LastLoadFromMetaData,
            "LastLoadFromTable": LastLoadFromTable
        }
    }
    if LastLoadFromTable > LastLoadFromMetaData:
        delta_table=getDiffDataFromTable(columns,table) # we select the columns from silver layer.. look at DDL of silver
        # print("delta :",delta_table)
        return delta_table,metdata_info
    else: 
        print(f"{table} is up to date") # return empty df
        return pd.DataFrame(), metdata_info


def denormalizedTables(df_main_table,primary_key):
    """
        It merges order table with order_items, payment,and reviews to get one table
    """
    # the tables with forign keys
    tables_foreign_keys= {
        "order_items": {
            "dataframe": df_order_items,
            "foreign_key": "order_id_items"
        },
        "payments": {
            "dataframe": df_payments,
            "foreign_key": "order_id_payments"
        },
        "reviews": {
            "dataframe": df_reviews,
            "foreign_key": "order_id_reviews"
        }
    }
    for table_name, config in tables_foreign_keys.items():

        df_main_table = df_main_table.merge(
            config["dataframe"],
            left_on=primary_key,
            right_on=config["foreign_key"],
            how='inner'
        )

    # print(df_main_table.columns)
    return df_main_table

def mappingFactTable(denormalizedTable):
    dim_customers_query="""
        select 
            customer_sk,
            customer_id from gold.dim_customers
    """
    dim_products_query="""
        select 
            product_sk,
            product_id from gold.dim_products
            where is_current=1
    """
    dim_sellers_query="""
        select 
            seller_sk,
            seller_id from gold.dim_sellers
    """
    dim_status_payments="""
        select 
            payment_sk,
            payment_type,
            order_status
            from gold.status_payments
    """
    dim_date="""
        select 
            date_sk,
            full_date
            from gold.dim_date
    """
    gold_customers = read_table_from_sql_server(dim_customers_query)
    gold_products = read_table_from_sql_server(dim_products_query)
    gold_sellers = read_table_from_sql_server(dim_sellers_query)
    gold_status_payments = read_table_from_sql_server(dim_status_payments)
    gold_date = read_table_from_sql_server(dim_date)

    gold_date["full_date"] = pd.to_datetime(
        gold_date["full_date"],
        errors="coerce"
    ).dt.normalize()

    tables_primary_keys = {
        "customers" : {
            "dataframe":  gold_customers,
            "primary_key": "customer_id",
            "foreign_key_in_other_table": "customer_id",
            "surrogate_key": "customer_sk",
            "is_date": False
        },
        "products": {
            "dataframe": gold_products,
            "primary_key":"product_id",
            "foreign_key_in_other_table":"product_id",
            "surrogate_key": "product_sk",
            "is_date": False

        },
        "sellers": {
            "dataframe": gold_sellers,
            "primary_key": "seller_id",
            "foreign_key_in_other_table":"seller_id",
            "surrogate_key": "seller_sk",
            "is_date": False
        },
        "order_status":{
            "dataframe": gold_status_payments,
            "primary_key":["payment_type","order_status"],
            "foreign_key_in_other_table":["payment_type","order_status"],
            "surrogate_key": "order_status_sk",
            "is_date": False
        },

        "order_purchase": {
            "dataframe": gold_date,
            "primary_key": "full_date",
            "foreign_key_in_other_table": "order_purchase_timestamp",
            "surrogate_key": "order_purchase_date_sk",
            "is_date": True
        
        },

        "order_approved": {
            "dataframe": gold_date,
            "primary_key": "full_date",
            "foreign_key_in_other_table": "order_approved_at",
            "surrogate_key": "order_approved_date_sk",
            "is_date": True
        },

        "order_delivered_carrier_date": {
            "dataframe": gold_date,
            "primary_key": "full_date",
            "foreign_key_in_other_table": "order_delivered_carrier_date",
            "surrogate_key": "order_delivered_carrier_date_sk",
            "is_date": True
        },

        "order_delivered_customer_date": {
            "dataframe": gold_date,
            "primary_key": "full_date",
            "foreign_key_in_other_table": "order_delivered_customer_date",
            "surrogate_key": "order_delivered_customer_date_sk",
            "is_date": True
        },

        "order_estimated_delivery_date": {
            "dataframe": gold_date,
            "primary_key": "full_date",
            "foreign_key_in_other_table": "order_estimated_delivery_date",
            "surrogate_key": "order_estimated_delivery_date_sk",
            "is_date": True
        },
    }

    
    for table_name, config in tables_primary_keys.items():
            # Cast foreign key to datetime
        if config["is_date"]:
            left_key = config["foreign_key_in_other_table"]
            denormalizedTable[left_key] = pd.to_datetime(
                denormalizedTable[left_key],
                errors="coerce"
            ).dt.normalize()

        denormalizedTable = denormalizedTable.merge(
            config["dataframe"],
            right_on=config["primary_key"],
            left_on=config["foreign_key_in_other_table"],
            how='left'
        )
        # we rename the target date_sk to another meaningful name
        denormalizedTable = denormalizedTable.rename(
                columns={ "date_sk": config["surrogate_key"] }
         )

        columns_to_drop = config["foreign_key_in_other_table"]
        # we check columns to drop like "custommer_id" directly or something like ["order_status","payment_type"], which is list
        if isinstance(columns_to_drop, str): # if yes, write it inside [], No>> it's already list
            columns_to_drop = [columns_to_drop]
            columns_to_drop.append(config['primary_key']) # just string always
        else: # we have list pk and fk
            columns_to_drop.extend(config['primary_key']) # we need to add content of list
        # we drop the primary as we don't after merge 
        denormalizedTable.drop(
            columns=columns_to_drop,
            inplace=True
        )

    # print(denormalizedTable.columns)
    return denormalizedTable
# --- end functions

payment_columns=[
        'order_id',
        'payment_type'
]

order_columns=[
        'order_id',
        'customer_id',
        'order_status',
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date',
        'is_updated'

]

order_items=[
        'order_item_id',
        'order_id',
        'product_id',
        'seller_id',
        'shipping_limit_date',
        'price',
        'freight_value'
]

review_columns=[
        'review_id',
        'order_id',
        'review_score'
]

metadata={}
df_orders,metadata = DeltaTableSteps('orders',order_columns,metadata)

df_reviews,metadata=DeltaTableSteps('reviews',review_columns,metadata)
df_reviews = df_reviews.rename(columns={ # we rename the columns to avoid the same names in two tables (_x,_y)
    'order_id': 'order_id_reviews'
})
df_order_items,metadata=DeltaTableSteps('order_items',order_items,metadata)
df_order_items = df_order_items.rename(columns={
    'order_id': 'order_id_items'
})
df_payments,metadata=DeltaTableSteps('payments',payment_columns,metadata)
# print("payments",df_payments)
df_payments = df_payments.rename(columns={
    'order_id': 'order_id_payments'
})

if not df_orders.empty:

    df_updated_orders=df_orders[df_orders["is_updated"] == 1] # selecting updated orders
    df_new_orders=df_orders[df_orders["is_updated"] != 1] # selecting new orders
    if not df_updated_orders.empty:
            # 1- mapping all order 2- get all order_ids to compare with old orders 3-compare date_sk 4-update the date if there are differences
        df_new_mapping_date=mappingUpdatesFactTable(df_updated_orders) # mapping all coming dates to dates_sk
        order_ids_list = df_new_mapping_date["order_id"].dropna().unique().tolist() # get all order_ids 
        df_oldOrders=getOldOrders(order_ids_list) # get all old orders
        mergedOldNewOrders=mergeOldNewOrders(df_oldOrders,df_new_mapping_date)
        df_updatedOrders=updateDifferentDates(mergedOldNewOrders)
        
        try:
            engine = create_connection_sql_server() # delete and insert from into fact table as atomic transaction
            with engine.begin() as conn:
                deleteOldOrders(conn,order_ids_list)
                insert_into_sql_server_atomic(conn,df_updatedOrders,'gold','fact_orders','append')
        except Exception as e:
            print(f"Couldn't delete or insert the updated orders with {e}")
    else:
        print("Fact orders does not contain any updated orders")
    
    if not df_new_orders.empty:
        df_denormalizedTables=denormalizedTables(df_new_orders,'order_id')
        # select some columns before mapping to get the surrogate key
        df_denormalizedTables=df_denormalizedTables[[
            'order_id',
            'customer_id',
            'product_id',
            'seller_id',
            'order_status',
            'order_purchase_timestamp',
            'order_approved_at',
            'order_delivered_carrier_date',
            'order_delivered_customer_date',
            'order_estimated_delivery_date',
            'price',
            'freight_value',
            'payment_type',
            'review_score'
        ]]
        # print(df_denormalizedTables.columns)
        df_mappingFact=mappingFactTable(df_denormalizedTables)
        # select to reorder the columns
        df_mappingFact=df_mappingFact[[
            'order_id',
            'customer_sk',
            'product_sk',
            'seller_sk',
            'payment_sk',
            'order_purchase_date_sk',
            'order_approved_date_sk', 
            'order_delivered_carrier_date_sk',
            'order_delivered_customer_date_sk',
            'order_estimated_delivery_date_sk',
            'price',
            'freight_value', 
            'review_score'
        ]]
        print(df_mappingFact.columns)
        try:
            is_loaded=insert_into_sql_server(df_mappingFact,'gold','fact_orders','append')
            if is_loaded:
                for table, load_info in metadata.items():
                    print("metadata written ",table," ",load_info[table]['LastLoadFromTable'])
                    writeLastTimeToMetaData(table,load_info[table]['LastLoadFromTable'])
                    print("we have successfully updated the orders")
        except Exception as e:
            print(f"there is unexpected error {e}") 
    else:
        print("Fact orders does not contain new orders or updated orders")
else:
    print("fact orders is up to date")
