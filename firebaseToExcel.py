import os
import firebase_admin
from firebase_admin import credentials, firestore
import openpyxl
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Firestore 초기화
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Firestore 데이터 가져오기
collection_name = "songs"
docs = db.collection(collection_name).stream()

# 엑셀 파일 생성
workbook = openpyxl.Workbook()
sheet = workbook.active

# 엑셀 헤더 추가
headers = ["track_id", "title", "artist", "artist_id", "album_title"]
sheet.append(headers)

# Firestore 데이터 엑셀에 추가
for doc in docs:
    data = doc.to_dict()
    row = [
        data.get("track_id", ""),
        data.get("title", ""),
        data.get("artist", ""),
        data.get("artist_id", ""),
        data.get("album_title", ""),
    ]
    sheet.append(row)

# 엑셀 저장
workbook.save("day6_songs.xlsx")
print("데이터가 day6_songs.xlsx에 저장되었습니다.")
