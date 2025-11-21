import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink, FormsModule, TranslatePipe],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  loading = false;
  submitted = false;
  error = '';
  returnUrl = '';
  showForgotPassword = false;
  forgotPasswordEmail = '';
  forgotPasswordSuccess = '';
  forgotPasswordError = '';
  forgotPasswordLoading = false;

  constructor(
    private formBuilder: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/dashboard']);
    }
  }

  ngOnInit(): void {
    this.loginForm = this.formBuilder.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });

    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/dashboard';
  }

  get f() { return this.loginForm.controls; }

  onSubmit(): void {
    this.submitted = true;
    this.error = '';

    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    this.authService.login(this.loginForm.value).subscribe({
      next: (response) => {
        // Check if user needs to change password
        if (response.require_password_change) {
          this.router.navigate(['/change-password'], { 
            queryParams: { required: 'true' } 
          });
        } else {
          this.router.navigate([this.returnUrl]);
        }
      },
      error: (error: any) => {
        this.error = error.error?.detail || 'Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.';
        this.loading = false;
      }
    });
  }

  closeForgotPassword(): void {
    this.showForgotPassword = false;
    this.forgotPasswordEmail = '';
    this.forgotPasswordSuccess = '';
    this.forgotPasswordError = '';
  }

  submitForgotPassword(): void {
    if (!this.forgotPasswordEmail) {
      return;
    }

    this.forgotPasswordLoading = true;
    this.forgotPasswordError = '';
    this.forgotPasswordSuccess = '';

    this.authService.forgotPassword(this.forgotPasswordEmail).subscribe({
      next: (response) => {
        this.forgotPasswordSuccess = response.message || 'Yêu cầu đã được gửi đến quản trị viên';
        this.forgotPasswordLoading = false;
        setTimeout(() => {
          this.closeForgotPassword();
        }, 3000);
      },
      error: (error: any) => {
        this.forgotPasswordError = error.error?.detail || 'Có lỗi xảy ra. Vui lòng thử lại.';
        this.forgotPasswordLoading = false;
      }
    });
  }
}
