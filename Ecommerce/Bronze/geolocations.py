import os 
import sys
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from Extraction.files import read_csv
from Connections.database import insert_into_sql_server,create_connection_sql_server


df_Geolocations = read_csv(r"H:\Atos\Ecommerce Dataset\olist_geolocation_dataset.csv")
insert_into_sql_server(df_Geolocations, 'bronze','geolocations')