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
    # filter with both
    merged = merged[merged["_merge"] == "both"].copy()

    tracked_columns=[
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state"
    ]
    
    # FALSE | [TRUE, FALSE,TRUE]
    changed_mask = False

    for col in tracked_columns:
        changed_mask |= (
            merged[f"{col}_silver"] != merged[f"{col}_gold"]
        )

    updated_customers = merged[ changed_mask ]

    if not updated_customers.empty:
        # :customer_unique_id reference customer_unique_id in silver
        update_query = text("""
            UPDATE gold.dim_customers
            SET
                customer_unique_id = :customer_unique_id,
                customer_zip_code_prefix = :customer_zip_code_prefix,
                customer_city = :customer_city,
                customer_state = :customer_state
            WHERE customer_id = :customer_id
        """)
        engine = create_connection_sql_server()
        with engine.begin() as connection:
            # customer_id: take the of the row and forward to above
            for _, row in updated_customers.iterrows():

                connection.execute(
                    update_query,
                    {
                        "customer_id":
                            row["customer_id"],

                        "customer_unique_id":
                            row["customer_unique_id_silver"],

                        "customer_zip_code_prefix":
                            row["customer_zip_code_prefix_silver"],

                        "customer_city":
                            row["customer_city_silver"],

                        "customer_state":
                            row["customer_state_silver"]
                    }
                )

def insertNewCustomers(merged):

    new_customers = merged[merged["_merge"] == "left_only"].copy()
    
    #select the wanted columns after making merge statement
    new_customers = new_customers[
        [
            "customer_id",
            "customer_unique_id_silver",
            "customer_zip_code_prefix_silver",
            "customer_city_silver",
            "customer_state_silver"
        ]
    ]

    # rename the columns to git rid of _sliver 
    new_customers.columns = [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state"
    ]
    insert_into_sql_server(new_customers,'gold','dim_customers','append')

#  end functions

columns=[
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state"
]

dim_customer_query="""
    SELECT
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state
    FROM gold.dim_customers
"""
LastLoadFromMetaData=getLastLoadFromMetaData('customers')
LastLoadFromTable=getLastLoadFromTable('customers')
print(LastLoadFromTable,LastLoadFromMetaData)
if LastLoadFromTable>LastLoadFromMetaData:
    customers_delta=getDiffDataFromTable(columns,"customers")
    print(customers_delta)
    gold_customers = read_table_from_sql_server(dim_customer_query)
    merged = customers_delta.merge(
        gold_customers,
        on="customer_id",
        how="left",
        suffixes=("_silver", "_gold"),
        indicator=True
    )

    insertNewCustomers(merged)
    updatedCustomers(merged)
    writeLastTimeToMetaData('customers',LastLoadFromTable) # commit last time to metadata
    # -------------------------------
else:
    print("Customers in gold layer is up to date")


# what occured after merge, 
# suffixes when the same column have same name, pandas add _x,_y, but we need meaningful names
# indicator=True >> write type both or left_only to determine which ones are new or updated
# customer_id | city_silver | state_silver | city_gold | state_gold | _merge
# ------------|-------------|--------------|-----------|------------|----------
# 1           | Cairo       | C            | Cairo     | C          | both
# 2           | Giza        | G            | Cairo     | C          | both
# 3           | Cairo       | C            | NaN       | NaN         | left_only

# changed_mask |= result  >>> changed_mask = changed_mask | result
# both the row exist in both >> left_only exist in the left


    # changed_mask = False

    # for col in tracked_columns:
    #     changed_mask |= (
    #         merged[f"{col}_silver"] != merged[f"{col}_gold"]
    #     )

    # updated_customers = merged[ changed_mask ]
# [city_silver]!=[city_gold] >>   [False,True]
                                     # OR
# [state_silver]!=[state_gold] >> [False,True]
                                # [False,True]
                                # so using changed_masked=True >> return changed