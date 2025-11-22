# 🚀 HƯỚNG DẪN NHANH: Xóa Kèo Nước (2 điểm)

## Bước 1: Chạy Python Script (KHUYẾN NGHỊ) ⭐

```bash
cd d:\python_project\Badminton_ranking
python remove_water_bets_script.py
```

Script sẽ:
- ✅ Hiển thị thống kê trước khi xóa
- ✅ Hiển thị danh sách người chơi bị ảnh hưởng
- ✅ Yêu cầu xác nhận bằng cách gõ "YES"
- ✅ Tự động rollback nếu có lỗi
- ✅ Kiểm tra không có điểm âm

## Bước 2: Verify Kết Quả

Sau khi script chạy xong, kiểm tra:

### Option A: Supabase SQL Editor
```sql
-- Kiểm tra không còn kèo 2 điểm
SELECT COUNT(*) FROM match_reports WHERE stake_value = 2;
-- Kết quả phải là 0

-- Xem top 10 người chơi
SELECT user_id, display_name, total_points, singles_points, doubles_points 
FROM users 
ORDER BY total_points DESC 
LIMIT 10;
```

### Option B: Sử dụng API
1. Truy cập: https://badminton-api-d0cc.onrender.com/docs
2. Test endpoint `/users/me` để xem điểm của bạn

## Bước 3: Test Frontend

1. Đăng nhập vào web: https://badminton-frontend-rosy.vercel.app
2. Vào trang Admin hoặc "Báo Cáo Kết Quả"
3. Kiểm tra dropdown "Điểm cược" chỉ có **5** và **10** (không còn "Kèo nước")
4. Vào "Hệ thống tính điểm" - ví dụ phải bắt đầu từ 5 điểm

## ⚠️ LƯU Ý QUAN TRỌNG

### Frontend đã được deploy:
- ✅ Loại bỏ option 2 điểm khỏi form
- ✅ Cập nhật translations
- ✅ Cập nhật scoring examples

### Backend:
- ⚠️ Chưa có validation từ chối stake_value = 2
- 🔧 Nên thêm validation nếu cần

## 📊 Thống Kê Trước Khi Xóa

Nếu muốn xem stats trước:

```sql
-- Tổng số kèo 2 điểm
SELECT 
    COUNT(*) as total_water_matches,
    SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved,
    SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending
FROM match_reports 
WHERE stake_value = 2;

-- Người chơi bị ảnh hưởng
SELECT 
    u.display_name,
    u.total_points as current_points,
    SUM(mp.points_earned) as points_from_water_bets,
    u.total_points - SUM(mp.points_earned) as new_points
FROM users u
JOIN match_players mp ON u.user_id = mp.user_id
JOIN match_reports mr ON mp.match_id = mr.match_id
WHERE mr.stake_value = 2 AND mr.status = 'APPROVED'
GROUP BY u.user_id, u.display_name, u.total_points
ORDER BY points_from_water_bets DESC;
```

## 🔄 Nếu Cần Rollback

**TRƯỚC KHI CHẠY**, backup database:

```bash
# Từ Supabase Dashboard -> Project Settings -> Database -> Connection String
# Hoặc backup thủ công từ Supabase Dashboard
```

## 📞 Hỗ Trợ

Nếu script báo lỗi hoặc có vấn đề:
1. Kiểm tra DATABASE_URL trong file `.env`
2. Kiểm tra kết nối internet
3. Xem log chi tiết trong terminal

---

**TÓM TẮT NHANH:**
```bash
python remove_water_bets_script.py
# Gõ: YES
# Xong! ✅
```
