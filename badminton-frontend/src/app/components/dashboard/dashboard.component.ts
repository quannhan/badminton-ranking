import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { MatchService } from '../../services/match.service';
import { User } from '../../models/user.model';
import { Match } from '../../models/match.model';
import { ReportMatchModalComponent } from '../report-match-modal/report-match-modal.component';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, ReportMatchModalComponent, TranslatePipe],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  currentUser: User | null = null;
  allUsers: User[] = [];
  completedMatches: Match[] = []; // Kết quả trận đấu (APPROVED)
  pendingMatches: Match[] = []; // Kèo đấu tạo bởi admin
  loading = false;
  showReportMatchModal = false;
  showUpdateResultModal = false;
  showReportResultModal = false;
  showProfileModal = false;
  showUpdateVideoModal = false;
  selectedMatch: Match | null = null;
  selectedUser: User | null = null;
  updateWinningTeam: number | null = null;
  updateVideoUrl: string = '';
  reportWinningTeam: number | null = null;
  reportVideoUrl: string = '';
  editVideoUrl: string = '';
  matchHistory: any[] = [];
  matchHistoryStats = {
    singles: { wins: 0, losses: 0 },
    doubles: { wins: 0, losses: 0 }
  };
  loadingMatchHistory = false;

  constructor(
    private authService: AuthService,
    private matchService: MatchService
  ) {}

  ngOnInit(): void {
    this.authService.currentUser.subscribe(user => {
      this.currentUser = user;
    });
    this.loadAllUsers();
    this.loadCompletedMatches();
    this.loadPendingMatches();
    this.refreshCurrentUser();
  }

  refreshCurrentUser(): void {
    // Refresh current user to get latest points
    this.authService.getProfile().subscribe({
      next: (user) => {
        console.log('Refreshed current user:', user);
      },
      error: (err) => {
        console.error('Error refreshing user:', err);
      }
    });
  }

  loadAllUsers(): void {
    this.loading = true;
    this.authService.getAllUsers().subscribe({
      next: (users) => {
        // Sort by level (A > B > C) then by total_points descending
        this.allUsers = users.sort((a, b) => {
          const levelOrder: { [key: string]: number } = { 'A': 1, 'B': 2, 'C': 3 };
          const levelDiff = (levelOrder[a.level] || 99) - (levelOrder[b.level] || 99);
          if (levelDiff !== 0) return levelDiff;
          return b.total_points - a.total_points;
        });
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading users:', error);
        this.loading = false;
      }
    });
  }

  loadCompletedMatches(): void {
    this.matchService.getCompletedMatchesThisMonth().subscribe({
      next: (matches) => {
        this.completedMatches = matches;
        console.log('Completed matches loaded:', matches);
        this.refreshCurrentUser();
      },
      error: (error) => {
        console.error('Error loading completed matches:', error);
      }
    });
  }

  loadPendingMatches(): void {
    this.matchService.getPendingMatchesThisMonth().subscribe({
      next: (matches) => {
        this.pendingMatches = matches;
      },
      error: (error) => {
        console.error('Error loading pending matches:', error);
      }
    });
  }

  getAvatarUrl(user: User): string {
    if (user.avatar) {
      return user.avatar;
    }
    return user.gender === 'F' 
      ? '/assets/avatars/avatar_female.jpg' 
      : '/assets/avatars/avatar_male.png';
  }

  getLevelBadgeClass(level: string): string {
    const badges: { [key: string]: string } = {
      'A': 'bg-danger',
      'B': 'bg-warning',
      'C': 'bg-success'
    };
    return badges[level] || 'bg-secondary';
  }

  getStatusBadgeClass(status: string): string {
    const badges: { [key: string]: string } = {
      'PENDING': 'bg-warning',
      'APPROVED': 'bg-success',
      'REJECTED': 'bg-danger'
    };
    return badges[status] || 'bg-secondary';
  }

  getMatchTypeLabel(type: string): string {
    const labels: { [key: string]: string } = {
      'SINGLES': 'Đơn',
      'DOUBLES_MEN': 'Đôi Nam',
      'DOUBLES_WOMEN': 'Đôi Nữ',
      'DOUBLES_MIXED': 'Đôi Nam Nữ'
    };
    return labels[type] || type;
  }

  openReportMatchModal(): void {
    this.showReportMatchModal = true;
  }

  closeReportMatchModal(): void {
    this.showReportMatchModal = false;
  }

  getCurrentMonth(): string {
    const months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'];
    return months[new Date().getMonth()];
  }

  isMatchPending(match: Match): boolean {
    // Check if match has PENDING results (not yet played)
    return match.players.some(p => p.result === 'PENDING');
  }

  isUserInMatch(match: Match): boolean {
    if (!this.currentUser) return false;
    return match.players.some(p => p.user_id === this.currentUser?.user_id);
  }

  isUserInAnyMatch(): boolean {
    if (!this.currentUser) return false;
    return this.pendingMatches.some(match => this.isUserInMatch(match));
  }

  getTeamPlayers(match: Match, team: number): any[] {
    return match.players.filter(p => p.team === team);
  }

  getTeamResult(match: Match, team: number): string {
    const teamPlayers = match.players.filter(p => p.team === team);
    return teamPlayers.length > 0 ? teamPlayers[0].result : '';
  }

  openUpdateResultModal(match: Match): void {
    this.selectedMatch = match;
    this.updateWinningTeam = null;
    this.updateVideoUrl = '';
    this.showUpdateResultModal = true;
  }

  closeUpdateResultModal(): void {
    this.showUpdateResultModal = false;
    this.selectedMatch = null;
    this.updateWinningTeam = null;
    this.updateVideoUrl = '';
  }

  submitUpdateResult(): void {
    if (!this.selectedMatch || !this.updateWinningTeam) {
      return;
    }

    if (confirm(`Xác nhận Team ${this.updateWinningTeam} thắng?`)) {
      this.matchService.updateMatchResult(this.selectedMatch.match_id, this.updateWinningTeam, this.updateVideoUrl).subscribe({
        next: () => {
          alert('Đã cập nhật kết quả thành công!');
          this.closeUpdateResultModal();
          this.loadCompletedMatches();
          this.loadPendingMatches();
          this.refreshCurrentUser();
          this.loadAllUsers();
        },
        error: (error) => {
          console.error('Error updating result:', error);
          alert('Lỗi khi cập nhật kết quả: ' + (error.error?.detail || 'Unknown error'));
        }
      });
    }
  }

  openReportResultModal(match: Match): void {
    this.selectedMatch = match;
    this.reportWinningTeam = null;
    this.reportVideoUrl = '';
    this.showReportResultModal = true;
  }

  closeReportResultModal(): void {
    this.showReportResultModal = false;
    this.selectedMatch = null;
    this.reportWinningTeam = null;
    this.reportVideoUrl = '';
  }

  submitReportResult(): void {
    if (!this.selectedMatch || !this.reportWinningTeam) {
      return;
    }

    if (confirm(`Xác nhận báo cáo Team ${this.reportWinningTeam} thắng? Kết quả sẽ được gửi đến admin để duyệt.`)) {
      this.matchService.reportMatchResult(this.selectedMatch.match_id, this.reportWinningTeam, this.reportVideoUrl).subscribe({
        next: () => {
          alert('Đã báo cáo kết quả thành công! Đang chờ admin duyệt.');
          this.closeReportResultModal();
          this.loadCompletedMatches();
          this.loadPendingMatches();
        },
        error: (error) => {
          console.error('Error reporting result:', error);
          alert('Lỗi khi báo cáo kết quả: ' + (error.error?.detail || 'Unknown error'));
        }
      });
    }
  }

  viewUserProfile(user: User): void {
    this.selectedUser = user;
    this.showProfileModal = true;
    this.loadMatchHistory(user.user_id);
  }

  closeProfileModal(): void {
    this.showProfileModal = false;
    this.selectedUser = null;
    this.matchHistory = [];
    this.matchHistoryStats = {
      singles: { wins: 0, losses: 0 },
      doubles: { wins: 0, losses: 0 }
    };
  }

  loadMatchHistory(opponentId: number): void {
    if (!this.currentUser) return;

    this.loadingMatchHistory = true;
    this.matchService.getAllMatches().subscribe({
      next: (matches) => {
        // Filter matches where both currentUser and opponent participated AND were on different teams
        const relevantMatches = matches.filter(match => {
          if (match.status !== 'APPROVED') return false;
          
          const currentUserInMatch = match.players.find(p => p.user_id === this.currentUser?.user_id);
          const opponentInMatch = match.players.find(p => p.user_id === opponentId);
          
          // Both must be in the match
          if (!currentUserInMatch || !opponentInMatch) return false;
          
          // Must have results (not PENDING)
          if (currentUserInMatch.result === 'PENDING') return false;
          
          // Must be on DIFFERENT teams (opposing teams)
          return currentUserInMatch.team !== opponentInMatch.team;
        });

        // Calculate stats and prepare history
        this.matchHistory = relevantMatches.map(match => {
          const myPlayer = match.players.find(p => p.user_id === this.currentUser?.user_id)!;
          const opponentPlayer = match.players.find(p => p.user_id === opponentId)!;
          
          return {
            ...match,
            myResult: myPlayer.result,
            opponentResult: opponentPlayer.result,
            sameTeam: false // Always false now since we filtered
          };
        });

        // Calculate stats
        this.matchHistoryStats = {
          singles: { wins: 0, losses: 0 },
          doubles: { wins: 0, losses: 0 }
        };

        this.matchHistory.forEach(match => {
          const isSingles = match.match_type === 'SINGLES';
          const category = isSingles ? 'singles' : 'doubles';
          
          if (match.myResult === 'WIN') {
            this.matchHistoryStats[category].wins++;
          } else if (match.myResult === 'LOSE') {
            this.matchHistoryStats[category].losses++;
          }
        });

        this.loadingMatchHistory = false;
      },
      error: (error) => {
        console.error('Error loading match history:', error);
        this.loadingMatchHistory = false;
      }
    });
  }

  openUpdateVideoModal(match: Match): void {
    this.selectedMatch = match;
    this.editVideoUrl = match.match_video_url || '';
    this.showUpdateVideoModal = true;
  }

  closeUpdateVideoModal(): void {
    this.showUpdateVideoModal = false;
    this.selectedMatch = null;
    this.editVideoUrl = '';
  }

  submitUpdateVideo(): void {
    if (!this.selectedMatch) {
      return;
    }

    this.matchService.updateMatchVideo(this.selectedMatch.match_id, this.editVideoUrl).subscribe({
      next: () => {
        alert('Đã cập nhật link video thành công!');
        this.closeUpdateVideoModal();
        this.loadCompletedMatches();
      },
      error: (error) => {
        console.error('Error updating video:', error);
        alert('Lỗi khi cập nhật video: ' + (error.error?.detail || 'Unknown error'));
      }
    });
  }
}
