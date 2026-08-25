import pandas as pd
import sys
sys.path.append("H:\\Atos\\RootPackage")
from Loading.database import insert_data_to_sql_server
from Loading.logJson import write_rejected_summary_to_json
from DataQuality.Check_Keys import insertMessageReason

def checkPositiveValues(df, columnName, rejected_table,message):
    goodDf=df[df[columnName]>=0].copy()
    badDf=df[df[columnName]<0].copy()
    # print("negative df",badDf)
    if not badDf.empty:
        insertMessageReason(badDf, rejected_table, message)
    return goodDf 


def checkRangeValues(df, columnName, minValue, maxValue, rejected_table,message):
    goodDf=df[(df[columnName]>=minValue) & (df[columnName]<=maxValue)].copy()
    badDf=df[(df[columnName]<minValue) | (df[columnName]>maxValue)].copy()
    if not badDf.empty:
        insertMessageReason(badDf, rejected_table, message)
    return goodDf


def checkLowCardinalityValues(df, columnName, arrValues, rejected_table, message):
    
    goodDf = df[df[columnName].isin(arrValues)].copy()

    badDf = df[~df[columnName].isin(arrValues)].copy()
    print("badOrderStatus",badDf)
    if not badDf.empty:
        insertMessageReason(badDf, rejected_table, message)
    return goodDf

