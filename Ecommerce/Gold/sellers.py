import os 
import sys
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from metadata.incremental_loading import getDiffDataFromTable,getLastLoadFromTable,getLastLoadFromMetaData,writeLastTimeToMetaData
from Extraction.database import read_table_from_sql_server
from Loading.database import insert_into_sql_server
from DataQuality.Check_Keys import SelectColumns
from Connections.database import create_connection_sql_server
from sqlalchemy import text


def updatedCustomers(merged):
    """
    - It starts with the merged dataframe between silver and gold
    - compares the column values
    - updates if there are changes
    """
    # filter existing rows in silver and gold
    merged = merged[merged["_merge"] == "both"].copy()

    tracked_columns=[
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
            "is_delete"
    ]
    
    # FALSE | [TRUE, FALSE,TRUE] to keep only the changed rows
    changed_mask = False

    for col in tracked_columns:
        changed_mask |= (
            merged[f"{col}_silver"] != merged[f"{col}_gold"]
        )

    updated_sellers = merged[ changed_mask ]

    if not updated_sellers.empty:
        # :customer_unique_id reference customer_unique_id in silver
        update_query = text("""
            UPDATE gold.dim_sellers
            SET
                seller_zip_code_prefix = :seller_zip_code_prefix,
                seller_city = :seller_city,
                seller_state = :seller_state,
                is_delete= :is_delete
            WHERE seller_id = :seller_id
        """)

        engine = create_connection_sql_server()
        with engine.begin() as connection:
            # customer_id: take the of the row and forward to above
            for _, row in updated_sellers.iterrows():
                connection.execute(
                    update_query,
                    {
                         # we got the values of rows in these variables
                        "seller_id":
                            row["seller_id"],

                        "seller_zip_code_prefix":
                            row["seller_zip_code_prefix_silver"],

                        "seller_city":
                            row["seller_city_silver"],

                        "seller_state":
                            row["seller_state_silver"],
                        "is_delete":
                            row["is_delete_silver"]
                    }
                )

def insertNewCustomers(merged):

    new_customers = merged[merged["_merge"] == "left_only"].copy()
    # print(new_customers)
    #select the needed columns after making merge statement (we have extra _silver)
    new_customers = new_customers[
        [
            "seller_id",
            "seller_zip_code_prefix_silver",
            "seller_city_silver",
            "seller_state_silver",
            "is_delete_silver"
        ]
    ]

    # rename the columns to git rid of _sliver 
    new_customers.columns = [
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
            "is_delete"

    ]
    insert_into_sql_server(new_customers,'gold','dim_sellers','append')

#  end functions

# columns passed to select the columns in the delta
columns=[
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
        "is_delete"
]

dim_seller_query="""
    SELECT
        seller_id,
        seller_zip_code_prefix,
        seller_city,
        seller_state,
        is_delete
    FROM gold.dim_sellers
"""
LastLoadFromMetaData=getLastLoadFromMetaData('sellers')
LastLoadFromTable=getLastLoadFromTable('sellers')
print(LastLoadFromTable,LastLoadFromMetaData)

if LastLoadFromTable > LastLoadFromMetaData:
    seller_delta=getDiffDataFromTable(columns,"sellers")
    print(seller_delta)
    gold_sellers = read_table_from_sql_server(dim_seller_query)
    merged = seller_delta.merge(
        gold_sellers,
        on="seller_id",
        how="left",
        suffixes=("_silver", "_gold"),
        indicator=True
    )

    insertNewCustomers(merged)
    updatedCustomers(merged)
    writeLastTimeToMetaData('sellers',LastLoadFromTable) # commit last time to metadata
    # -------------------------------
else:
    print("Sellers in gold layer is up to date")
