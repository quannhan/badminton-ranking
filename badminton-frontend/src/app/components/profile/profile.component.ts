import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { User } from '../../models/user.model';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {
  currentUser: User | null = null;
  selectedFile: File | null = null;
  uploading = false;
  uploadMessage = '';

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.authService.currentUser.subscribe(user => {
      this.currentUser = user;
    });
  }

  getAvatarUrl(): string {
    console.log('Profile - currentUser.avatar:', this.currentUser?.avatar?.substring(0, 50));
    console.log('Profile - currentUser.gender:', this.currentUser?.gender);
    if (this.currentUser?.avatar) {
      return this.currentUser.avatar;
    }
    return this.currentUser?.gender === 'F' 
      ? '/assets/avatars/avatar_female.jpg' 
      : '/assets/avatars/avatar_male.png';
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        this.uploadMessage = 'Vui lòng chọn file ảnh';
        return;
      }
      // Validate file size (5MB)
      if (file.size > 5 * 1024 * 1024) {
        this.uploadMessage = 'Kích thước file phải nhỏ hơn 5MB';
        return;
      }
      this.selectedFile = file;
      this.uploadMessage = '';
    }
  }

  uploadAvatar(): void {
    if (!this.selectedFile) return;

    this.uploading = true;
    this.authService.uploadAvatar(this.selectedFile).subscribe({
      next: (response) => {
        this.uploadMessage = 'Upload avatar thành công!';
        this.selectedFile = null;
        this.uploading = false;
      },
      error: (error) => {
        this.uploadMessage = 'Lỗi upload: ' + (error.error?.detail || 'Unknown error');
        this.uploading = false;
      }
    });
  }

  deleteAvatar(): void {
    if (!confirm('Bạn có chắc muốn xóa avatar?')) return;

    this.authService.deleteAvatar().subscribe({
      next: () => {
        this.uploadMessage = 'Đã xóa avatar';
      },
      error: (error) => {
        this.uploadMessage = 'Lỗi xóa avatar: ' + (error.error?.detail || 'Unknown error');
      }
    });
  }

  getLevelBadgeClass(level: string): string {
    const badges: { [key: string]: string } = {
      'A': 'bg-danger',
      'B': 'bg-warning',
      'C': 'bg-success'
    };
    return badges[level] || 'bg-secondary';
  }
}
