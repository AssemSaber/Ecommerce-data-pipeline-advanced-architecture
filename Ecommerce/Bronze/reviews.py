import os 
import sys
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from Extraction.apis import getFromAPI
from Loading.database import insert_into_sql_server


# df_Reviews = read_csv(r"H:\Atos\Ecommerce Dataset\olist_order_reviews_dataset.csv")
df_Reviews=getFromAPI('order-reviews')
print('=================================')
print('readed reviews assem')
print(df_Reviews)
print('=================================')
insert_into_sql_server(df_Reviews, 'bronze','reviews')