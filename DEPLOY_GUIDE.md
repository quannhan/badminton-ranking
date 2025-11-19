# 🚀 Hướng dẫn Deploy Miễn Phí

## 📋 Tổng quan
- **Backend**: Render.com (Free tier - 750 giờ/tháng)
- **Frontend**: Vercel (Free tier - Unlimited)
- **Database**: Supabase (Free tier - 500MB)

---

## 🗄️ BƯỚC 1: Chuẩn bị Database (Supabase)

### 1.1. Đăng ký Supabase
1. Truy cập: https://supabase.com
2. Đăng ký tài khoản miễn phí (dùng GitHub/Google)
3. Click **"New Project"**
4. Điền thông tin:
   - Name: `badminton-club`
   - Database Password: **LƯU MẬT KHẨU NÀY**
   - Region: Singapore (gần VN nhất)
5. Click **"Create new project"** (chờ 2-3 phút)

### 1.2. Lấy DATABASE_URL
1. Vào project vừa tạo
2. Click **Settings** (góc trái dưới)
3. Click **Database**
4. Tìm mục **"Connection string"** > chọn **URI**
5. Copy chuỗi dạng: `postgresql://postgres:[YOUR-PASSWORD]@...supabase.co:5432/postgres`
6. **QUAN TRỌNG**: Thay `[YOUR-PASSWORD]` bằng mật khẩu bạn đã tạo ở bước 1.1

### 1.3. Chạy SQL Migration
1. Trong Supabase, click **SQL Editor** (bên trái)
2. Click **"New query"**
3. Copy toàn bộ nội dung file `migrations/add_password_reset.sql` vào
4. Click **"Run"**
5. Lặp lại với các file SQL khác trong folder `migrations/` nếu có

---

## 🖥️ BƯỚC 2: Deploy Backend (Render.com)

### 2.1. Chuẩn bị Code
1. Tạo file `.gitignore` (nếu chưa có):
```
__pycache__/
*.pyc
.env
.venv/
venv/
*.db
.DS_Store
database_info.txt
```

2. Push code lên GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/[YOUR-USERNAME]/badminton-ranking.git
git push -u origin main
```

### 2.2. Deploy trên Render
1. Truy cập: https://render.com
2. Đăng ký miễn phí (dùng GitHub)
3. Click **"New +"** > **"Web Service"**
4. Chọn repository GitHub vừa push
5. Điền thông tin:
   - **Name**: `badminton-api`
   - **Region**: Singapore
   - **Branch**: `main`
   - **Root Directory**: để trống
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: **Free**

6. Click **"Advanced"** > **Add Environment Variable**:
   ```
   DATABASE_URL = postgresql://postgres:...  (copy từ Supabase)
   SECRET_KEY = [tạo chuỗi random phức tạp, vd: openssl rand -hex 32]
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 43200
   ```

7. Click **"Create Web Service"**
8. Chờ deploy (5-10 phút)
9. **LƯU URL**: Render sẽ cấp URL dạng `https://badminton-api.onrender.com`

### 2.3. Kiểm tra Backend
- Truy cập: `https://badminton-api.onrender.com/docs`
- Nếu thấy Swagger UI → Backend OK! ✅

### ⚠️ LƯU Ý Render Free Tier:
- **Tự động sleep sau 15 phút không dùng**
- **Request đầu tiên sau khi sleep sẽ mất 30-50 giây để wake up**
- **750 giờ/tháng = ~25 giờ/ngày** (đủ dùng nếu không có nhiều traffic)

---

## 🌐 BƯỚC 3: Deploy Frontend (Vercel)

### 3.1. Cập nhật API URL
1. Mở file: `badminton-frontend/src/environments/environment.ts`
2. Thay đổi:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};
```

3. Tạo file: `badminton-frontend/src/environments/environment.prod.ts`
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://badminton-api.onrender.com'  // URL Render vừa lấy
};
```

4. Cập nhật `angular.json` để dùng environment.prod.ts khi build:
   - Tìm `"configurations"` > `"production"`
   - Thêm/kiểm tra:
   ```json
   "fileReplacements": [
     {
       "replace": "src/environments/environment.ts",
       "with": "src/environments/environment.prod.ts"
     }
   ]
   ```

