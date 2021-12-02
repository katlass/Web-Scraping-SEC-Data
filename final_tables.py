#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 10:25:09 2021

@author: m1kal01
"""

import pandas as pd
from itertools import chain
import datetime
import numpy as np
pd.options.display.max_columns=500
pd.options.display.max_rows=20

#Reading in data from pull_process.py
companies=pd.read_pickle('companies.pkl') #this comes from pull_process.py (it is all the compnaies you want to pull)

#Find closest business quarter to a date
def Closest_Quarter(target):
    candidates = [
        datetime.date(target.year - 1, 12, 31),
        datetime.date(target.year, 3, 31),
        datetime.date(target.year, 6, 30),
        datetime.date(target.year, 9, 30),
        datetime.date(target.year, 12, 31),
    ]
    answer=candidates[np.argmin(list(map(lambda x: abs(target -x),candidates)))]
    return (answer)

#-------------------------------------------------------------------------------------------------------------------------
#Finding the quarters reported in each file pulled, setting up lists of results as dicitonaries for compiler()
def SetUp_Compiler(All_Company_Quarters,All_Company_Cash,All_Company_CP,All_Company_CD):
    #-------------------------------------------------------------------------------------------------------------------------
    Period_of_report_dict=dict()
    Quarter_dict=dict() #initaliaze empty dictionary
    Clean_Quarters=[] #initialize empty list to hold results
    for x in range(0,len(All_Company_Quarters)):#for all the companies
        stripped_dates = [sub.replace('\t', '') for sub in All_Company_Quarters[x]]#replace the \t' that appears after period of report with blank
        dates=[datetime.datetime.strptime(x, "%Y%m%d").date() for x in stripped_dates]#covert to date
        Period_of_report_dict[companies[x]]=[x.strftime("%Y-%m-%d") for x in dates]#add to dictionary of periods reported for each company
        Periods=[Closest_Quarter(x) for x in dates]#get closest quarter to those period of report dates
        Clean_Quarters=Clean_Quarters+[[str(i.year)+"Q"+str(i.quarter) for i in  pd.to_datetime(Periods)]]#take the month and quarter from the period of report dates and combine like 2020Q1
        Quarter_dict[companies[x]]=[str(i.year)+"Q"+str(i.quarter) for i in  pd.to_datetime(Periods)]#Add it to a dictionary (Quarter_dict['microsoft corp'] would return all quarters we have filings for for microsoft corp)

    Unique_Quarters=pd.unique(list(chain.from_iterable(Clean_Quarters))) #unlist the nested lists and take the unique quarter filing dates that appear
    Unique_Quarters.sort()#sort so it appears on logical date order (will look like 2020Q1,2020Q2,2020Q3...)
    #-------------------------------------------------------------------------------------------------------------------------
    #setting up lists of results as dicitonarys for compiler()
    All_Company_Cash_dict=dict() #Adding the cash values pulled as a dictionary (like  All_Company_Cash_dict['microsoft corp'] would return all the cash and cash equivalent values pulled for each of the filing dates for Microsoft)
    for x in range(0,len(companies)):
        All_Company_Cash_dict[companies[x]]=All_Company_Cash[x]


    All_Company_CP_dict=dict()#Adding the commercial paper values pulled as a dictionary (like  All_Company_CP_dict['microsoft corp'] would return all the commerial paper values pulled for each of the filing dates for Microsoft)
    for x in range(0,len(companies)):
        All_Company_CP_dict[companies[x]]=All_Company_CP[x]

    All_Company_CD_dict=dict()#Adding the CD values pulled as a dictionary (like  All_Company_CD_dict['microsoft corp'] would return all the CD values pulled for each of the filing dates for Microsoft)
    for x in range(0,len(companies)):
        All_Company_CD_dict[companies[x]]=All_Company_CD[x]
    return(Unique_Quarters,Quarter_dict,All_Company_Cash_dict,All_Company_CP_dict,All_Company_CD_dict,Period_of_report_dict)
#-------------------------------------------------------------------------------------------------------------------------
#Formatting the results into a dataframe to push to excel
def Compiler(Unique_Quarters,Quarter_dict,All_Company_Cash_dict,All_Company_CP_dict,All_Company_CD_dict,Period_of_report_dict):
    cash_fin=dict()#initaliaze empty dictionary
    cp_fin=dict()#initaliaze empty dictionary
    cd_fin=dict()#initaliaze empty dictionary
    per_of_report_fin=dict()
    for quarter in Unique_Quarters:#for each of the unique quarters files were pulled for
        cash_values=[]#collect all the values as a list that contains the answer for each company
        cp_values=[]
        cd_values=[]
        per_of_report_values=[]
        for company in companies:#for each company
            cash=""#if it does not meet the condition below (i.e there is no data for that quarter for that company, set value equal to blank)
            cp=""
            cd=""
            per_of_report=""
            if quarter in Quarter_dict[company]:#If that company does have information pulled for that quarter
                Index_of_value_to_pull=Quarter_dict[company].index(quarter)#Get the index for that quarter in the list of quarters that we are examining (i.e in [2020Q1,202Q2,202Q3] 202Q3 appears in the 2 index position because python index starts at 0)
                cash=All_Company_Cash_dict[company][Index_of_value_to_pull]#for that compnay, take the cash value at that same index (i.e for the same quarter)
                per_of_report=Period_of_report_dict[company][Index_of_value_to_pull]
                try:
                    cp=All_Company_CP_dict[company][Index_of_value_to_pull]#for that compnay, take the cp value at that same index (i.e for the same quarter)
                except:
                    cp="" #if it fails leave it blank
                try:
                    cd=All_Company_CD_dict[company][Index_of_value_to_pull]#for that compnay, take the cash value at that same index (i.e for the same quarter)
                except:
                    cd=""#if it fails leave it blank
            cash_values= cash_values +[cash]#add result to a list of lists of answers
            cp_values= cp_values +[cp]#add result to a list of lists of answers
            cd_values= cd_values +[cd]#add result to a list of lists of answers
            per_of_report_values=per_of_report_values+[per_of_report]
        cash_fin[quarter]=cash_values#Once you have looped through all companies for that quarter, add it to cash_fin dictionary like cash_fin["2020Q2"] would return a list of all the cash values pulled on that date
        cp_fin[quarter]=cp_values#Once you have looped through all companies for that quarter, add it to cp_fin dictionary like cp_fin["2020Q2"] would return a list of all the cp values pulled on that date
        cd_fin[quarter]=cd_values     #Once you have looped through all companies for that quarter, add it to cd_fin dictionary like cd_fin["2020Q2"] would return a list of all the cd values pulled on that date
        per_of_report_fin[quarter]=per_of_report_values
    #Convert dictionaries to dataframes
    cash_df=pd.DataFrame.from_dict(cash_fin)
    cp_df=pd.DataFrame.from_dict(cp_fin)
    cd_df=pd.DataFrame.from_dict(cd_fin)
    per_of_report_df=pd.DataFrame.from_dict(per_of_report_fin)
    return(cash_df,cp_df,cd_df,per_of_report_df)
#-------------------------------------------------------------------------------------------------------------------------  
#Get most recent data available for each company for a final sheet of the excel workbook
def MostRecentValues(cash_df,cp_df,cd_df,per_of_report_df,Unique_Quarters):
    cash_df=cash_df.replace("",np.nan)#replacing blanks with nans
    cp_df=cp_df.replace("",np.nan)
    cd_df=cd_df.replace("",np.nan)
    per_of_report_df=per_of_report_df.replace("",np.nan)
    cash_values_most_recent=[]#initaliaze empty list
    cp_values_most_recent=[]#initaliaze empty list
    cd_values_most_recent=[]#initaliaze empty list
    per_of_report_values_most_recent=[]#initaliaze empty list
    for row in range(0,len(cash_df)):#for the number of rows availble in the cash dataframe, go by row index
       cash_value = cash_df.loc[row][~cash_df.loc[row].isna()][-1]   #get last non blank value for each row (company)                                                                                                                                       
       cash_values_most_recent=cash_values_most_recent+[cash_value]  #add it to a list storing these values
       try:
           cp_value = cp_df.loc[row][~cp_df.loc[row].isna()][-1]   #get last non blank value for each row (company) 
       except:
           cp_value = ""               #if there is no data, leave it blank                                                                                                           
       cp_values_most_recent=cp_values_most_recent+[cp_value] #add it to a list storing these values
       try:
           cd_value = cd_df.loc[row][~cd_df.loc[row].isna()][-1]   #get last non blank value for each row (company 
       except:                 
           cd_value = ""      #if there is no data, leave it blank                                                                                                              
       cd_values_most_recent=cd_values_most_recent+[cd_value] #add it to a list storing these values
       per_of_report_value = per_of_report_df.loc[row][~per_of_report_df.loc[row].isna()][-1]       #get last non blank value for each row (company                                                                                                                                   
       per_of_report_values_most_recent=per_of_report_values_most_recent+[per_of_report_value]#add it to a list storing these values
       
    cash_values_most_recent_df=pd.DataFrame(cash_values_most_recent)  #convert results to a single column dataframe
    cp_values_most_recent_df=pd.DataFrame(cp_values_most_recent)  #convert results to a single column dataframe
    cd_values_most_recent_df=pd.DataFrame(cd_values_most_recent)  #convert results to a single column dataframe
    per_of_report_values_most_recent_df=pd.DataFrame(per_of_report_values_most_recent)  #convert results to a single column dataframe
    
    cash_df['most_recent_values']=cash_values_most_recent_df#add this new column to the cash_df
    cp_df['most_recent_values']=cp_values_most_recent_df#add this new column to the cp_df
    cd_df['most_recent_values']=cd_values_most_recent_df#add this new column to the cd_df
    per_of_report_df['most_recent_values']=per_of_report_values_most_recent_df#add this new column to the period_of_report_df
    Unique_Quarters=np.append(Unique_Quarters,'most_recent_values')#add a final quarter called "most recent value" so it will create a new tab for this new column in TableCreation()
    return(cash_df,cp_df,cd_df,per_of_report_df,Unique_Quarters)
#-------------------------------------------------------------------------------------------------------------------------  
#Output dataframes from Compiler() and MostRecentValues() to excel
def TableCreation():
    writer = pd.ExcelWriter('/stfm/dev2/m1kal01/Instruments/cp/CorporateCPHolders/corporate_holdings_mess.xlsx', engine='xlsxwriter')
    for x in range(0,len(Unique_Quarters)):
       cash_df.iloc[:,x].to_excel(writer, sheet_name=Unique_Quarters[x], startrow=1,startcol=1,index=False,header=False)
       cp_df.iloc[:,x].to_excel(writer, sheet_name=Unique_Quarters[x], startrow=1,startcol=2,index=False,header=False)
       cd_df.iloc[:,x].to_excel(writer, sheet_name=Unique_Quarters[x], startrow=1,startcol=3,index=False,header=False)
       per_of_report_df.iloc[:,x].to_excel(writer, sheet_name=Unique_Quarters[x], startrow=1,startcol=4,index=False,header=False)
       workbook  = writer.book
       worksheet = writer.sheets[Unique_Quarters[x]]
       worksheet.set_column('A:A', 21)
       worksheet.set_column('B:B', 33)
       worksheet.set_column('C:C', 27)
       worksheet.set_column('D:D', 30)
       worksheet.set_column('E:E', 20)
       border_format=workbook.add_format({
                                    'border':1,
                                    'align':'left',
                                    'font_size':10
                                   })
       border_format_thick=workbook.add_format({
                                    'border':5,
                                    'align':'left',
                                    'font_size':10
                                   })
       worksheet.write('A1', 'Company Name')
       worksheet.write('B1', 'Cash and cash equivalent (in millions)')
       worksheet.write('C1', 'Commercial paper (in millions)')
       worksheet.write('D1', 'Certificate of deposits (in millions)')
       worksheet.write('E1', 'Period of Report')
       for x in range(0,len(companies)):
           cell="A"+str(x+2)
           worksheet.write(cell, excel_display_names[companies[x]])
       last_row=len(companies)+1
       full_range='A1:E'+str(last_row)
       worksheet.conditional_format( full_range , { 'type' : 'no_blanks' , 'format' : border_format} )
       worksheet.conditional_format( full_range , { 'type' : 'blanks' , 'format' : border_format} )
       worksheet.conditional_format( 'A1:E1' , { 'type' : 'no_blanks' , 'format' : border_format_thick} )
       worksheet.conditional_format( full_range , { 'type' : 'no_blanks' , 'format' : border_format_thick} )
    writer.close()

#Reading the results of numbers pulled from string_search.py
All_Company_Quarters=pd.read_pickle('All_Company_Quarters.pkl')
All_Company_CP=pd.read_pickle('All_Company_CP.pkl')
All_Company_CD=pd.read_pickle('All_Company_CD.pkl')
All_Company_Cash=pd.read_pickle('All_Company_Cash.pkl')

#How you'd like them labeled in the final excel tables (determined in pull_process.py)
excel_display_names=pd.read_pickle('/stfm/dev2/m1kal01/Instruments/cp/CorporateCPHolders/excel_display_names.pkl')

#Now that we pulled the data, lets format is and push it to excel
Unique_Quarters,Quarter_dict,All_Company_Cash_dict,All_Company_CP_dict,All_Company_CD_dict,Period_of_report_dict = SetUp_Compiler(All_Company_Quarters,All_Company_Cash,All_Company_CP,All_Company_CD)
cash_df,cp_df,cd_df,per_of_report_df=Compiler(Unique_Quarters,Quarter_dict,All_Company_Cash_dict,All_Company_CP_dict,All_Company_CD_dict,Period_of_report_dict)
cash_df,cp_df,cd_df,per_of_report_df,Unique_Quarters= MostRecentValues(cash_df,cp_df,cd_df,per_of_report_df,Unique_Quarters)
TableCreation()
