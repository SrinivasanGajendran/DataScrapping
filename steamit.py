from streamlit_option_menu import option_menu
import plotly.express as px
import streamlit as st
import main
import mysql.connector
import pymongo
import pandas as pd
from googleapiclient.discovery import build


st.set_page_config(page_title='YTDH', page_icon=":tada", layout='wide')

api_service_name = 'youtube'
api_version = 'v3'
youtube = build(api_service_name,api_version,developerKey='AIzaSyAq60ZlRPrCkyMBzGAX8P9A8DkFjs9DkwU')

st.title('YoutubeDataHarvesting')

SELECT = option_menu(
    menu_title=None,
    options=['Home', 'Process','Database'],
    icons=['house', 'bar-chart'],
    default_index=2,
    orientation='horizontal',
    styles={
        'container': {'padding': '0!important', 'background-color': 'white', 'size': 'cover'},
        'icon': {'color': 'white', 'font-size': '20px'},
        'nav-link': {'font-size': '20px', 'text-align': 'center', 'margin': '-2px', '--hover-color': '#808080'},
        'nav-link-selected': {'background-color': '#808080'}
    }
)

if SELECT == 'Home':
    st.subheader(
        'Data harvesting, also known as data scraping or data collection, refers to the process of extracting and gathering data from various sources, such as websites, databases, APIs, or any other digital platforms.'
        'It involves automated techniques to retrieve and collect structured or unstructured data from these sources.')
    st.subheader('Data harvesting typically involves writing code or using specialized tools to access and extract specific data points or a large amount of data from targeted sources.'
                 'The harvested data can include various types of information, such as text, images, videos, numerical values, or any other data format that is accessible and relevant to the specific objective.')


elif SELECT == 'Process':
    user_input = st.number_input('''How many Channel_id's You Are Going To Enter''',min_value=1, value=1, step=1)
    comments_input = st.number_input('''How Many Comments Required For Each Video ''',min_value=1, value=1, step=1)
    max_comments = int(comments_input)

    ch = []
    count = 0

    integer = int(user_input)
    for i in range(integer):
            box_label = f"Channel_Id {i + 1}"
            user_input = st.text_input(box_label)
            ch.append(user_input)

    if st.button('Fetch And Store'):
            for i in ch:
                data = []
                video_id = []
                new = {}
                response1 = main.channel_details(youtube, i)
                channel_name = response1['items'][0]['snippet']['title']
                channel_video_count = response1['items'][0]['statistics']['videoCount']
                channel_sub = response1['items'][0]['statistics']['subscriberCount']
                channel_view_count = response1['items'][0]['statistics']['viewCount']
                channel_descr = response1['items'][0]['snippet']['description']
                channel_playlist_id = response1['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                channel = {'channel_id':i,
                           'channel_name':channel_name,
                           'channel_video_count':channel_video_count,
                           'subscriber':channel_sub,
                           'channel_view_count':channel_view_count,
                           'channel_descr':channel_descr,
                           'playlist_id':channel_playlist_id,}
                playlist_items = main.Playlist_Video(youtube, channel_playlist_id)

                for item in playlist_items:
                    video_id.append(item['contentDetails']['videoId'])
                for v in video_id:
                    ind = 1
                    comments = {}
                    for item in main.get_video_comments(youtube, v, max_comments):
                        comment_id = item["id"]
                        vid_id = v
                        comment_snippet = item['snippet']['topLevelComment']['snippet']
                        author_name = comment_snippet['authorDisplayName']
                        published_time = comment_snippet['publishedAt']
                        comment_text = comment_snippet['textDisplay']
                        comment_details = {
                            'id': comment_id,
                            'video_Id':vid_id,
                            'author_name': author_name,
                            'published_time': published_time,
                            'comment_text': comment_text
                        }
                        key = f'Comment_Id_{ind}'
                        comments[key] = comment_details
                        ind += 1
                    video = main.Video_Details(youtube, v)
                    video_title = video['snippet']['title']
                    video_like_count = video['statistics']['likeCount']
                    video_dislike_count = video['statistics'].get('dislikeCount', 0)
                    video_comment_count = video['statistics']['commentCount']
                    video_tags = video['snippet'].get('tags', [])[:2]
                    video_descr = video['snippet']['description']
                    video_published = video['snippet']['publishedAt']
                    video_vc = video['statistics']['viewCount']
                    video_duration = video['contentDetails']['duration']
                    videos = {
                        "Video_Id": v,
                        "Video_Name": video_title,
                        "Video_Description": video_descr,
                        "Tags": ', '.join(video_tags),
                        "PublishedAt": video_published,
                        "View_Count": video_vc,
                        "Like_Count": video_like_count,
                        "Dislike_Count": video_dislike_count,
                        "Comment_Count": video_comment_count,
                        "Video_Duration": main.convert_duration(video_duration),
                        "comments": comments
                    }
                    data.append(videos)

                new = {'channel': channel, 'video': data}
                main.upload_to_DB(channel_name,new)
                st.write('Data Fetched & Stored In MongoDB')

