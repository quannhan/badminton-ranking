import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormArray, FormsModule } from '@angular/forms';
import { MatchService } from '../../services/match.service';
import { AuthService } from '../../services/auth.service';
import { Match, CreateMatchRequest } from '../../models/match.model';
import { User } from '../../models/user.model';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss']
})
export class AdminComponent implements OnInit {
  createMatchForm!: FormGroup;
  pendingMatches: Match[] = [];
  pendingUsers: User[] = [];
  allUsers: User[] = [];
  passwordResetRequests: any[] = [];
  loading = false;
  error = '';
  success = '';
  showResetPointsModal = false;
  resetPassword = '';
  currentUser: User | null = null;
  showPasswordResetModal = false;
  selectedResetRequest: any = null;
  newTempPassword = '';

  matchTypes = [
    { value: 'SINGLES', label: 'Đơn' },
    { value: 'DOUBLES_MEN', label: 'Đôi Nam' },
    { value: 'DOUBLES_WOMEN', label: 'Đôi Nữ' },
    { value: 'DOUBLES_MIXED', label: 'Đôi Nam Nữ' }
  ];

  stakeValues = [
    { value: 2, label: '2 (Kèo nước)' },
    { value: 5, label: '5' },
    { value: 10, label: '10' }
  ];

  constructor(
    private fb: FormBuilder,
    private matchService: MatchService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.initForm();
    this.loadPendingMatches();
    this.loadPendingUsers();
    this.loadAllUsers();
    this.loadCurrentUser();
    if (this.isSuperAdmin()) {
      this.loadPasswordResetRequests();
    }
  }

  loadCurrentUser(): void {
    this.currentUser = this.authService.currentUserValue;
  }

  isSuperAdmin(): boolean {
    return this.currentUser?.email === 'thaiquan251198@gmail.com';
  }

  openResetPointsModal(): void {
    this.showResetPointsModal = true;
    this.resetPassword = '';
    this.error = '';
  }

  closeResetPointsModal(): void {
    this.showResetPointsModal = false;
    this.resetPassword = '';
  }

  confirmResetPoints(): void {
    if (!this.resetPassword) {
      this.error = 'Vui lòng nhập mật khẩu';
      return;
    }

    this.loading = true;
    this.matchService.resetAllPoints(this.resetPassword).subscribe({
      next: (response: any) => {
        this.success = `Đã reset điểm thành công cho ${response.users_affected} thành viên`;
        this.closeResetPointsModal();
        this.loading = false;
        setTimeout(() => this.success = '', 5000);
      },
      error: (err: any) => {
        this.error = err.error?.detail || 'Có lỗi xảy ra khi reset điểm';
        this.loading = false;
      }
    });
  }

  initForm(): void {
    this.createMatchForm = this.fb.group({
      match_type: ['SINGLES', Validators.required],
      stake_value: [5, Validators.required],
      team1_player_ids: this.fb.array([this.fb.control(null, Validators.required)]),
      team2_player_ids: this.fb.array([this.fb.control(null, Validators.required)]),
      winning_team: [null], // Optional, if set then auto-approve
      notes: [''], // Optional notes
      match_video_url: [''] // Optional YouTube link
    });

    // Watch match type changes to adjust player arrays
    this.createMatchForm.get('match_type')?.valueChanges.subscribe(type => {
      this.adjustPlayerArrays(type);
    });
  }

  get team1Players(): FormArray {
    return this.createMatchForm.get('team1_player_ids') as FormArray;
  }

  get team2Players(): FormArray {
    return this.createMatchForm.get('team2_player_ids') as FormArray;
  }

  adjustPlayerArrays(matchType: string): void {
    const requiredPlayers = matchType === 'SINGLES' ? 1 : 2;
    
    // Adjust team 1
    while (this.team1Players.length < requiredPlayers) {
      this.team1Players.push(this.fb.control(null, Validators.required));
    }
    while (this.team1Players.length > requiredPlayers) {
      this.team1Players.removeAt(this.team1Players.length - 1);
    }

    // Adjust team 2
    while (this.team2Players.length < requiredPlayers) {
      this.team2Players.push(this.fb.control(null, Validators.required));
    }
    while (this.team2Players.length > requiredPlayers) {
      this.team2Players.removeAt(this.team2Players.length - 1);
    }
  }

  loadPendingMatches(): void {
    this.matchService.getPendingMatches().subscribe({
      next: (matches) => {
        this.pendingMatches = matches;
      },
      error: (err) => {
        console.error('Error loading pending matches:', err);
      }
    });
  }

  loadAllUsers(): void {
    this.authService.getAllUsers().subscribe({
      next: (users) => {
        this.allUsers = users;
      },
      error: (err) => {
        console.error('Error loading users:', err);
      }
    });
  }

  loadPendingUsers(): void {
    this.authService.getPendingUsers().subscribe({
      next: (users) => {
        this.pendingUsers = users;
      },
      error: (err) => {
        console.error('Error loading pending users:', err);
      }
    });
  }

