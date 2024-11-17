import os
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Firestroe 초기화
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 요청 헤더 설정
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

# 주어진 가수 id의 곡 데이터를 크롤링하고 Firestore에 저장하는 함수
def crawl_and_save_artist_songs(artist_id):
    results = []
    base_url = f"https://music.bugs.co.kr/artist/{artist_id}/tracks"

    for page in range(1, 100):
        # 동적 URL 생성
        url = f"{base_url}?type=RELEASE&sort=P&page={page}&roleCode=0&highQualityOnly="
        data = requests.get(url, headers=headers)
        # BeautifulSoup을 사용해 HTML 파싱
        soup = BeautifulSoup(data.text, 'html.parser')

        # 곡 목록 추출
        trs = soup.select(f'#ARTIST{artist_id} > table.trackList > tbody > tr')

        # 곡 데이터가 없으면 종료
        if not trs:
            break

        for tr in trs :
            # 권리없는 곡인지 확인
            if tr.select_one('th > p.title > span.badge.permission'):
                continue

            # 기본 정보 추출
            track_id = tr["trackid"]
            title = tr.select_one('th > p.title > a').text.strip()
            artist = tr.select_one('td.left > p.artist > a').text.strip()
            album_title = tr.select_one('td.left > a.album').text.strip()

            # 세부페이지 URL 추출
            detail_link = tr.select_one('td > a.trackInfo')['href']

            # 세부 페이지 요청 및 데이터 추출
            detail_response = requests.get(detail_link, headers=headers)
            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

            # 앨범 이미지 추출
            album_img = detail_soup.select_one('#container > section.sectionPadding.summaryInfo.summaryTrack > div > div.basicInfo > div > ul > li > a > img')['src']
            
            # 재생 시간 추출
            play_time_row = detail_soup.find('th', string='재생 시간')
            play_time = play_time_row.find_next('td').find('time').text

            # Firestore에 저장할 데이터
            song_data = {
                "track_id": track_id,
                "title": title,
                "artist": artist,
                "album_title": album_title,
                "album_img": album_img,
                "play_time": play_time,
                "artist_id": artist_id
            }

            # Firestore 저장
            db.collection('songs').document(track_id).set(song_data)
            results.append(song_data)

        
    # 확인용 출력
    print(f"{len(results)} songs from artist {artist} saved to Firestore.")
    return results

artist_ids = ["80246393"]
for artist_id in artist_ids:
    crawl_and_save_artist_songs(artist_id)