elif SELECT == 'Database':
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["mydatabase"]
    collection_names = db.list_collection_names()
    st.header("MongoDB Collections:")
    selected_collections = st.selectbox("Select MongoDB Collections to migrate to mysql", collection_names)
    mongo_db = myclient['mydatabase']
    mongo_collection = mongo_db[selected_collections]
    mongo_data = mongo_collection.find()
    if st.button('migrate'):
        main.DB_Create()
        for document in mongo_data:
            main.SQL_Channel(document['channel'])
            p_id = document['channel']['playlist_id']
            main.playlist(document['channel'])
            for i in document['video']:
                main.Video(i,p_id)
                co = i['comments']
                main.Comments(co)
        st.write('Selected Data Has Been Migrated To MYSQL.')

    question_tosql = st.selectbox('**Select your Question**',
                                  ('',
                                   '1. What are the names of all the videos and their corresponding channels?',
                                   '2. Which channels have the most number of videos, and how many videos do they have?',
                                   '3. What are the top 10 most viewed videos and their respective channels?',
                                   '4. How many comments were made on each video, and what are their corresponding video names?',
                                   '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                                   '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                                   '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                                   '8. What are the names of all the channels that have published videos in the year 2022?',
                                   '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                                   '10. Which videos have the highest number of comments, and what are their corresponding channel names?'),
                                  key='collection_question')
    conn = mysql.connector.connect(
        host="localhost",
        user="srini",
        password="password",
        database="YDH"
    )
    cursor = conn.cursor()
    if question_tosql == '1. What are the names of all the videos and their corresponding channels?':
        cursor.execute(
            "SELECT YoutubeChannel.Channel_Name, Videos.Video_Name FROM YoutubeChannel JOIN playlist JOIN Videos ON YoutubeChannel.Channel_Id = playlist.Channel_Id AND playlist.channel_playlist_id = Videos.Playlist_Id;")
        result_1 = cursor.fetchall()
        df1 = pd.DataFrame(result_1, columns=['Channel Name', 'Video Name']).reset_index(drop=True)
        df1.index += 1
        st.dataframe(df1)

    elif question_tosql == '2. Which channels have the most number of videos, and how many videos do they have?':
        cursor.execute("SELECT Channel_Name, channel_video_count FROM YoutubeChannel ORDER BY channel_video_count DESC;")
        result_2 = cursor.fetchall()
        df2 = pd.DataFrame(result_2, columns=['Channel Name', 'Video Count']).reset_index(drop=True)
        st.dataframe(df2)
        st.bar_chart(df2,x='Channel Name', y='Video Count', width=20)

    elif question_tosql == '3. What are the top 10 most viewed videos and their respective channels?':
        cursor.execute("SELECT YoutubeChannel.Channel_Name, Videos.Video_Name, Videos.View_Count FROM YoutubeChannel JOIN Playlist ON YoutubeChannel.Channel_Id = Playlist.channel_id JOIN Videos ON Playlist.channel_playlist_id = Videos.Playlist_Id ORDER BY Videos.View_Count DESC LIMIT 10")
        result_3 = cursor.fetchall()
        df3 = pd.DataFrame(result_3, columns=['Channel Name', 'Video Name', 'View count']).reset_index(drop=True)
        df3.index += 1
        st.dataframe(df3)

    elif question_tosql == '4. How many comments were made on each video, and what are their corresponding video names?':
        cursor.execute("SELECT Videos.Video_Name, Videos.Comment_Count FROM Videos")
        result_4 = cursor.fetchall()
        df4 = pd.DataFrame(result_4,columns=['Video Name', 'Comment count']).reset_index(drop=True)
        df4.index += 1
        st.dataframe(df4)

    elif question_tosql == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        cursor.execute("SELECT YoutubeChannel.Channel_Name, Videos.Video_Name, Videos.Like_Count FROM YoutubeChannel JOIN playlist ON YoutubeChannel.Channel_Id = playlist.channel_id JOIN Videos ON playlist.channel_playlist_id = Videos.Playlist_Id ORDER BY Videos.Like_Count DESC;")
        result_5= cursor.fetchall()
        df5 = pd.DataFrame(result_5,columns=['Channel Name', 'Video Name', 'Like count']).reset_index(drop=True)
        df5.index += 1
        st.dataframe(df5)

    elif question_tosql == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        st.write('**Note:- In November 2021, YouTube removed the public dislike count from all of its videos.**')
        cursor.execute(
            "SELECT YoutubeChannel.Channel_Name, Videos.Video_Name, Videos.Like_Count, Videos.Dislike_Count FROM YoutubeChannel JOIN Playlist ON YoutubeChannel.Channel_Id = Playlist.channel_id JOIN Videos ON Playlist.channel_playlist_id = Videos.Playlist_Id ORDER BY Videos.Like_Count DESC;")
        result_6 = cursor.fetchall()
        df6 = pd.DataFrame(result_6, columns=['Channel Name', 'Video Name', 'Like count', 'Dislike count']).reset_index(
            drop=True)
        df6.index += 1
        st.dataframe(df6)

    elif question_tosql == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        cursor.execute("SELECT Channel_Name, channel_view_count FROM YoutubeChannel ORDER BY channel_view_count DESC;")
        result_7 = cursor.fetchall()
        df7 = pd.DataFrame(result_7, columns=['Channel Name', 'Total number of views']).reset_index(drop=True)
        df7.index += 1
        st.dataframe(df7)
        fig = px.pie(df7, values='Total number of views', names='Channel Name')
        st.write(fig)


    elif question_tosql == '8. What are the names of all the channels that have published videos in the year 2022?':
        cursor.execute(
            "SELECT YoutubeChannel.Channel_Name, Videos.Video_Name, Videos.PublishedAt FROM YoutubeChannel JOIN Playlist ON YoutubeChannel.Channel_Id = playlist.channel_id JOIN Videos ON playlist.channel_playlist_id = Videos.Playlist_Id  WHERE EXTRACT(YEAR FROM PublishedAt) = 2022;")
        result_8 = cursor.fetchall()
        df8 = pd.DataFrame(result_8, columns=['Channel Name', 'Video Name', 'Year 2022 only']).reset_index(drop=True)
        df8.index += 1
        st.dataframe(df8)

    elif question_tosql == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        cursor.execute(
            "SELECT YoutubeChannel.Channel_Name, TIME_FORMAT(SEC_TO_TIME(AVG(TIME_TO_SEC(TIME(Videos.Video_Duration)))), '%H:%i:%s') AS duration  FROM YoutubeChannel JOIN Playlist ON YoutubeChannel.Channel_Id = playlist.Channel_Id JOIN Videos ON playlist.channel_playlist_id = Videos.Playlist_Id GROUP by Channel_Name ORDER BY duration DESC")
        result_9 = cursor.fetchall()
        df9 = pd.DataFrame(result_9, columns=['Channel Name', 'Average duration of videos (HH:MM:SS)']).reset_index(
            drop=True)
        df9.index += 1
        st.dataframe(df9)

    elif question_tosql == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        cursor.execute(
            "SELECT YoutubeChannel.Channel_Name, Videos.Video_Name, Videos.Comment_Count FROM YoutubeChannel JOIN Playlist ON YoutubeChannel.Channel_Id = playlist.channel_id JOIN Videos ON playlist.channel_playlist_id = Videos.Playlist_Id ORDER BY Videos.Comment_Count DESC")
        result_10 = cursor.fetchall()
        df10 = pd.DataFrame(result_10, columns=['Channel Name', 'Video Name', 'Number of comments']).reset_index(drop=True)
        df10.index += 1
        st.dataframe(df10)
