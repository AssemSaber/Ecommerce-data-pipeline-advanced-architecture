import os 
import sys
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from Extraction.files import read_csv
from Loading.database import insert_into_sql_server

df_OrderItems = read_csv(r"H:\Atos\Ecommerce Dataset\olist_order_items_dataset.csv")
insert_into_sql_server(df_OrderItems, 'bronze','order_items')