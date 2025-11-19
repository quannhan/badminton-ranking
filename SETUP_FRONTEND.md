# 🏸 HƯỚNG DẪN CHẠY FRONTEND ANGULAR

## Bước 1: Cài đặt Node.js và Angular CLI

### Cài đặt Node.js
1. Tải Node.js từ: https://nodejs.org/ (chọn bản LTS)
2. Cài đặt và kiểm tra:
```powershell
node --version
npm --version
```

### Cài đặt Angular CLI
```powershell
npm install -g @angular/cli
ng version
```

## Bước 2: Tạo và cấu hình project

### Option A: Sử dụng code đã tạo sẵn
Nếu bạn đã có thư mục `badminton-frontend` với các file đã tạo:

```powershell
cd d:\python_project\Badminton_ranking\badminton-frontend
npm install
```

### Option B: Tạo mới từ đầu
```powershell
cd d:\python_project\Badminton_ranking
ng new badminton-frontend --routing --style=scss
cd badminton-frontend
npm install bootstrap @ng-bootstrap/ng-bootstrap bootstrap-icons
```

## Bước 3: Chạy Backend API (FastAPI)

Mở terminal thứ nhất:
```powershell
cd d:\python_project\Badminton_ranking
# Kích hoạt virtual environment nếu có
.\venv\Scripts\Activate.ps1

# Chạy FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API sẽ chạy tại: http://localhost:8000

## Bước 4: Chạy Frontend Angular

Mở terminal thứ hai:
```powershell
cd d:\python_project\Badminton_ranking\badminton-frontend
ng serve --open
```

Hoặc:
```powershell
npm start
```

Frontend sẽ tự động mở tại: http://localhost:4200

## Bước 5: Sử dụng ứng dụng

1. **Đăng ký tài khoản mới:**
   - Truy cập http://localhost:4200/register
   - Điền thông tin và chọn level (A/B/C)
   - Click "Đăng ký"

2. **Đăng nhập:**
   - Truy cập http://localhost:4200/login
   - Nhập username và password
   - Click "Đăng nhập"

3. **Dashboard:**
   - Xem thông tin cá nhân
   - Truy cập các chức năng khác

4. **Xem bảng xếp hạng:**
   - Click "Bảng xếp hạng" trên menu
   - Chọn loại và level để xem

## Cấu trúc project đã tạo

```
badminton-frontend/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── login/               # Trang đăng nhập
│   │   │   ├── register/            # Trang đăng ký
│   │   │   ├── dashboard/           # Trang chính
│   │   │   └── rankings/            # Bảng xếp hạng
│   │   ├── services/
│   │   │   ├── auth.service.ts      # Xác thực người dùng
│   │   │   ├── match.service.ts     # Quản lý trận đấu
│   │   │   └── ranking.service.ts   # Bảng xếp hạng
│   │   ├── guards/
│   │   │   └── auth.guard.ts        # Bảo vệ routes
│   │   ├── interceptors/
│   │   │   └── auth.interceptor.ts  # Tự động thêm JWT token
│   │   ├── models/                  # TypeScript interfaces
│   │   │   ├── user.model.ts
│   │   │   ├── match.model.ts
│   │   │   └── ranking.model.ts
│   │   ├── app.module.ts            # Module chính
│   │   ├── app-routing.module.ts    # Routing config
│   │   └── app.component.*          # Component chính
│   ├── environments/
│   │   ├── environment.ts           # Config dev
│   │   └── environment.prod.ts      # Config production
│   ├── styles.scss                  # Global styles
│   └── index.html
├── package.json
└── README.md
```

## Tính năng đã implement

✅ Login/Register với validation
✅ JWT Authentication
✅ Route Guards (bảo vệ trang yêu cầu đăng nhập)
✅ HTTP Interceptor (tự động thêm token)
✅ Dashboard với thông tin người dùng
✅ Bảng xếp hạng (overall và theo loại)
✅ Responsive design với Bootstrap 5
✅ Navigation menu
✅ User profile dropdown

## Các tính năng cần thêm (tuỳ chọn)

📝 Report Match Component - Báo cáo trận đấu
📝 Match History Component - Lịch sử trận đấu
📝 Admin Panel - Trang quản trị (approve/reject matches)
📝 User Profile Page - Trang cá nhân chi tiết
📝 Notifications - Thông báo

## Tạo thêm components

```powershell
# Report Match
ng generate component components/report-match

# Match History
ng generate component components/match-history

# Admin Panel
ng generate component components/admin

# User Profile
ng generate component components/profile
```

## Build cho production

```powershell
ng build --configuration production
```

File build sẽ ở thư mục `dist/badminton-frontend/`

## Troubleshooting

### Lỗi CORS
Nếu gặp lỗi CORS, đảm bảo backend có cấu hình:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Lỗi không kết nối được API
- Kiểm tra backend đang chạy tại http://localhost:8000
- Kiểm tra `environment.ts` có đúng apiUrl
- Mở DevTools (F12) để xem lỗi trong Console

### Port 4200 đã được sử dụng
```powershell
ng serve --port 4201
```

## Các lệnh hữu ích

```powershell
# Chạy dev server
ng serve

# Chạy và tự động mở browser
ng serve --open

# Build production
ng build --prod

# Chạy tests
ng test

# Generate component
ng generate component <name>

# Generate service
ng generate service <name>
```

## Tài liệu tham khảo

- Angular: https://angular.io/docs
- Bootstrap: https://getbootstrap.com/docs/5.3/
- RxJS: https://rxjs.dev/guide/overview
- TypeScript: https://www.typescriptlang.org/docs/