  onSubmit(): void {
    if (this.createMatchForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = '';
    this.success = '';

    const formValue = this.createMatchForm.value;
    const matchData: CreateMatchRequest = {
      match_type: formValue.match_type,
      stake_value: formValue.stake_value,
      team1_player_ids: formValue.team1_player_ids.filter((id: any) => id !== null),
      team2_player_ids: formValue.team2_player_ids.filter((id: any) => id !== null),
      winning_team: formValue.winning_team || null,
      notes: formValue.notes || null,
      match_video_url: formValue.match_video_url || null
    };

    console.log('Creating match with data:', matchData);

    this.matchService.createMatch(matchData).subscribe({
      next: (match) => {
        this.success = 'Tạo kèo thành công!';
        this.createMatchForm.reset({
          match_type: 'SINGLES',
          stake_value: 5,
          winning_team: null
        });
        this.initForm();
        this.loadPendingMatches();
        this.loading = false;
        
        setTimeout(() => this.success = '', 3000);
      },
      error: (err) => {
        console.error('Error creating match:', err);
        this.error = err.error?.detail || 'Có lỗi xảy ra khi tạo kèo';
        this.loading = false;
      }
    });
  }

  approveMatch(matchId: number): void {
    if (!confirm('Xác nhận duyệt trận đấu này?')) {
      return;
    }

    this.matchService.approveMatch(matchId).subscribe({
      next: () => {
        this.success = 'Đã duyệt trận đấu!';
        this.loadPendingMatches();
        setTimeout(() => this.success = '', 3000);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Có lỗi xảy ra';
      }
    });
  }

  rejectMatch(matchId: number): void {
    const reason = prompt('Nhập lý do từ chối:');
    if (!reason) {
      return;
    }

    this.matchService.rejectMatch(matchId, reason).subscribe({
      next: () => {
        this.success = 'Đã từ chối trận đấu!';
        this.loadPendingMatches();
        setTimeout(() => this.success = '', 3000);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Có lỗi xảy ra';
      }
    });
  }

  getPlayerName(userId: number): string {
    const user = this.allUsers.find(u => u.user_id === userId);
    return user ? user.display_name : 'Unknown';
  }

  getTeamPlayers(match: Match, team: number): string {
    const players = match.players.filter(p => p.team === team);
    return players.map(p => p.display_name).join(', ');
  }

  getTeamResult(match: Match, team: number): string {
    const players = match.players.filter(p => p.team === team);
    if (players.length === 0) return '';
    return players[0].result;
  }

  getMatchTypeLabel(type: string): string {
    const mt = this.matchTypes.find(t => t.value === type);
    return mt ? mt.label : type;
  }

  approveUser(userId: number): void {
    if (!confirm('Xác nhận kích hoạt tài khoản này?')) {
      return;
    }

    this.authService.approveUser(userId).subscribe({
      next: () => {
        this.success = 'Đã kích hoạt tài khoản!';
        this.loadPendingUsers();
        this.loadAllUsers();
        setTimeout(() => this.success = '', 3000);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Có lỗi xảy ra';
      }
    });
  }

  rejectUser(userId: number): void {
    if (!confirm('Xác nhận từ chối và xóa tài khoản này?')) {
      return;
    }

    this.authService.rejectUser(userId).subscribe({
      next: () => {
        this.success = 'Đã từ chối tài khoản!';
        this.loadPendingUsers();
        setTimeout(() => this.success = '', 3000);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Có lỗi xảy ra';
      }
    });
  }

  loadPasswordResetRequests(): void {
    this.matchService.getPasswordResetRequests().subscribe({
      next: (requests) => {
        this.passwordResetRequests = requests;
      },
      error: (err: any) => {
        console.error('Error loading password reset requests:', err);
      }
    });
  }

  openPasswordResetModal(request: any): void {
    this.selectedResetRequest = request;
    this.newTempPassword = this.generateTempPassword();
    this.showPasswordResetModal = true;
    this.error = '';
  }

  closePasswordResetModal(): void {
    this.showPasswordResetModal = false;
    this.selectedResetRequest = null;
    this.newTempPassword = '';
  }

  generateTempPassword(): string {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789';
    let password = '';
    for (let i = 0; i < 8; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
  }

  approvePasswordReset(): void {
    if (!this.selectedResetRequest || !this.newTempPassword) {
      return;
    }

    this.loading = true;
    this.matchService.approvePasswordReset(this.selectedResetRequest.request_id, this.newTempPassword).subscribe({
      next: (response: any) => {
        this.success = `Đã cấp mật khẩu mới cho ${this.selectedResetRequest.display_name}: ${this.newTempPassword}`;
        this.closePasswordResetModal();
        this.loadPasswordResetRequests();
        this.loading = false;
        setTimeout(() => this.success = '', 10000);
      },
      error: (err: any) => {
        this.error = err.error?.detail || 'Có lỗi xảy ra khi cấp mật khẩu';
        this.loading = false;
      }
    });
  }

  rejectPasswordReset(requestId: number): void {
    if (!confirm('Xác nhận từ chối yêu cầu reset mật khẩu này?')) {
      return;
    }

    this.matchService.rejectPasswordReset(requestId).subscribe({
      next: () => {
        this.success = 'Đã từ chối yêu cầu reset mật khẩu';
        this.loadPasswordResetRequests();
        setTimeout(() => this.success = '', 3000);
      },
      error: (err: any) => {
        this.error = err.error?.detail || 'Có lỗi xảy ra';
      }
    });
  }
}
