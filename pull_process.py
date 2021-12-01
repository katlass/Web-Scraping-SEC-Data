#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 12:47:50 2021

@author: m1kal01
"""
# ==============================================================================================#
#This file actually pulls the data from the SEC and formats the HTML as a txt file
# ==============================================================================================#
#pullFile() iterates through the URLS of SEC txt filings found in retrieveWriteIndexes() depending on which companies are desired, and calls 
#GetFile() performs a system command, to pull the text information stored in that URL and write text information to a file
#Then processFile() actually reads in that html file and converts to txt
#removefile() just removes the html file now that there is txt file
#returns all text file paths where the data that has been pulled has been written as txtFiles
# ==============================================================================================#
import subprocess
import os
import pandas as pd
from bs4 import BeautifulSoup
from os import path
import pickle 
import requests

#GetFile() performs a system command, to pull the text information stored in that URL and write text information to a file
def GetFile(htmlfile, edgarurl1):
    print('Downloading '+ htmlfile + '\n')
    proxies = {'https':'wwwproxy.xxxxxxxxxxxx.gov'}
    lines = requests.get(edgarurl1, proxies=proxies,headers = {"user-agent": "frX-XXXXXX-XXXX"}).text
    Html_file= open(htmlfile,"w")
    Html_file.write(lines)
    Html_file.close()  
    print('Done Downloading '+ htmlfile + '\n')
    return
         
#Then processFile() actually reads in that html file and converts to txt
def processFile(htmlpath):
    txtpath = htmlpath.strip('.html') + '.txt'
    print("Processing: " + htmlpath)
    htmlfile = open(htmlpath, 'r')
    txtfile = open(txtpath, 'wb')
    #Reading in the entire text of the document
    #  and truncating at the end of the first deliminated document
    cleantext = htmlfile.read()
    cleantext = cleantext[:cleantext.find("</DOCUMENT>")]
    #Extracting the text from the html parts
    soup = BeautifulSoup(cleantext)
    cleantext = soup.get_text()
    #Writing the text out
    txtfile.write(cleantext.encode('UTF-8'))
    print(txtpath + " written.")
    htmlfile.close()
    txtfile.close()
    return txtpath #Returning the path the file was written to
            
#removefile() just removes the html file now that there is txt file
def removefile(to_remove):
    if path.isfile(to_remove):
        subprocess.call(('rm',to_remove))
        print(to_remove + " removed.\n")       

#pullFile() iterates through the URLS of SEC txt filings found in retrieveWriteIndexes() depending on which companies are desired
#and pulls and writes data to txt files.
#It returns a list of all text file paths where the data that has been pulled has been written
def pullFile(companies):
    ## Setting the output dir. Please change if the location is changed   
    wd = os.getcwd()
    masterIndex = pd.read_csv('masterEdgarIndexes.csv', header=None, 
                              names = ['cik','company', 'form', 'date', 'url'])
    masterIndex=masterIndex[masterIndex.company.str.lower().isin(companies)]
    html_files=[]
    txt_paths=[]
    edgarurls=[]
    for index, row in masterIndex.iterrows():
        company = row['company'].split('/')[0].strip()
        date = row['date']
        form = row['form']
        url = row['url'].strip()
        #Generating a path to save to
        html_file = wd + company + '_' + form + '_'+ date + '.html'
        txt_path = wd + company + '_' + form + '_' + date + '.txt'
        edgarurl = 'https://www.sec.gov/Archives/' + url 
        html_files=html_files+[html_file]
        txt_paths=txt_paths+[txt_path]
        edgarurls=edgarurls+[edgarurl]
    for index in range(0,len(masterIndex)):        
        GetFile(html_files[index], edgarurls[index]) 
        print(html_files[index] + " successfully pulled \n") 
        processFile(html_files[index])
        print(html_files[index] + " converted to .txt\n")
        removefile(html_files[index])
    return txt_paths

#Pick companies you'd like to pull data for
companies=['apple inc.','alphabet inc.','microsoft corp','amazon com inc' ,'facebook inc','unitedhealth group inc','chevron corp','oracle corp','ford motor co', 'ford motor credit co llc', 'anthem, inc.', 'exxon mobil corp', 'coca cola co', 'cigna corp', 'cvs health corp',  'intel corp']
txtFiles = pullFile(companies) 
with open('txtFiles.pkl', 'wb') as f:
        pickle.dump(txtFiles, f)
with open('companies.pkl', 'wb') as f:
        pickle.dump(companies, f)
