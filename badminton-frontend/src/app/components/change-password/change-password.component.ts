import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.scss']
})
export class ChangePasswordComponent implements OnInit {
  changePasswordForm!: FormGroup;
  loading = false;
  error = '';
  success = '';
  isRequired = false;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private route: ActivatedRoute,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.isRequired = this.route.snapshot.queryParams['required'] === 'true';
    
    this.changePasswordForm = this.fb.group({
      oldPassword: ['', Validators.required],
      newPassword: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required]
    }, { validator: this.passwordMatchValidator });
  }

  passwordMatchValidator(form: FormGroup) {
    const newPassword = form.get('newPassword');
    const confirmPassword = form.get('confirmPassword');
    
    if (newPassword && confirmPassword && newPassword.value !== confirmPassword.value) {
      confirmPassword.setErrors({ passwordMismatch: true });
    } else {
      return null;
    }
    return null;
  }

  get f() { return this.changePasswordForm.controls; }

  onSubmit(): void {
    this.error = '';
    this.success = '';

    if (this.changePasswordForm.invalid) {
      return;
    }

    const { oldPassword, newPassword } = this.changePasswordForm.value;

    this.loading = true;
    this.authService.changePassword(oldPassword, newPassword).subscribe({
      next: (response) => {
        this.success = response.message || 'Đổi mật khẩu thành công';
        setTimeout(() => {
          this.router.navigate(['/dashboard']);
        }, 2000);
      },
      error: (error: any) => {
        this.error = error.error?.detail || 'Có lỗi xảy ra khi đổi mật khẩu';
        this.loading = false;
      }
    });
  }

  cancel(): void {
    if (!this.isRequired) {
      this.router.navigate(['/dashboard']);
    }
  }
}
