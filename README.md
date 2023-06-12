# YoutubeDataHarvesting
Data harvesting, also known as data scraping or data collection, refers to the process of extracting and gathering data from various sources, such as websites, databases, APIs, or any other digital platforms.It involves automated techniques to retrieve and collect structured or unstructured data from these sources.

In this project we have used Google API to retreive data from youtube when we enter the channel id.

we have created two files for this project one is the **main.py** and another one is the **stream.py** 

Environment am Using

**Pycharm, Anconda Navigator, MongoDB Compass, MySQL Workbench**

------------------------------------------------------------------------------------------------------------------------------------------------------------------

# main.py
```
import pymongo
import datetime
import mysql.connector
import regex as re
```

In this **main.py** file we create different functions to extract data from youtube using Google's API.
Function's Named

```
def channel_details(youtube, channel_id)
def Playlist_Video(youtube, playlist_id)
def Video_Details(youtube, video_id)
def get_video_comments(youtube, video_id, max_comments)
def checkExistence_DB(DB_NAME, client)
def upload_to_DB(channel_name,new)
def DB_Create()
--------------------------Function's to insert data into MYSQL-------------------------------
def SQL_Channel(channel)
def playlist(channel)
def Video(item,channel_playlist_id)
def Comments(co)
----------------------------------Function to Convert Extracted Time-------------------------
def convert_duration(duration)
```

In this file we create three different types of fucntions for the opertaion Data Extraction From Youtube, Storing extracted data in MONGODB, 
Inserting selected data into MYSQL.

------------------------------------------------------------------------------------------------------------------------------------------------------------------

# streamit.py

```
from streamlit_option_menu import option_menu
import plotly.express as px
import streamlit as st
import main
import mysql.connector
import pymongo
import pandas as pd
from googleapiclient.discovery import build
from PIL import Image
```

This is the place where we will create the UI for our project,

Starting with the first line in the streamlit ```st.set_page_config(page_title='TEXT_EXTRACTION_USING_OCR', page_icon=":tada", layout='wide')``` page config

Here we define the youtube API key to extract the data whihch we needed 

api_service_name = 'youtube'
api_version = 'v3'
youtube = build(api_service_name,api_version,developerKey='######Aq60ZlR######MBzG#X8P9A######s9D888')

Heere we call the function which we have definied in the **main.py** and store the data in **MONGODB**

Now we have to give option for the user to select the data which he wants to store in MYSQL 

Once it is selected it should be moved and we have to display the data according to the queries given in the document.

Below is the screenshot of the UI

![Screenshot (55)](https://github.com/SrinivasanGajendran/DataScrapping/assets/46883734/8ab9804b-3ca8-4dee-b0b2-1936ca05726a)


![Screenshot (56)](https://github.com/SrinivasanGajendran/DataScrapping/assets/46883734/29ae532e-b2f8-4f09-ac30-2cf4a200016d)


![Screenshot (57)](https://github.com/SrinivasanGajendran/DataScrapping/assets/46883734/932205f5-742c-4164-ad02-2d52513017e5)


