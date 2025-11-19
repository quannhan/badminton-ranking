# 🚀 QUICK START - Deploy trong 15 phút

## Bước 1: Supabase (3 phút)
1. https://supabase.com → Sign up (GitHub)
2. New Project → Name: `badminton-club` → Chọn Singapore → Tạo password → Create
3. Settings → Database → Connection string (URI) → Copy
4. SQL Editor → New query → Copy/paste file `migrations/*.sql` → Run

## Bước 2: Render.com (5 phút)
1. https://render.com → Sign up (GitHub)
2. New + → Web Service → Connect GitHub repo
3. Điền:
   - Name: `badminton-api`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Free tier
4. Environment Variables:
   ```
   DATABASE_URL = [paste từ Supabase]
   SECRET_KEY = [random string - dùng: openssl rand -hex 32]
   FRONTEND_URL = https://badminton-ranking.vercel.app
   ```
5. Create → Chờ → Copy URL

## Bước 3: Update Code (2 phút)
1. Sửa `badminton-frontend/src/environments/environment.prod.ts`:
   ```typescript
   apiUrl: 'https://[YOUR-RENDER-URL].onrender.com'
   ```
2. Build:
   ```bash
   cd badminton-frontend
   npm install
   npm run build
   ```

## Bước 4: Vercel (5 phút)
```bash
npm install -g vercel
cd badminton-frontend
vercel login
vercel --prod
```
→ Làm theo hướng dẫn, chọn mặc định
→ Done! Copy URL

## Kiểm tra
- Frontend: https://[vercel-url].vercel.app
- Backend: https://[render-url].onrender.com/docs
- Đăng ký tài khoản → Login → Test!

## Xử lý Backend Sleep
Dùng https://cron-job.org:
- URL: `https://[render-url].onrender.com/health`
- Interval: Every 10 minutes
- Free!

---
**🎉 DONE! Chia sẻ link cho bạn bè!**
