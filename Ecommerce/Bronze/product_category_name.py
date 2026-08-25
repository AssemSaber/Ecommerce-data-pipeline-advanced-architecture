import os 
import sys
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from Extraction.files import read_csv
from Loading.database import insert_into_sql_server


df_Products = read_csv(r"H:\Atos\Ecommerce Dataset\product_category_name_translation.csv")
insert_into_sql_server(df_Products, 'bronze','product_category_name_translation')