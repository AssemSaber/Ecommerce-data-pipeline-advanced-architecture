import sys
import pandas as pd
sys.path.append("H:\\Atos\\RootPackage")
# from Connections.database import insert_data_to_sql_server,create_connection_sql_server
from Loading.database import insert_data_to_sql_server
from Loading.logJson import write_rejected_summary_to_json



def joinForeignKeysReference(df_with_fk,fk_name,df_with_pk,pk_name):
    # from Extraction.files import read_csv
    # df_with_pk = read_csv(rf"C:\Users\Moham\Downloads\{df_with_pk}.csv")
    
    df_with_pk=df_with_pk.rename(columns={pk_name: f"{pk_name}_right"}) # to keep the column name unique for the merge operation instead of one column with the same name
    df_with_fk=df_with_fk.rename(columns={fk_name: f"{fk_name}_left"})
    # print("===============")
    # print(df_with_fk.columns)
    # print(df_with_pk.columns)
    # print("===============")
    df_result = df_with_fk.merge(
    df_with_pk,
    left_on=f"{fk_name}_left",
    right_on=f"{pk_name}_right",
    how="left"
    )
    return df_result # 

        
def insertMessageReason(df, rejected_table, message):
    try:
            df["reason"] = message
            insert_data_to_sql_server(df, rejected_table,'append')
            write_rejected_summary_to_json(df,rejected_table.split("_", 1)[1])


    except Exception as e:
        print(f"Error inserting bad references: {e}")


def checkNullKeys(df, columnName,rejected_table,message):
    # Check for missing values in the column
    missing_values = df[columnName].isna().sum()
    badDf=df[df[columnName].isna()] # we filter the df with only null
    goodDf=df[df[columnName].notna()] #
    if missing_values > 0:
        insertMessageReason(badDf, rejected_table, message)

    return goodDf
    

def checkDuplicateKeys(df, columnName, rejected_table, message):
    """
        It takes copy of dataframe based on the column name
        and insert the duplicate rows into the rejected table with the reason
    """
    dup_mask = df.duplicated(subset=columnName, keep="first")

    duplicated_df = df[dup_mask].copy()
    not_duplicated_df = df[~dup_mask].copy()

    if not duplicated_df.empty:
        insertMessageReason(duplicated_df, rejected_table, message)

    return not_duplicated_df


def getBadReferences(dfAfterMerge,fk_name,pk_name):
    """"
        get bad references from the dataframe after the merge statement 
        and keep in mind, that contains all columns of the merge
    """
    badReference = dfAfterMerge[dfAfterMerge[f"{pk_name}_right"].isna()] # take the df with null in the right column after the merge statement
    print(badReference)
    badReference = badReference.rename(columns={f"{fk_name}_left": fk_name}) # Rename (fk) to match the column name  in the rejected table
    return badReference

def getGoodReferences(dfAfterMerge,fk_name,pk_name):
    """"
        get good references from the dataframe after the merge statement 
        and keep in mind, that contains all columns of the merge
    """
    goodReference = dfAfterMerge[dfAfterMerge[f"{pk_name}_right"].notna()] # take the df with not null in the right column after the merge statement
    goodReference = goodReference.rename(columns={f"{fk_name}_left": fk_name}) #Rename (fk) to match the column name in the origin table
    return goodReference


def SelectColumns(df, columns):
    selectedColumns = df[columns]  # select columns from the dataframe after merge statement to insert into the rejected table
    return selectedColumns

def checkColumnsReference(df_with_fk,fk_name,table_with_pk,pk_name,columns,rejected_table):
    """"
        join the dataframes of PK and FK (merge)
        get the good and bad references
        select some columns after merge statement
    """
    dfWithReference = joinForeignKeysReference(df_with_fk,fk_name,table_with_pk,pk_name)
    df_badReferences = getBadReferences(dfWithReference,fk_name,pk_name)
    df_goodReferences = getGoodReferences(dfWithReference,fk_name,pk_name)
    selectedColumnsForGoodReferences = SelectColumns(df_goodReferences, columns)  # select columns from the dataframe after merge statement to insert into the rejected table
    selectedColumnsForBadReferences = SelectColumns(df_badReferences, columns)  # select columns from the dataframe after merge statement to insert into the rejected table
    if not selectedColumnsForBadReferences.empty:
        insertMessageReason(selectedColumnsForBadReferences,rejected_table,f'Invalid Foreign Key Reference for {fk_name}')
    return selectedColumnsForGoodReferences
  

    # with hardcoded
    # dfWithReferenceToMatchID=joinForeignKeysReference(df_playerID_with_not_null,'MatchID','Matches','MatchID')
    # df_MatchID_with_null = dfWithReferenceToMatchID[dfWithReferenceToMatchID["MatchID_right"].isna()].copy()
    # df_MatchID_with_not_null = dfWithReferenceToMatchID[dfWithReferenceToMatchID["MatchID_right"].notna()].copy()
    # df_MatchID_with_null = df_MatchID_with_null.rename(columns={"MatchID_left": "MatchID"}) # to match the column name in the rejected table
    # df_MatchID_with_not_null = df_MatchID_with_not_null.rename(columns={"MatchID_left": "MatchID"}) # to match the column name in the rejected table
    # df_MatchID_with_null = df_MatchID_with_null[["StatID", "PlayerID", "MatchID","Goals","Assists","YellowCards","RedCards","MinutesPlayed"]]
    # df_MatchID_with_not_null = df_MatchID_with_not_null[["StatID", "PlayerID", "MatchID","Goals","Assists","YellowCards","RedCards","MinutesPlayed"]]

    # insertMessageReason(df_MatchID_with_null,"rejected_PlayerStats",'Invalid Foreign Key Reference for MatchID')

