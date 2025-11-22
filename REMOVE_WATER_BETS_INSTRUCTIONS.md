# Hướng dẫn xóa các kèo 2 điểm (Kèo nước)

## ⚠️ CẢNH BÁO
Script này sẽ XÓA VĨNH VIỄN tất cả các kèo 2 điểm và điều chỉnh lại điểm của người chơi. Hãy chắc chắn bạn đã backup database trước khi thực hiện!

## 📋 Các bước thực hiện

### Bước 1: Backup Database
```bash
# Backup từ Supabase hoặc PostgreSQL của bạn
pg_dump -h [your-host] -U [your-user] -d [your-database] > backup_before_remove_water_bets.sql
```

### Bước 2: Kết nối đến Database

#### Option A: Sử dụng Supabase SQL Editor
1. Đăng nhập vào Supabase Dashboard
2. Chọn project của bạn
3. Vào **SQL Editor**
4. Copy nội dung file `remove_water_bets.sql` và paste vào editor
5. Click **Run** để thực thi

#### Option B: Sử dụng psql command line
```bash
psql "postgresql://[user]:[password]@[host]:[port]/[database]" -f remove_water_bets.sql
```

#### Option C: Sử dụng Python script
```python
from app.database import engine
from sqlalchemy import text

with open('remove_water_bets.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()

with engine.connect() as conn:
    conn.execute(text(sql_script))
    conn.commit()
```

### Bước 3: Kiểm tra kết quả

Script sẽ hiển thị:
1. Danh sách người chơi bị ảnh hưởng với điểm cũ và điểm mới
2. Số lượng kèo 2 điểm sẽ bị xóa (theo trạng thái)
3. Xác nhận việc xóa hoàn tất
4. Kiểm tra không có ai có điểm âm

### Bước 4: Verify sau khi xóa

```sql
-- Kiểm tra không còn kèo 2 điểm
SELECT COUNT(*) FROM match_reports WHERE stake_value = 2;
-- Kết quả phải là 0

-- Kiểm tra điểm của người chơi
SELECT user_id, display_name, total_points, singles_points, doubles_points 
FROM users 
ORDER BY total_points DESC 
LIMIT 10;
```

## 🔄 Frontend Changes

Frontend đã được cập nhật để loại bỏ tùy chọn 2 điểm:

1. ✅ `admin.component.ts` - Removed stake value 2
2. ✅ `report-match-modal.component.ts` - Removed stake value 2
3. ✅ `translations.ts` - Removed water bet translations
4. ✅ `scoring-rules.component.html` - Updated examples to use 5 points

## 📝 Thống kê trước khi xóa

Để xem thống kê trước khi xóa:

```sql
-- Tổng số kèo 2 điểm
SELECT 
    COUNT(*) as total_water_matches,
    SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved,
    SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending,
    SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected
FROM match_reports 
WHERE stake_value = 2;

-- Tổng điểm từ kèo 2 điểm sẽ bị trừ đi
SELECT 
    COUNT(DISTINCT mp.user_id) as affected_users,
    SUM(mp.points_earned) as total_points_to_deduct
FROM match_players mp
JOIN match_reports mr ON mp.match_id = mr.match_id
WHERE mr.stake_value = 2 AND mr.status = 'APPROVED';
```

## ⚡ Deploy Changes

### Backend
```bash
git add .
git commit -m "Remove 2-point water bets from system"
git push
# Render sẽ tự động deploy
```

### Frontend
```bash
cd badminton-frontend
git add .
git commit -m "Remove 2-point stake option from UI"
git push
# Vercel sẽ tự động deploy
```

## 🔙 Rollback (nếu cần)

Nếu có vấn đề, restore từ backup:

```bash
psql "postgresql://[connection-string]" < backup_before_remove_water_bets.sql
```

## ✅ Checklist

- [ ] Đã backup database
- [ ] Đã xem thống kê trước khi xóa
- [ ] Đã chạy SQL script
- [ ] Đã verify kết quả (không còn stake_value = 2)
- [ ] Đã verify không có điểm âm
- [ ] Đã commit frontend changes
- [ ] Đã push và deploy
- [ ] Đã test tạo kèo mới (chỉ có 5 và 10 điểm)

## 📞 Support

Nếu có vấn đề, liên hệ quản trị viên hệ thống.