### 3.2. Build Frontend
```bash
cd badminton-frontend
npm install
npm run build
```
- Kiểm tra folder `dist/badminton-frontend` được tạo

### 3.3. Deploy lên Vercel

#### Cách 1: Deploy qua Vercel CLI (Khuyên dùng)
```bash
# Cài Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd badminton-frontend
vercel --prod
```
- Làm theo hướng dẫn, chọn các option mặc định
- **LƯU URL**: Vercel cấp URL dạng `https://badminton-ranking.vercel.app`

#### Cách 2: Deploy qua Web UI
1. Truy cập: https://vercel.com
2. Đăng ký miễn phí (dùng GitHub)
3. Click **"Add New..."** > **"Project"**
4. Import repository GitHub (nếu đã push frontend lên GitHub)
5. Điền thông tin:
   - **Framework Preset**: Angular
   - **Root Directory**: `badminton-frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist/badminton-frontend/browser` (Angular 17+)
6. Click **"Deploy"**
7. Chờ 2-3 phút

### 3.4. Cập nhật CORS Backend
1. Quay lại Render.com > vào Web Service backend
2. Click **"Environment"**
3. Thêm biến:
   ```
   FRONTEND_URL = https://badminton-ranking.vercel.app
   ```
4. **LƯU Ý**: Cần update code `app/main.py` để dùng FRONTEND_URL

---

## 🔧 BƯỚC 4: Cập nhật CORS (Quan trọng!)

### 4.1. Sửa file `app/main.py`:
```python
# CORS configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4.2. Push lại code:
```bash
git add .
git commit -m "Update CORS for production"
git push
```
- Render sẽ tự động deploy lại (2-3 phút)

---

## ✅ BƯỚC 5: Kiểm tra hoạt động

1. **Truy cập Frontend**: `https://badminton-ranking.vercel.app`
2. **Đăng ký tài khoản mới**
3. **Đăng nhập**
4. **Tạo trận đấu thử**

### Nếu có lỗi:
- **Lỗi CORS**: Kiểm tra lại FRONTEND_URL trong Render
- **Backend không response**: Chờ 30-50s (wake up từ sleep)
- **500 Error**: Kiểm tra Logs trong Render Dashboard

---

## 💰 Chi phí (MIỄN PHÍ HOÀN TOÀN)

| Dịch vụ | Free Tier | Giới hạn |
|---------|-----------|----------|
| **Supabase** | 500MB Database | Đủ cho ~5000 users |
| **Render** | 750 giờ/tháng | Sleep sau 15 phút không dùng |
| **Vercel** | Unlimited | 100GB bandwidth/tháng |

### Khi nào cần trả tiền?
- **Supabase**: Khi DB > 500MB (hiếm khi xảy ra với app nhỏ)
- **Render**: Khi muốn backend KHÔNG sleep ($7/tháng)
- **Vercel**: Khi > 100GB bandwidth (rất khó đạt với app nhỏ)

---

## 🔄 Cập nhật Code sau này

### Backend:
```bash
git add .
git commit -m "Update backend"
git push
```
- Render tự động deploy lại

### Frontend:
```bash
cd badminton-frontend
npm run build
vercel --prod
```
- Hoặc push lên GitHub, Vercel tự động deploy

---

## 🆘 Xử lý sự cố

### Backend bị sleep:
- **Giải pháp**: Dùng cron job ping mỗi 10 phút
- **Free cron**: https://cron-job.org
- **URL ping**: `https://badminton-api.onrender.com/health`

### Database đầy:
- **Xem logs**: Render Dashboard > Logs
- **Xóa dữ liệu cũ**: Viết API để cleanup matches cũ

### Build frontend lỗi:
```bash
# Xóa cache
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 📱 Tùy chỉnh Domain (Optional)

### Vercel:
1. Mua domain (Namecheap, Cloudflare - ~$1/năm)
2. Vercel Settings > Domains > Add
3. Thêm CNAME record vào DNS

### Render:
1. Settings > Custom Domain > Add
2. Cập nhật DNS theo hướng dẫn

---

## 🎉 Hoàn thành!

Website của bạn đã online tại:
- **Frontend**: https://badminton-ranking.vercel.app
- **API**: https://badminton-api.onrender.com
- **API Docs**: https://badminton-api.onrender.com/docs

**Chia sẻ link cho bạn bè để sử dụng!** 🏸
