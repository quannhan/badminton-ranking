# Create HTML templates for components

$loginHtml = @'
<div class="login-container">
  <div class="login-card">
    <div class="text-center mb-4">
      <h2>🏸 Badminton Ranking</h2>
      <p class="text-muted">Đăng nhập vào hệ thống</p>
    </div>

    <div *ngIf="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ error }}
      <button type="button" class="btn-close" (click)="error=''" aria-label="Close"></button>
    </div>

    <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
      <div class="mb-3">
        <label for="username" class="form-label">Tên đăng nhập</label>
        <input 
          type="text" 
          class="form-control" 
          id="username" 
          formControlName="username"
          [class.is-invalid]="submitted && f['username'].errors"
          placeholder="Nhập tên đăng nhập">
        <div *ngIf="submitted && f['username'].errors" class="invalid-feedback">
          <div *ngIf="f['username'].errors['required']">Vui lòng nhập tên đăng nhập</div>
        </div>
      </div>

      <div class="mb-3">
        <label for="password" class="form-label">Mật khẩu</label>
        <input 
          type="password" 
          class="form-control" 
          id="password" 
          formControlName="password"
          [class.is-invalid]="submitted && f['password'].errors"
          placeholder="Nhập mật khẩu">
        <div *ngIf="submitted && f['password'].errors" class="invalid-feedback">
          <div *ngIf="f['password'].errors['required']">Vui lòng nhập mật khẩu</div>
        </div>
      </div>

      <button type="submit" class="btn btn-primary w-100 mb-3" [disabled]="loading">
        <span *ngIf="loading" class="spinner-border spinner-border-sm me-2"></span>
        Đăng nhập
      </button>

      <div class="text-center">
        <p class="mb-0">Chưa có tài khoản? <a routerLink="/register" class="text-decoration-none">Đăng ký ngay</a></p>
      </div>
    </form>
  </div>
</div>
'@

$registerHtml = @'
<div class="register-container">
  <div class="register-card">
    <div class="text-center mb-4">
      <h2>🏸 Đăng ký tài khoản</h2>
      <p class="text-muted">Tham gia hệ thống ranking badminton</p>
    </div>

    <div *ngIf="success" class="alert alert-success" role="alert">
      Đăng ký thành công! Đang chuyển đến trang đăng nhập...
    </div>

    <div *ngIf="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ error }}
      <button type="button" class="btn-close" (click)="error=''" aria-label="Close"></button>
    </div>

    <form [formGroup]="registerForm" (ngSubmit)="onSubmit()">
      <div class="row">
        <div class="col-md-6 mb-3">
          <label for="username" class="form-label">Tên đăng nhập *</label>
          <input 
            type="text" 
            class="form-control" 
            id="username" 
            formControlName="username"
            [class.is-invalid]="submitted && f['username'].errors">
          <div *ngIf="submitted && f['username'].errors" class="invalid-feedback">
            <div *ngIf="f['username'].errors['required']">Bắt buộc</div>
            <div *ngIf="f['username'].errors['minlength']">Tối thiểu 3 ký tự</div>
          </div>
        </div>

        <div class="col-md-6 mb-3">
          <label for="display_name" class="form-label">Tên hiển thị *</label>
          <input 
            type="text" 
            class="form-control" 
            id="display_name" 
            formControlName="display_name"
            [class.is-invalid]="submitted && f['display_name'].errors">
          <div *ngIf="submitted && f['display_name'].errors" class="invalid-feedback">
            Bắt buộc
          </div>
        </div>
      </div>

      <div class="mb-3">
        <label for="email" class="form-label">Email *</label>
        <input 
          type="email" 
          class="form-control" 
          id="email" 
          formControlName="email"
          [class.is-invalid]="submitted && f['email'].errors">
        <div *ngIf="submitted && f['email'].errors" class="invalid-feedback">
          <div *ngIf="f['email'].errors['required']">Bắt buộc</div>
          <div *ngIf="f['email'].errors['email']">Email không hợp lệ</div>
        </div>
      </div>

      <div class="mb-3">
        <label for="password" class="form-label">Mật khẩu *</label>
        <input 
          type="password" 
          class="form-control" 
          id="password" 
          formControlName="password"
          [class.is-invalid]="submitted && f['password'].errors">
        <div *ngIf="submitted && f['password'].errors" class="invalid-feedback">
          <div *ngIf="f['password'].errors['required']">Bắt buộc</div>
          <div *ngIf="f['password'].errors['minlength']">Tối thiểu 6 ký tự</div>
        </div>
      </div>

      <div class="row">
        <div class="col-md-6 mb-3">
          <label for="phone_number" class="form-label">Số điện thoại</label>
          <input 
            type="text" 
            class="form-control" 
            id="phone_number" 
            formControlName="phone_number">
        </div>

        <div class="col-md-6 mb-3">
          <label for="level" class="form-label">Trình độ *</label>
          <select class="form-select" id="level" formControlName="level">
            <option value="C">C - Người mới</option>
            <option value="B">B - Trung bình</option>
            <option value="A">A - Nâng cao</option>
          </select>
        </div>
      </div>

      <button type="submit" class="btn btn-primary w-100 mb-3" [disabled]="loading">
        <span *ngIf="loading" class="spinner-border spinner-border-sm me-2"></span>
        Đăng ký
      </button>

      <div class="text-center">
        <p class="mb-0">Đã có tài khoản? <a routerLink="/login" class="text-decoration-none">Đăng nhập</a></p>
      </div>
    </form>
  </div>
</div>
'@

