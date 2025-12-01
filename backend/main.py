from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data.route import data_route

app = FastAPI()

# ----------- CORS AYARLARI -----------
origins = [
    "http://localhost:3000",   # Next.js dev ortamı
    "http://127.0.0.1:3000",
    # Eğer deploy edeceksen domaine buraya eklersin:
    # "https://your-frontend-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # izin verilen kaynaklar
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, PUT, DELETE hepsi
    allow_headers=["*"],        # Authorization dahil tüm headerlar
)
# -------------------------------------

app.include_router(data_route)
