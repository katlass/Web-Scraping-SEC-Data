#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 15:17:19 2021

@author: m1kal01
"""
# ==============================================================================================#
#This script pulls the specific commercial paper/negotiable certificates of deposit/cash and cash equivalent data from the SEC's edgar site for the top 15 corporate holders
# ==============================================================================================#
#Set-up
import pandas as pd
import re
import pickle 
pd.options.display.max_columns=500
pd.options.display.max_rows=20

#Reading in data from pull_process.py
companies=pd.read_pickle('companies.pkl') #this comes from pull_process.py (it is all the compnaies you want to pull)
txtFiles=pd.read_pickle('txtFiles.pkl') #this comes from pull_process.py (it is all the text files from the SEC for those companies)

#Splitting txt files up by company, assigning to a dictionary (company_dict) for easy accessing
company_dict=dict([(i, []) for i in companies])
for company in companies:
    files=[item for item in txtFiles if item.lower().find(company) != -1]
    company_dict[company]=files

#--------------------------------------------------------------------------------------------------------------#
#This pulls the digits we want from the txt files returned by pullFile() in  pull_process.py 
def ResultFinder(files,start_word_trigger,end_word_trigger,start_number_trigger,end_number_trigger,custom_stopper=1,find_final_occurance=False,seperator=' ',which_occurance=1,specific_index=False):
    result=[] #Intialize empty list to store answers
    for x in files:#loop through each file for that company
        anaFile = open(x, "r")
        interestingText = anaFile.read() #read in the data as new string interestingText
        anaFile.close()
        interestingText=interestingText.lower()
        interestingText= interestingText.replace(u'\xa0', u' ')
        interestingText= interestingText.replace(u'\n', u'') #put it to lower case and remove weird line breaks/special characters
        start=interestingText.find(start_word_trigger)#start_word_trigger should be the broader passage you want to search for the key phrase (like commerical paper)
        end=interestingText.find(end_word_trigger,start) #end_word_trigger should be the end of the broader passage you want to search for the key phrase in
        if find_final_occurance == False: #This is for the case where the value we want to pull is in the first column if there is say 2+ columns of digits (default)
            compaper=interestingText.find(start_number_trigger,start,end)#This is the key word within that broader passage you want to specifically look for
            startnum=compaper+len(start_number_trigger)#Then it will start looking for the number to pull right after the end of that key word phrase
        else:
            compaper=interestingText.rfind(start_number_trigger,start,end)#This is case where the digits we want to pull are in the last column (if there are 2+ columns of digits)
            startnum=compaper
        endnum=interestingText.find(end_number_trigger,startnum)-custom_stopper#This is where the digits we want to pull end. custom_stopper helps when the last number gets cut off
        if specific_index == True:#This is case where the digits we want to pull are in the nth column (i.e column 5) if there are 2+ columns.
            compaper=interestingText.find(start_number_trigger,start,end)#This is the key word within that broader passage you want to specifically look for
            whole_range=interestingText[compaper:compaper+200]#Takes the next 200 charcaters after that key word
            occurances=[m.start() for m in re.finditer(seperator, whole_range)]#finds occurances of some seperator between columns of digits (like a space, double space, etc) specefied by you in seperator parameter
            index_start=occurances[which_occurance-1]#This will grab the nth occurance of that seperator (i.e the nth column)
            result=result+[whole_range[index_start:occurances[which_occurance]]]#Then will grab from that digit up to the next seperator
        else:
            result=result+[interestingText[startnum:endnum]]#add answer to list of results
    return(result)

#-------------------------------------------------------------------------------------------------------------------------
#NOW FOR THE ACTUAL FINAL PULL OF DIGITS
#This pulls the actual data, modify/add queries (_pt2,_pt3,etc...) if the filing format for a specific company changes over time (check out debugging.py for help)
#-------------------------------------------------------------------------------------------------------------------------
intel_cp=[]
intel_cd=[]
intel_cash_pt1=ResultFinder(company_dict['intel corp'][0:1],start_word_trigger='assets    current assets:',
                end_word_trigger='total current assets',
                start_number_trigger='cash and cash equivalents $',end_number_trigger='$',custom_stopper=0)
#Form was changed on 2020-07-24, thus cash_pt2
intel_cash_pt2=ResultFinder(company_dict['intel corp'][1:],start_word_trigger='assetscurrent assets:',
                end_word_trigger='total current assets',
                start_number_trigger='cash and cash equivalents$',end_number_trigger='$',custom_stopper=0)
#Combine query results
intel_cash=intel_cash_pt1+intel_cash_pt2
intel_quarters=ResultFinder(company_dict['intel corp'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
cvs_cp=[]
cvs_cd=[]
cvs_cash=ResultFinder(company_dict[ 'cvs health corp'],start_word_trigger='cvs health corporation condensed consolidated balance sheets',
                end_word_trigger='total current assets',
                start_number_trigger='cash and cash equivalents$',end_number_trigger='$',custom_stopper=0)
cvs_quarters=ResultFinder(company_dict['cvs health corp'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
cigna_cp=[]
cigna_cd=[]
cigna_cash=ResultFinder(company_dict['cigna corp'],start_word_trigger='cigna corporationconsolidated balance sheets',
                end_word_trigger='total current assets',
                start_number_trigger='cash and cash equivalents$',end_number_trigger='$',custom_stopper=0)
cigna_quarters=ResultFinder(company_dict['cigna corp'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
cola_cp=[]
cola_cd=[]
cola_cash=ResultFinder(company_dict['coca cola co'],start_word_trigger='current assets',
                end_word_trigger='short-term investments',
                start_number_trigger='cash and cash equivalents$',end_number_trigger='$',custom_stopper=0)
cola_quarters=ResultFinder(company_dict['coca cola co'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
exxon_cp=[]
exxon_cd=[]
exxon_cash_pt1=ResultFinder(company_dict['exxon mobil corp'][0:2],start_word_trigger='current assets',
                end_word_trigger='total assets',
                start_number_trigger='cash and cash equivalents  ',end_number_trigger=' ',custom_stopper=0)
#Form change on 2020-11-04
exxon_cash_pt2=ResultFinder(company_dict['exxon mobil corp'][2:],start_word_trigger='current assets',
                end_word_trigger='total assets',
                start_number_trigger='cash and cash equivalents',end_number_trigger=' ',custom_stopper=0)
exxon_cash=exxon_cash_pt1+exxon_cash_pt2
exxon_quarters=ResultFinder(company_dict['exxon mobil corp'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
anthem_cp=[]
anthem_cd=[]
anthem_cash=ResultFinder(company_dict['anthem, inc.'],start_word_trigger='current assets:',
                end_word_trigger='fixed maturity securities',
                start_number_trigger='cash and cash equivalents$',end_number_trigger=' ',custom_stopper=0)
anthem_quarters=ResultFinder(company_dict['anthem, inc.'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
ford_credit_cp=[]
ford_credit_cd=[]
ford_credit_cash=ResultFinder(company_dict['ford motor credit co llc'],start_word_trigger='ford motor credit company llc and subsidiariesconsolidated balance sheet',
                end_word_trigger='marketable securities',
                start_number_trigger='$',end_number_trigger='marketable securities',find_final_occurance=True,custom_stopper=0)
ford_credit_quarters=ResultFinder(company_dict['ford motor credit co llc'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
ford_cp=[]
ford_cd=[]
ford_cash=ResultFinder(company_dict['ford motor co'],start_word_trigger='ford motor company and subsidiariesconsolidated balance sheet',
                end_word_trigger='marketable securities',
                start_number_trigger='$',end_number_trigger='marketable securities',find_final_occurance=True,custom_stopper=0)
ford_quarters=ResultFinder(company_dict['ford motor co'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
oracle_cp_pt1=ResultFinder(company_dict['oracle corp'][0:2],start_word_trigger='assets and liabilities measured at fair value on a recurring basis',
                 end_word_trigger='money market funds',
                 start_number_trigger='commercial paper debt securities',end_number_trigger=' ',custom_stopper=0,seperator='  ',which_occurance=3,specific_index=True)
#The form changed for this company in March 2021, so there are two seperate queries
oracle_cp_pt2=ResultFinder(company_dict['oracle corp'][2:],start_word_trigger='assets and liabilities measured at fair value on a recurring basis',
                 end_word_trigger='derivative financial instruments',
                 start_number_trigger='commercial paper debt securities',end_number_trigger=' ',custom_stopper=0,seperator='  ',which_occurance=3,specific_index=True)
#Combine query results
oracle_cp=oracle_cp_pt1+oracle_cp_pt2
oracle_cd=[]
oracle_cash=ResultFinder(company_dict['oracle corp'],start_word_trigger='current assets:',
                end_word_trigger='marketable securities',
                start_number_trigger='cash and cash equivalents $',end_number_trigger=' ',custom_stopper=0)
oracle_quarters=ResultFinder(company_dict['oracle corp'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
chevron_cp=[]
chevron_cd=[]
chevron_cash=ResultFinder(company_dict['chevron corp'],start_word_trigger='chevron corporation and subsidiariesconsolidated balance sheet',
                end_word_trigger='marketable securities',
                start_number_trigger='$',end_number_trigger=' ',custom_stopper=0)
chevron_quarters=ResultFinder(company_dict['chevron corp'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
united_cp=[]
united_cd=[]
united_cash=ResultFinder(company_dict['unitedhealth group inc'],start_word_trigger='current assets:',
                end_word_trigger='short-term investments',
                start_number_trigger='$',end_number_trigger=' ',custom_stopper=0)
united_quarters=ResultFinder(company_dict['unitedhealth group inc'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
facebook_cp=ResultFinder(company_dict['facebook inc'],start_word_trigger='cash and cash equivalents, and marketable securities',
                 end_word_trigger='total cash and cash equivalents',
                 start_number_trigger='corporate debt securities',end_number_trigger=' ',custom_stopper=0)

facebook_cd=ResultFinder(company_dict['facebook inc'],start_word_trigger='cash and cash equivalents, and marketable securities',
                 end_word_trigger='total cash and cash equivalents',
                 start_number_trigger='certificate of deposits and time deposits',end_number_trigger=' ',custom_stopper=0)

facebook_cash=ResultFinder(company_dict['facebook inc'],start_word_trigger='current assets:',
                end_word_trigger='marketable securities',
                start_number_trigger='$',end_number_trigger=' ',custom_stopper=0)
facebook_quarters=ResultFinder(company_dict['facebook inc'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
amazon_cp=[]
amazon_cd=[]
amazon_cash=ResultFinder(company_dict['amazon com inc'],start_word_trigger='current assets:',
                end_word_trigger='marketable securities',
                start_number_trigger='$',end_number_trigger='marketable securities',find_final_occurance=True,custom_stopper=0)
amazon_quarters=ResultFinder(company_dict['amazon com inc'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
alphabet_cp=[]
alphabet_cd=[]
alphabet_cash=ResultFinder(company_dict['alphabet inc.'],start_word_trigger='current assets:',
                end_word_trigger='marketable securities',
                start_number_trigger='$',end_number_trigger=' marketable securities',find_final_occurance=True,custom_stopper=0)
alphabet_quarters=ResultFinder(company_dict['alphabet inc.'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
apple_cp=ResultFinder(company_dict['apple inc.'],start_word_trigger='cash, cash equivalents and marketable securities',
                 end_word_trigger='mortgage- and asset-backed securities',
                 start_number_trigger='commercial paper',end_number_trigger='?')

apple_cd=ResultFinder(company_dict['apple inc.'],start_word_trigger='cash, cash equivalents and marketable securities',
                 end_word_trigger='mortgage- and asset-backed securities',
                 start_number_trigger='certificates of deposit and time deposits',end_number_trigger='?')

apple_cash=ResultFinder(company_dict['apple inc.'],start_word_trigger='current assets:',
                 end_word_trigger='marketable securities',
                 start_number_trigger='cash and cash equivalents',end_number_trigger=' $',custom_stopper=0)
apple_quarters=ResultFinder(company_dict['apple inc.'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)

#-------------------------------------------------------------------------------------------------------------------------
mcsft_cp=ResultFinder(company_dict['microsoft corp'],start_word_trigger='changes in fair value recorded in other comprehensive income',
                 end_word_trigger='total debt investments',
                 start_number_trigger='commercial paper level 2  $',end_number_trigger=' $')

mcsft_cd=ResultFinder(company_dict['microsoft corp'],start_word_trigger='changes in fair value recorded in other comprehensive income',
                 end_word_trigger='total debt investments',
                 start_number_trigger='certificates of deposit level 2   ',end_number_trigger='   ',custom_stopper=0)

mcsft_cash=ResultFinder(company_dict['microsoft corp'],start_word_trigger='current assets:',
                 end_word_trigger='short-term investments',
                 start_number_trigger='cash and cash equivalents ',end_number_trigger='  $')

mcsft_quarters=ResultFinder(company_dict['microsoft corp'],start_word_trigger="period of report",
                 end_word_trigger='filed as of date',
                 start_number_trigger='period of report:',end_number_trigger='filed as of date',custom_stopper=0)
#-------------------------------------------------------------------------------------------------------------------------
#SETUP for Tables (final_tables.py)
#Finding the quarters reported in each file pulled
All_Company_Quarters=[apple_quarters,alphabet_quarters,mcsft_quarters,amazon_quarters,facebook_quarters,
    united_quarters,chevron_quarters,oracle_quarters,ford_quarters,ford_credit_quarters,
    anthem_quarters,exxon_quarters,cola_quarters,cigna_quarters,cvs_quarters,intel_quarters]

with open('All_Company_Quarters.pkl', 'wb') as f:
        pickle.dump(All_Company_Quarters, f)
    
#combining all the values pulled for each company into a list of lists
All_Company_Cash=[apple_cash,alphabet_cash,mcsft_cash,amazon_cash,facebook_cash,
    united_cash,chevron_cash,oracle_cash,ford_cash,ford_credit_cash,
    anthem_cash,exxon_cash,cola_cash,cigna_cash,cvs_cash,intel_cash]

with open('All_Company_Cash.pkl', 'wb') as f:
        pickle.dump(All_Company_Cash, f)
    
#combining all the values pulled for each company into a list of lists
All_Company_CP=[apple_cp,alphabet_cp,mcsft_cp,amazon_cp,facebook_cp,
    united_cp,chevron_cp,oracle_cp,ford_cp,ford_credit_cp,
    anthem_cp,exxon_cp,cola_cp,cigna_cp,cvs_cp,intel_cp]

with open('All_Company_CP.pkl', 'wb') as f:
        pickle.dump(All_Company_CP, f)
    
#combining all the values pulled for each company into a list of lists
All_Company_CD=[apple_cd,alphabet_cd,mcsft_cd,amazon_cd,facebook_cd,
    united_cd,chevron_cd,oracle_cd,ford_cd,ford_credit_cd,
    anthem_cd,exxon_cd,cola_cd,cigna_cd,cvs_cd,intel_cd]

with open('All_Company_CD.pkl', 'wb') as f:
        pickle.dump(All_Company_CD, f)
