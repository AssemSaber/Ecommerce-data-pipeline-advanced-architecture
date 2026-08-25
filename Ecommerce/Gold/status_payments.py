import os 
import sys
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
from Extraction.database import read_table_from_sql_server
from Loading.database import insert_into_sql_server




def findNewCombinations(currentCombinations,dim_status_payments):
    new_combinations = currentCombinations.merge(
        dim_status_payments,
        on=["payment_type", "order_status"],
        how="left",
        indicator=True
    )

    new_combinations = new_combinations[
        new_combinations["_merge"] == "left_only"
    ].drop(columns="_merge")

    return new_combinations

def createCombinations():
    payment_type = [
    "credit_card",
    "debit_card",
    "boleto",
    "voucher"
    ]

    order_status = [
        "approved",
        "delivered",
        "created",
        "invoiced",
        "processing",
        "unavailable",
        "canceled",
        "shipped"
    ]

    df_payment = pd.DataFrame({
        "payment_type": payment_type
    })

    df_status = pd.DataFrame({
        "order_status": order_status
    })
    # applying junk dimension
    df = df_payment.merge(
        df_status,
        how="cross"
    )

    return df

# ---- end functions


dim_status_payments_query="""
    SELECT
        payment_type,
        order_status
    FROM gold.status_payments
"""

currentCombinations=createCombinations()
dim_status_payments=read_table_from_sql_server(dim_status_payments_query)

newCombinations=findNewCombinations(currentCombinations,dim_status_payments)
if not newCombinations.empty:
        insert_into_sql_server(newCombinations,'gold','status_payments','append')
