import os
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

# .env 파일 로드
load_dotenv()

# Firestore 초기화
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 요청 헤더 설정
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

# 세부 페이지 URL에서 곡 정보를 크롤링하고 Firestore에 저장하는 함수
def add_single_track(track_url):
    # 곡 정보 크롤링
    response = requests.get(track_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        # URL에서 track_id 추출
        parsed_url = urlparse(track_url)
        track_id = parsed_url.path.split('/')[-1]

        # 데이터 추출
        title = soup.select_one('#container > header > div > h1').text.strip()

        album_titme_row = soup.find('th', string='앨범')
        album_title = album_titme_row.find_next('td').find('a').text.strip()

        album_img = soup.select_one('#container > section.sectionPadding.summaryInfo.summaryTrack > div > div.basicInfo > div > ul > li > a > img')['src']

        artist_element = soup.select_one('#container > section.sectionPadding.summaryInfo.summaryTrack > div > div.basicInfo > table > tbody > tr:nth-child(1) > td > a')
        artist = artist_element.text.strip()
        artist_url = artist_element['href']
        artist_id = urlparse(artist_url).path.split('/')[-1]

        play_time_row = soup.find('th', string='재생 시간')
        play_time = play_time_row.find_next('td').find('time').text

        # Firestore에 저장할 데이터 구성
        track_data = {
            "track_id": track_id,
            "title": title,
            "artist": artist,
            "album_title": album_title,
            "album_img": album_img,
            "play_time": play_time,
            "artist_id": artist_id
        }

        # Firestore 저장
        db.collection('songs').document(track_id).set(track_data)
        print(f"'{track_data}' has been added to Firestore.")
        return track_data

    except Exception as e:
        print(f"Error adding track from URL {track_url}: {e}")
        return None

# 곡 디테일 페이지 링크 넣으면 곡 추가 가능
if __name__ == "__main__":
    add_single_track(f'https://music.bugs.co.kr/track/94478745?wl_ref=list_tr_08_search')
