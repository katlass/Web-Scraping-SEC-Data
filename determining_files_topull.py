#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 14:59:35 2021

@author: m1kal01
"""
#This script grabs the relevent information on what URLS to pull
#genUrls aggregates the names of the master indexes from the SEC to search in for the date range, 
#ex. https://www.sec.gov/Archives/edgar/full-index/2020/QTR1/master.idx
#Then, from this master index retrieveWriteIndexes() generates the individual URL file paths/company info we are looking at pulling 
#CIK, company name, filing type, period of report, URL to text of that filing
#ex. 1000045,NICHOLAS FINANCIAL INC,10-Q,2020-02-14,edgar/data/1000045/0001564590-20-004703.txt


#Imports
import sys
import requests
import pandas as pd
pd.options.display.max_columns=500
pd.options.display.max_rows=20
#--------------------------------------------------------------------------------------------------------------#
#This function acquires urls for all master index files in the time period
def genUrls( startDate, endDate ):
    #Setting the start and end variables
    startYear = startDate[0]
    startQuarter = (startDate[1]-1) // 3 + 1
    endYear = endDate[0]
    endQuarter = (endDate[1]-1) // 3 + 1
    #Making a list of Quarter tags for propper url construction
    quarters = ["QTR1", "QTR2", "QTR3", "QTR4"]
    period = [(y, q) for y in range(startYear+1,endYear)
              for q in quarters]
    #Adding the potential partial years at the beginning and end
    for i in range(0, 5-startQuarter):
        period.insert(i,(startYear, quarters[startQuarter+i-1]))
    for i in range(0, endQuarter):
        period.append((endYear, quarters[i]))
    #Creating the list of urls
    urls = ['https://www.sec.gov/Archives/edgar/full-index/%d/%s/master.idx' 
            % (x[0], x[1]) for x in period]
    urls.sort()
    return urls

#--------------------------------------------------------------------------------------------------------------#
def retrieveWriteIndexes( urls , filings = ['10-Q', '10-K', 'NT 10-Q', 'NT 10-k']):
    #Looping through each url, retrieving the data, and writing to csv
    dataframes = pd.DataFrame({
                "cik":[],
                "company":[],
                "form":[],
                "date":[],
                "url":[]
                })
    proxies = {'https':'wwwproxy.xxxxxxxxxxxx.gov'}
    for url in urls[1:len(urls)]:
        #Retrieving the text of the url
        lines = requests.get(url, proxies=proxies,headers = {"user-agent": "frX-XXXXXX-XXXX"}).text.splitlines()
        #This list holds one tuple per company in a given quarter's master index
        #each tuple contains CIK, company name, filing type, period of report, URL to text of that filing
        #   (The first eleven lines of each file form a header)
        records = [tuple(line.split('|')) for line in lines[11:]]
        #Writing all records to the csv by turning the current index into a data frame and appending it
        #   a larger dataframe
        dataframe = pd.DataFrame(records,columns = ['cik', 'company', 'form', 'date', 'url'])
        dataframe = dataframe[dataframe.form.isin(filings)]
        dataframes = dataframes.append(dataframe)   
    dataframes.to_csv("masterEdgarIndexes.csv", header=False, index=False)
    return


start=[int(sys.argv[1][0:4]),int(sys.argv[1][4:6]),int(sys.argv[1][6:8])]
end=[int(sys.argv[2][0:4]),int(sys.argv[2][4:6]),int(sys.argv[2][6:8])]


print("Getting URLs...")
urls = genUrls(start,end) #returns the URLS for the master indexes like https://www.sec.gov/Archives/edgar/full-index/2020/QTR1/master.idx
urls =list(pd.unique(urls))
print("Successfully generated list of URLs.")
print("Writing URLs/company info into master index file...")
retrieveWriteIndexes(urls, ['10-Q', 'NT 10-Q']) #generates the individual URL file paths we are looking at pulling
#Form type options: ['10-Q', '10-K', 'NT 10-Q', 'NT 10-k'], we are intrested in 10-Qs 
print("MasterEdgarIndexes.csv was successfully updated.") 
