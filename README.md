# 🏸 Badminton Ranking System

Hệ thống quản lý và xếp hạng câu lạc bộ cầu lông với tính năng:
- ✅ Đăng ký/Đăng nhập thành viên
- ✅ Báo cáo kết quả trận đấu
- ✅ Quản trị viên duyệt kết quả
- ✅ Bảng xếp hạng theo level (A/B/C) và loại trận
- ✅ Lịch sử đối đầu giữa các thành viên
- ✅ Reset mật khẩu (admin approve)
- ✅ Reset điểm toàn bộ thành viên (super admin)
- ✅ Ghi chú và link video YouTube cho trận đấu

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database (Supabase)
- **JWT** - Authentication
- **Bcrypt** - Password hashing

### Frontend
- **Angular 17+** - Standalone components
- **Bootstrap 5** - UI Framework
- **RxJS** - Reactive programming
- **TypeScript** - Type safety

## 📂 Cấu trúc Project

```
Badminton_ranking/
├── app/                          # Backend (FastAPI)
│   ├── main.py                  # Entry point
│   ├── models.py                # Database models
│   ├── schemas.py               # Pydantic schemas
│   ├── database.py              # DB connection
│   ├── auth.py                  # JWT authentication
│   ├── routers/                 # API endpoints
│   │   ├── users.py            # User management
│   │   ├── matches.py          # Match management
│   │   ├── admin.py            # Admin functions
│   │   └── rankings.py         # Rankings
│   └── utils/                   # Utilities
│       ├── scoring.py          # Point calculation
│       └── email.py            # Email notifications
├── badminton-frontend/          # Frontend (Angular)
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/     # UI Components
│   │   │   ├── services/       # API Services
│   │   │   ├── models/         # TypeScript models
│   │   │   └── guards/         # Route guards
│   │   └── environments/       # Environment configs
├── migrations/                  # SQL migrations
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render.com config
└── vercel.json                 # Vercel config
```

## 🚀 Deployment (MIỄN PHÍ)

### Option 1: Quick Deploy (15 phút)
Làm theo hướng dẫn trong file: **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)**

### Option 2: Chi tiết từng bước
Làm theo hướng dẫn đầy đủ trong file: **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)**

### Các dịch vụ sử dụng:
- **Database**: Supabase (Free tier: 500MB)
- **Backend**: Render.com (Free tier: 750h/month)
- **Frontend**: Vercel (Free tier: Unlimited)

## 💻 Local Development

### 1. Setup Backend
```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Cài dependencies
pip install -r requirements.txt

# Setup .env
cp .env.example .env
# Sửa DATABASE_URL và SECRET_KEY trong .env

# Run server
uvicorn app.main:app --reload
```

Backend chạy tại: http://localhost:8000
API Docs: http://localhost:8000/docs

### 2. Setup Frontend
```bash
cd badminton-frontend

# Cài dependencies
npm install

# Run dev server
npm start
```

Frontend chạy tại: http://localhost:4200

### 3. Setup Database
1. Tạo database PostgreSQL (local hoặc Supabase)
2. Chạy migration scripts trong folder `migrations/`
3. Update `DATABASE_URL` trong `.env`

## 🔑 Generate SECRET_KEY

```bash
python generate_secret_key.py
```

Hoặc dùng OpenSSL:
```bash
openssl rand -hex 32
```

## 📱 Features

### User Features
- Đăng ký tài khoản (cần admin duyệt)
- Đăng nhập/Đăng xuất
- Xem bảng xếp hạng (tổng hợp, theo level, theo loại trận)
- Báo cáo kết quả trận đấu
- Xem lịch sử trận đấu của mình
- Xem profile người chơi khác
- Xem lịch sử đối đầu
- Quên mật khẩu (yêu cầu admin reset)
- Đổi mật khẩu

### Admin Features
- Duyệt/Từ chối đăng ký thành viên mới
- Tạo trận đấu (tự động duyệt)
- Duyệt/Từ chối kết quả trận đấu
- Xem danh sách tất cả thành viên
- Duyệt/Từ chối yêu cầu reset mật khẩu

### Super Admin Features
- Reset điểm toàn bộ thành viên (yêu cầu xác nhận mật khẩu)
- Tất cả quyền của Admin

## 🎯 Quy tắc tính điểm

### Loại trận:
- **Đơn** (Singles): 1v1
- **Đôi nam** (Doubles Men): 2v2 nam
- **Đôi nữ** (Doubles Women): 2v2 nữ
- **Đôi nam nữ** (Doubles Mixed): 2v2 nam nữ

### Level:
- **A**: Cao thủ
- **B**: Trung bình
- **C**: Mới chơi

### Điểm thưởng/phạt:
- **Thắng**: +3 điểm
- **Thua**: -1 điểm
- **Điểm tổng** = Điểm đơn + Điểm đôi

## 🐛 Xử lý sự cố

### Backend bị sleep (Render free tier):
- Request đầu tiên sau 15 phút không hoạt động sẽ mất 30-50s để wake up
- **Giải pháp**: Dùng cron job ping mỗi 10 phút
  - Sử dụng https://cron-job.org (miễn phí)
  - Ping URL: `https://your-backend.onrender.com/health`
  - Hoặc mở file `keep-alive.html` trong trình duyệt

### CORS Error:
- Kiểm tra `FRONTEND_URL` trong Render environment variables
- Đảm bảo `app/main.py` đã cập nhật CORS config

### Database connection error:
- Kiểm tra `DATABASE_URL` có đúng format không
- Đảm bảo đã thay `[YOUR-PASSWORD]` bằng password thật
- Kiểm tra Supabase project có active không

## 📊 Database Schema

### Main Tables:
- `users` - Thông tin thành viên
- `user_settings` - Cài đặt người dùng (require_password_change)
- `match_reports` - Báo cáo trận đấu
- `match_players` - Người chơi trong trận
- `rankings` - Bảng xếp hạng theo tháng
- `notifications` - Thông báo
- `password_reset_requests` - Yêu cầu reset mật khẩu

## 🔐 Security

- Password hashing với Bcrypt
- JWT token authentication
- Admin role-based access control
- Super admin với email hardcoded
- Environment variables cho sensitive data
- CORS configuration cho production

## 📝 API Endpoints

### Authentication
- `POST /users/register` - Đăng ký
- `POST /users/login` - Đăng nhập
- `GET /users/me` - Lấy thông tin user hiện tại

### Matches
- `POST /matches/report` - Báo cáo kết quả
- `GET /matches/my-matches` - Lịch sử trận đấu

### Rankings
- `GET /rankings/overall/{level}` - Xếp hạng tổng
- `GET /rankings/{match_type}/{level}` - Xếp hạng theo loại

### Admin
- `GET /admin/pending-users` - Danh sách user chờ duyệt
- `POST /admin/approve-match/{match_id}` - Duyệt trận
- `POST /admin/reset-all-points` - Reset điểm (super admin)

**Full API Documentation**: http://localhost:8000/docs

## 📞 Support

- **Issues**: Tạo issue trên GitHub
- **Email**: thaiquan251198@gmail.com

## 📄 License

MIT License - Free to use and modify

---

**Phát triển bởi**: Thái Quân
**Version**: 1.0.0
**Last Updated**: November 2025
