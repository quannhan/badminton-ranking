import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { TournamentService } from '../../services/tournament.service';
import { User } from '../../models/user.model';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
  selector: 'app-tournament',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslatePipe],
  templateUrl: './tournament.component.html',
  styleUrls: ['./tournament.component.scss']
})
export class TournamentComponent implements OnInit {
  currentUser: User | null = null;
  tournamentRules: string = '';
  showRulesEditor = false;
  editRules: string = '';
  loading = false;

  constructor(
    private authService: AuthService,
    private tournamentService: TournamentService
  ) {}

  ngOnInit(): void {
    this.authService.currentUser.subscribe(user => {
      this.currentUser = user;
    });
    this.loadTournamentRules();
  }

  isSuperAdmin(): boolean {
    return this.currentUser?.email === 'thaiquan251198@gmail.com';
  }

  loadTournamentRules(): void {
    this.loading = true;
    this.tournamentService.getTournamentRules().subscribe({
      next: (data: { rules: string | null; updated_at: string | null }) => {
        this.tournamentRules = data.rules || '';
        this.loading = false;
      },
      error: (error: any) => {
        console.error('Error loading tournament rules:', error);
        this.loading = false;
      }
    });
  }

  openRulesEditor(): void {
    this.editRules = this.tournamentRules;
    this.showRulesEditor = true;
  }

  closeRulesEditor(): void {
    this.showRulesEditor = false;
    this.editRules = '';
  }

  saveRules(): void {
    if (!this.editRules.trim()) {
      alert('Vui lòng nhập nội dung thể lệ!');
      return;
    }

    this.loading = true;
    this.tournamentService.updateTournamentRules(this.editRules).subscribe({
      next: () => {
        alert('Đã cập nhật thể lệ giải đấu thành công!');
        this.tournamentRules = this.editRules;
        this.closeRulesEditor();
        this.loading = false;
      },
      error: (error: any) => {
        console.error('Error updating tournament rules:', error);
        alert('Lỗi: ' + (error.error?.detail || 'Unknown error'));
        this.loading = false;
      }
    });
  }
}