$dashboardHtml = @'
<div class="dashboard-container">
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="welcome-banner">
          <h1>Chào mừng, {{ currentUser?.display_name }}! 👋</h1>
          <p class="lead">Trình độ: <span class="badge bg-primary">{{ currentUser?.level }}</span></p>
        </div>
      </div>
    </div>

    <div class="row mt-4">
      <div class="col-md-4 mb-4">
        <div class="card dashboard-card">
          <div class="card-body text-center">
            <i class="bi bi-trophy-fill display-4 text-warning mb-3"></i>
            <h5 class="card-title">Bảng xếp hạng</h5>
            <p class="card-text">Xem thứ hạng và điểm số của bạn</p>
            <a routerLink="/rankings" class="btn btn-primary">Xem ngay</a>
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-4">
        <div class="card dashboard-card">
          <div class="card-body text-center">
            <i class="bi bi-clipboard-check-fill display-4 text-success mb-3"></i>
            <h5 class="card-title">Báo cáo trận đấu</h5>
            <p class="card-text">Ghi nhận kết quả trận đấu mới</p>
            <a routerLink="/matches/report" class="btn btn-success">Báo cáo</a>
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-4">
        <div class="card dashboard-card">
          <div class="card-body text-center">
            <i class="bi bi-list-check display-4 text-info mb-3"></i>
            <h5 class="card-title">Lịch sử trận đấu</h5>
            <p class="card-text">Xem các trận đấu đã chơi</p>
            <a routerLink="/matches/history" class="btn btn-info">Xem lịch sử</a>
          </div>
        </div>
      </div>
    </div>

    <div class="row" *ngIf="currentUser?.is_admin">
      <div class="col-12">
        <div class="alert alert-info">
          <h5><i class="bi bi-shield-check"></i> Quản trị viên</h5>
          <p class="mb-0">Bạn có quyền quản trị. <a routerLink="/admin" class="alert-link">Truy cập trang quản trị</a></p>
        </div>
      </div>
    </div>
  </div>
</div>
'@

$rankingsHtml = @'
<div class="rankings-container">
  <div class="container">
    <h2 class="mb-4">🏆 Bảng xếp hạng</h2>

    <div class="card mb-4">
      <div class="card-body">
        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label">Loại xếp hạng</label>
            <select class="form-select" [(ngModel)]="selectedType" (change)="onFilterChange()">
              <option *ngFor="let type of matchTypes" [value]="type.value">
                {{ type.label }}
              </option>
            </select>
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label">Trình độ</label>
            <select class="form-select" [(ngModel)]="selectedLevel" (change)="onFilterChange()">
              <option *ngFor="let level of levels" [value]="level">
                Level {{ level }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div *ngIf="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Đang tải...</span>
      </div>
    </div>

    <div *ngIf="error" class="alert alert-danger">{{ error }}</div>

    <!-- Overall Rankings -->
    <div *ngIf="!loading && selectedType === 'overall' && overallRankings.length > 0" class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Hạng</th>
                <th>Tên</th>
                <th>Tổng điểm</th>
                <th>Đơn</th>
                <th>Đôi nam</th>
                <th>Đôi nữ</th>
                <th>Đôi nam nữ</th>
                <th>Trận đấu</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let ranking of overallRankings" [class]="getMedalClass(ranking.rank)">
                <td>
                  <strong>#{{ ranking.rank }}</strong>
                  <span *ngIf="ranking.rank <= 3" class="ms-2">
                    {{ ranking.rank === 1 ? '🥇' : ranking.rank === 2 ? '🥈' : '🥉' }}
                  </span>
                </td>
                <td><strong>{{ ranking.display_name }}</strong></td>
                <td><span class="badge bg-primary">{{ ranking.total_points }}</span></td>
                <td>{{ ranking.singles_points }}</td>
                <td>{{ ranking.doubles_men_points }}</td>
                <td>{{ ranking.doubles_women_points }}</td>
                <td>{{ ranking.doubles_mixed_points }}</td>
                <td>{{ ranking.total_matches }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Type-specific Rankings -->
    <div *ngIf="!loading && selectedType !== 'overall' && typeRankings.length > 0" class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Hạng</th>
                <th>Tên</th>
                <th>Điểm</th>
                <th>Trận đấu</th>
                <th>Thắng</th>
                <th>Thua</th>
                <th>Tỷ lệ thắng</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let ranking of typeRankings" [class]="getMedalClass(ranking.rank)">
                <td>
                  <strong>#{{ ranking.rank }}</strong>
                  <span *ngIf="ranking.rank <= 3" class="ms-2">
                    {{ ranking.rank === 1 ? '🥇' : ranking.rank === 2 ? '🥈' : '🥉' }}
                  </span>
                </td>
                <td><strong>{{ ranking.display_name }}</strong></td>
                <td><span class="badge bg-primary">{{ ranking.points }}</span></td>
                <td>{{ ranking.total_matches }}</td>
                <td class="text-success">{{ ranking.wins }}</td>
                <td class="text-danger">{{ ranking.losses }}</td>
                <td>{{ (ranking.win_rate * 100).toFixed(1) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div *ngIf="!loading && ((selectedType === 'overall' && overallRankings.length === 0) || (selectedType !== 'overall' && typeRankings.length === 0))" 
         class="alert alert-info">
      Chưa có dữ liệu xếp hạng cho bộ lọc này.
    </div>
  </div>
</div>
'@

# Write HTML files
Set-Content -Path "src\app\components\login\login.component.html" -Value $loginHtml
Set-Content -Path "src\app\components\register\register.component.html" -Value $registerHtml
Set-Content -Path "src\app\components\dashboard\dashboard.component.html" -Value $dashboardHtml
Set-Content -Path "src\app\components\rankings\rankings.component.html" -Value $rankingsHtml

Write-Host "All HTML templates created successfully!" -ForegroundColor Green
