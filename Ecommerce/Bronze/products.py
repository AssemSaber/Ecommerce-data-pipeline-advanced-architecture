import os 
import sys
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from Extraction.files import read_csv
from Loading.database import insert_into_sql_server

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

df_Products = read_csv(r"H:\Atos\Ecommerce Dataset\olist_products_dataset.csv")
# df_products_mapping=getMappingProductCategory(df_Products)
insert_into_sql_server(df_Products, 'bronze','products')