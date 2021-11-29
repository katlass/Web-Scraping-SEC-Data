#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 09:25:35 2021

@author: m1kal01
"""

#Imports
import sys
import subprocess


def main():
    subprocess.call([sys.executable,'determining_files_topull.py', "20200101", "20211014"])#change dates to the correct range in form YYYYMMDD
    subprocess.call([sys.executable,'pull_process.py'])
    subprocess.call([sys.executable,'string_search.py'])
    subprocess.call([sys.executable,'final_tables.py'])
