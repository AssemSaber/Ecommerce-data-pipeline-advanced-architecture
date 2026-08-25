import os 
import sys
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from Extraction.apis import getFromAPI
from Loading.database import insert_into_sql_server


# df_Payments = read_csv(r"H:\Atos\Ecommerce Dataset\olist_order_payments_dataset.csv")
# print(df_Payments.head())
df_Payments=getFromAPI('payments')
insert_into_sql_server(df_Payments, 'bronze','payments')