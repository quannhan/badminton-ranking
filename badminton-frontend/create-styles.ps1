# Create SCSS files for components

$loginScss = @'
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  padding: 40px;
  width: 100%;
  max-width: 450px;
}

h2 {
  color: #667eea;
  font-weight: bold;
}
'@

$registerScss = @'
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  padding: 40px;
  width: 100%;
  max-width: 600px;
}

h2 {
  color: #667eea;
  font-weight: bold;
}
'@

$dashboardScss = @'
.dashboard-container {
  padding: 30px 0;
  min-height: calc(100vh - 56px);
  background-color: #f8f9fa;
}

.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.dashboard-card {
  border: none;
  border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
  }
}
'@

$rankingsScss = @'
.rankings-container {
  padding: 30px 0;
  min-height: calc(100vh - 56px);
  background-color: #f8f9fa;
}

.gold {
  background-color: #fff9e6;
}

.silver {
  background-color: #f5f5f5;
}

.bronze {
  background-color: #fff5e6;
}

.table {
  thead {
    background-color: #667eea;
    color: white;
  }
}
'@

# Write SCSS files
Set-Content -Path "src\app\components\login\login.component.scss" -Value $loginScss
Set-Content -Path "src\app\components\register\register.component.scss" -Value $registerScss
Set-Content -Path "src\app\components\dashboard\dashboard.component.scss" -Value $dashboardScss
Set-Content -Path "src\app\components\rankings\rankings.component.scss" -Value $rankingsScss

Write-Host "All SCSS files created successfully!" -ForegroundColor Green
