# Chạy ở local : 
## Kích hoạt virtual environment
source .\venv\Scripts\activate
## Chạy server
uvicorn app.main:app --reload --port 8000

🌐  Chạy Frontend Locally
cd badminton-frontend
## Chạy Angular dev server
ng serve

# Chạy ở server : 

## backend : 
git add -A; git status
git commit -m [message]; 
git push
## front end
cd badminton-frontend
vercel --prod