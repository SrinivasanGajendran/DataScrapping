import streamlit as st
import main
from googleapiclient.discovery import build
st.set_page_config(page_title='YTDH', page_icon=":tada", layout='wide')

api_service_name = 'youtube'
api_version = 'v3'
youtube = build(api_service_name,api_version,developerKey='AIzaSyAhuXky7gqy86lvokdcdXgZWvyvMVlayoY')

st.title('Youtube_Data_Harvesting')

user_input = st.number_input('''How many channel_id's you are going to enter''',min_value=1, value=1, step=1)
comments_input = st.number_input('''how many comments required for each video ''',min_value=1, value=1, step=1)
max_comments = int(comments_input)

ch = []
comments={}
data=[]
count = 0

integer = int(user_input)
for i in range(integer):
        box_label = f"Channel_Id {i + 1}"
        user_input = st.text_input(box_label)
        ch.append(user_input)
if st.button('Submit'):
        main.DB_Create()
        for i in ch:
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
            video_id = []
            videos = {}
            for item in playlist_items:
                video_id.append(item['contentDetails']['videoId'])
            for v in video_id:
                video = main.Video_Details(youtube, v)
                main.get_video_comments(youtube, v, max_comments)
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
                    "Video_Duration": video_duration,
                    'comments': comments
                }
                data.append(videos)
                main.Video(videos)
                count += 1
                new = {'channel': channel, 'video': data}
                #print(videos)
                main.Comments(comments)
            main.upload_to_DB()
            main.SQL_Channel(channel)
            main.playlist(channel)
