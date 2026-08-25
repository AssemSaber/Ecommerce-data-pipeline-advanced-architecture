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




def insertNewRecords(merged,scd_two=0):

    if not scd_two:
        merged = merged[merged["_merge"] == "left_only"].copy()
    # print(new_customers)
    #select the needed columns after making merge statement (we have extra _silver)
    merged = merged[
        [
        "product_id",
        "product_category_name_silver",
        "product_name_lenght_silver" ,
        "product_description_lenght_silver",
        "product_photos_qty_silver",
        "product_weight_g_silver",
        "product_length_cm_silver",
        "product_height_cm_silver",
        "product_width_cm_silver"
        ]
    ]

    # rename the columns to git rid of _sliver 
    merged.columns = [
        "product_id",
        "product_category_name",
        "product_name_lenght" ,
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"

    ]
    # adding current date for the new record
    merged["start_date"] = pd.Timestamp.now()
    
    insert_into_sql_server(merged,'gold','dim_products','append')

def setDelete(delete_only):

    if delete_only.empty:
        return

    update_query = text("""
        UPDATE gold.dim_products
        SET
            end_date = SYSDATETIME(),
            is_current = 0,
            is_delete = :is_delete
        WHERE product_id = :product_id
          AND is_current = 1
    """)

    engine = create_connection_sql_server()

    with engine.begin() as connection:

        for _, row in delete_only.iterrows():

            connection.execute(
                update_query,
                {
                    "product_id": row["product_id"],
                    "is_delete": row["is_delete_silver"]
                }
            )


def updatedRecords(merged):
    """
    - It starts with the merged dataframe between silver and gold
    - compares the column values
    - updates if there are changes
    """
    # filter existing rows in silver and gold
    merged = merged[merged["_merge"] == "both"].copy()

    tracked_columns=[
        "product_category_name",
        "product_name_lenght" ,
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]
    
    # FALSE | [TRUE, FALSE,TRUE] to keep only the changed rows
    changed_mask = False

    for col in tracked_columns: # () >> [true or false]
        changed_mask |= (
            merged[f"{col}_silver"] != merged[f"{col}_gold"]
        )

    changed_products = merged[ changed_mask ] # (only changed rows )

    delete_changed = ( merged["is_delete_silver"] != merged["is_delete_gold"] ) # () >> true or false

    delete_only = merged[ delete_changed & ~changed_mask ].copy() # row for deleted

    setDelete(delete_only)
    print("changed products: ",changed_products)
    print("deleted products: ",delete_only)
    if not changed_products.empty: # is_current=0 and call insertNewRecords
        # :customer_unique_id reference customer_unique_id in silver
        update_query = text("""
            UPDATE gold.dim_products
            SET
                end_date= SYSDATETIME(),
                is_current=0,
                is_delete = :is_delete
            WHERE product_id = :product_id AND is_current = 1
        """)
        engine = create_connection_sql_server()
        with engine.begin() as connection:
            # customer_id: take the of the row and forward to above
            for _, row in changed_products.iterrows():
                connection.execute(
                    update_query,
                    {
                         # for each row, we got the values of columns in these variables
                        "product_id":
                            row["product_id"],
                        "is_delete":
                            row["is_delete_silver"],
                    }
                )
        print("for insertion",changed_products)
        insertNewRecords(changed_products,1) # we send the changedRecords to be inserted
#  end functions

# columns passed to select the columns in the delta
columns=[
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g" ,
        "product_length_cm" ,
        "product_height_cm" ,
        "product_width_cm"  ,
        "is_delete"

]

dim_product_query="""
    SELECT
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g" ,
        "product_length_cm" ,
        "product_height_cm" ,
        "product_width_cm"  ,
        "is_delete"
    FROM gold.dim_products
    where is_current = 1
"""

LastLoadFromMetaData=getLastLoadFromMetaData('products')
LastLoadFromTable=getLastLoadFromTable('products')
print(LastLoadFromTable,LastLoadFromMetaData)

if LastLoadFromTable > LastLoadFromMetaData:
    product_delta=getDiffDataFromTable(columns,"products") # we got the columns from silver layer.. look at DDL of silver
    print("delta :",product_delta)
    gold_products = read_table_from_sql_server(dim_product_query)
    merged = product_delta.merge(
        gold_products,
        on="product_id",
        how="left",
        suffixes=("_silver", "_gold"),
        indicator=True
    )
    insertNewRecords(merged)
    print("inserted")
    updatedRecords(merged)
    print("first update")
    writeLastTimeToMetaData('products',LastLoadFromTable) # commit last time to metadata
    # -------------------------------
else:
    print("Products in gold layer is up to date")
