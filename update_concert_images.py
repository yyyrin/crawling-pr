import os
import firebase_admin
from firebase_admin import credentials, firestore, storage
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Firestore Admin 초기화
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    "storageBucket": "nolda-obsida.firebasestorage.app"
})

# Firestore와 Storage 초기화
db = firestore.client()
bucket = storage.bucket()

# Firestore concerts 컬랙션 가져오기
def update_concert_images():
    concerts_ref = db.collection("concerts")
    concerts = concerts_ref.stream()

    for concert in concerts:
        concert_id = concert.id

        poster_paths = [f"poster/{concert_id}-poster.jpeg", f"poster/{concert_id}-poster.jpg"]
        review_paths = [f"review/{concert_id}-review.jpeg", f"review/{concert_id}-review.jpg"]

        poster_url = ""
        review_url = ""

        for path in poster_paths:
            blob = bucket.blob(path)
            if blob.exists():
                poster_url = f"gs://{bucket.name}/{path}"
                break  # 첫 번째로 존재하는 경로를 선택

        for path in review_paths:
            blob = bucket.blob(path)
            if blob.exists():
                review_url = f"gs://{bucket.name}/{path}"
                break  # 첫 번째로 존재하는 경로를 선택

        # Firestore 업데이트
        concerts_ref.document(concert_id).update({
            "poster_url": poster_url,
            "review_url": review_url
        })
        print(f"Updated {concert_id}: poster_url={poster_url}, review_url={review_url}")

update_concert_images()
