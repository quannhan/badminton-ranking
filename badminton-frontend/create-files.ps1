# Script để tạo tất cả các file cần thiết cho Angular project

# Create models
$userModel = @'
export interface User {
  user_id: number;
  username: string;
  email: string;
  display_name: string;
  phone_number?: string;
  level: 'A' | 'B' | 'C';
  is_admin: boolean;
  profile_picture?: string;
  last_played_date?: string;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  display_name: string;
  phone_number?: string;
  level: 'A' | 'B' | 'C';
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}
'@

$matchModel = @'
export interface Match {
  match_id: number;
  match_type: 'SINGLES' | 'DOUBLES_MEN' | 'DOUBLES_WOMEN' | 'DOUBLES_MIXED';
  level: 'A' | 'B' | 'C';
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  match_date: string;
  team1_player1_id: number;
  team1_player2_id?: number;
  team2_player1_id: number;
  team2_player2_id?: number;
  team1_score: number;
  team2_score: number;
  winner_team: 1 | 2;
  reported_by: number;
  approved_by?: number;
  approved_at?: string;
  created_at: string;
}

export interface ReportMatchRequest {
  match_type: string;
  level: string;
  team1_player1_id: number;
  team1_player2_id?: number;
  team2_player1_id: number;
  team2_player2_id?: number;
  team1_score: number;
  team2_score: number;
  winner_team: number;
  match_date: string;
}
'@

$rankingModel = @'
export interface Ranking {
  rank: number;
  user_id: number;
  display_name: string;
  level: string;
  total_matches: number;
  wins: number;
  losses: number;
  points: number;
  win_rate: number;
}

export interface OverallRanking {
  rank: number;
  user_id: number;
  display_name: string;
  level: string;
  total_points: number;
  singles_points: number;
  doubles_men_points: number;
  doubles_women_points: number;
  doubles_mixed_points: number;
  total_matches: number;
}
'@

# Create Services
$authService = @'
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { User, LoginRequest, RegisterRequest, LoginResponse } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject: BehaviorSubject<User | null>;
  public currentUser: Observable<User | null>;

  constructor(private http: HttpClient) {
    const storedUser = localStorage.getItem('currentUser');
    this.currentUserSubject = new BehaviorSubject<User | null>(
      storedUser ? JSON.parse(storedUser) : null
    );
    this.currentUser = this.currentUserSubject.asObservable();
  }

  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return this.http.post<LoginResponse>(`${this.apiUrl}/users/login`, formData).pipe(
      tap((response: LoginResponse) => {
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('currentUser', JSON.stringify(response.user));
        this.currentUserSubject.next(response.user);
      })
    );
  }

  register(userData: RegisterRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/users/register`, userData);
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  isAdmin(): boolean {
    return this.currentUserValue?.is_admin || false;
  }

  getProfile(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/users/me`);
  }

  getUserProfile(userId: number): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/users/profile/${userId}`);
  }
}
'@

$matchService = @'
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Match, ReportMatchRequest } from '../models/match.model';

@Injectable({
  providedIn: 'root'
})
export class MatchService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  reportMatch(matchData: ReportMatchRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/matches/report`, matchData);
  }

  getMyMatches(): Observable<Match[]> {
    return this.http.get<Match[]>(`${this.apiUrl}/matches/my-matches`);
  }

  getPendingMatches(): Observable<Match[]> {
    return this.http.get<Match[]>(`${this.apiUrl}/admin/pending-matches`);
  }

  approveMatch(matchId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/approve-match/${matchId}`, {});
  }

  rejectMatch(matchId: number, reason?: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/reject-match/${matchId}`, { reason });
  }
}
'@

$rankingService = @'
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Ranking, OverallRanking } from '../models/ranking.model';

@Injectable({
  providedIn: 'root'
})
export class RankingService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getOverallRankings(level: string): Observable<OverallRanking[]> {
    return this.http.get<OverallRanking[]>(`${this.apiUrl}/rankings/overall/${level}`);
  }

  getRankingsByType(matchType: string, level: string): Observable<Ranking[]> {
    return this.http.get<Ranking[]>(`${this.apiUrl}/rankings/${matchType}/${level}`);
  }

  resetMonthlyRankings(): Observable<any> {
    return this.http.post(`${this.apiUrl}/rankings/reset-monthly`, {});
  }
}
'@

# Write files
New-Item -Path "src\app\models" -ItemType Directory -Force | Out-Null
New-Item -Path "src\app\services" -ItemType Directory -Force | Out-Null

Set-Content -Path "src\app\models\user.model.ts" -Value $userModel
Set-Content -Path "src\app\models\match.model.ts" -Value $matchModel
Set-Content -Path "src\app\models\ranking.model.ts" -Value $rankingModel

Set-Content -Path "src\app\services\auth.service.ts" -Value $authService
Set-Content -Path "src\app\services\match.service.ts" -Value $matchService
Set-Content -Path "src\app\services\ranking.service.ts" -Value $rankingService

Write-Host "All models and services created successfully!" -ForegroundColor Green
