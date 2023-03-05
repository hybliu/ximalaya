#!/usr/bin/env python
#encoding:utf-8
import os
import json
import copy
import requests
from pydub import AudioSegment
from bs4 import BeautifulSoup
headers = {'User-Agent':'Unnecessary semicolonMozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}

def get_album_name(album_id=''):
    url = r'https://www.ximalaya.com/album/{}'.format(album_id)
    res = requests.get(url=url, headers=headers)
    reslut=res.content.decode("utf-8")
    soup = BeautifulSoup(reslut,"lxml")
    album_name = soup.find_all('h1')[0].text
    album_name = album_name.replace('|','_')
    return album_name
def get_album_info_list(album_id='', page_size=30):
    print("## get_album_info_list")
    song_info_list = []
    song_info = {}
    i = 1
    for page in range(1, 1000):
        print('正在解析第{}页'.format(i))
        i += 1
        url = f'https://www.ximalaya.com/revision/album/v1/getTracksList?albumId={album_id}&pageNum={page}&sort=1&pageSize={page_size}'
        res = requests.get(url=url, headers=headers)
        jsonData = json.loads(res.text)
        tracks_list = jsonData['data']['tracks']
        if tracks_list:
            for track in tracks_list:
                idx = track['index']
                title = track['title']
                song_info["trackId"] = track['trackId']
                song_info["name"] = f"p{idx:03d}_{title}"
                song_info_list.append(copy.deepcopy(song_info))
        else:
            break
    print('解析完毕')
    return song_info_list
def get_audio_url_list(song_info_list):
    print("## get_audio_url_list")
    i = 1 
    for info in song_info_list:
        print('正在获取第{}项地址，共{}项'.format(i,len(song_info_list)))
        i += 1
        audio_info_url = f"https://www.ximalaya.com/revision/play/v1/audio?id={info['trackId']}&ptype=1"
        res = requests.get(url=audio_info_url, headers=headers)
        jsonData = json.loads(res.text)
        if jsonData["ret"] != 200:
            continue
        if "src" in jsonData["data"]:
            info['audio_url'] = jsonData["data"]["src"]   
    return song_info_list

def download_and_convert_audio(path,album_name,url_list):
    headers = {'User-Agent':'Unnecessary semicolonMozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}
    save_path = path + album_name + '/'
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    i = 1
    for item in url_list:
        print('正在下载第{}项，共{}项'.format(i,len(url_list)))
        i+=1
        try:
            file_path = save_path + item['name'] + '.m4a'
            if not os.path.exists(file_path):
                r = requests.get(item['audio_url'], headers = headers)
                with open(file_path,'wb') as f:
                    f.write(r.content)
                    f.close()
        except:
            print(item['name'],"爬取失败")
    i = 1
    for filename in os.listdir(save_path):
        print('正在转换第{}项，共{}项'.format(i,len(os.listdir(save_path))))
        i+=1
        try:
            if filename.endswith('m4a'):
                filepath = save_path + filename
                file = AudioSegment.from_file(filepath)
                mp3_save_path = save_path + filename[:len(filename)-4] + '.mp3'
                file.export(mp3_save_path,format='MP3')
        except:
            print(filename,"转换失败")

if __name__ == "__main__":
    path = r'D:/ximalaya/'
    album_id ='46345586'
    album_name = get_album_name(album_id=album_id)
    song_info_list = get_album_info_list(album_id=album_id)
    url_list = get_audio_url_list(song_info_list)
    download_and_convert_audio(path,album_name,url_list)