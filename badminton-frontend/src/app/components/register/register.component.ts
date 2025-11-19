import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
  loading = false;
  submitted = false;
  error = '';
  success = false;

  constructor(
    private formBuilder: FormBuilder,
    private router: Router,
    private authService: AuthService
  ) {
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/dashboard']);
    }
  }

  ngOnInit(): void {
    this.registerForm = this.formBuilder.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      display_name: ['', Validators.required],
      phone_number: [''],
      level: ['C', Validators.required]
    });
  }

  get f() { return this.registerForm.controls; }

  onSubmit(): void {
    this.submitted = true;
    this.error = '';

    if (this.registerForm.invalid) {
      return;
    }

    this.loading = true;
    this.authService.register(this.registerForm.value).subscribe({
      next: () => {
        this.success = true;
        // Don't auto-redirect, show success message
      },
      error: (error: any) => {
        this.error = error.error?.detail || 'Đăng ký thất bại. Vui lòng thử lại.';
        this.loading = false;
      }
    });
  }
}
