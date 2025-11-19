import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Match, ReportMatchRequest, CreateMatchRequest } from '../models/match.model';

@Injectable({
  providedIn: 'root'
})
export class MatchService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // User endpoints
  reportMatch(matchData: ReportMatchRequest): Observable<Match> {
    return this.http.post<Match>(`${this.apiUrl}/matches/report`, matchData);
  }

  getMyMatches(): Observable<Match[]> {
    return this.http.get<Match[]>(`${this.apiUrl}/matches/my-matches`);
  }

  getAllMatches(): Observable<Match[]> {
    return this.http.get<Match[]>(`${this.apiUrl}/matches/all`);
  }

  getCompletedMatchesThisMonth(): Observable<Match[]> {
    return this.http.get<Match[]>(`${this.apiUrl}/matches/completed-this-month`);
  }

  getPendingMatchesThisMonth(): Observable<Match[]> {
    return this.http.get<Match[]>(`${this.apiUrl}/matches/pending-this-month`);
  }

  // Admin endpoints
  createMatch(matchData: CreateMatchRequest): Observable<Match> {
    return this.http.post<Match>(`${this.apiUrl}/admin/create-match`, matchData);
  }

  getPendingMatches(): Observable<Match[]> {
    return this.http.get<Match[]>(`${this.apiUrl}/admin/pending-matches`);
  }

  approveMatch(matchId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/approve-match/${matchId}`, {});
  }

  rejectMatch(matchId: number, adminNotes: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/reject-match/${matchId}?admin_notes=${encodeURIComponent(adminNotes)}`, {});
  }

  updateMatchResult(matchId: number, winningTeam: number, videoUrl?: string): Observable<any> {
    let url = `${this.apiUrl}/admin/update-match-result/${matchId}?winning_team=${winningTeam}`;
    if (videoUrl) {
      url += `&match_video_url=${encodeURIComponent(videoUrl)}`;
    }
    return this.http.post(url, {});
  }

  reportMatchResult(matchId: number, winningTeam: number, videoUrl?: string): Observable<any> {
    let url = `${this.apiUrl}/admin/report-match-result/${matchId}?winning_team=${winningTeam}`;
    if (videoUrl) {
      url += `&match_video_url=${encodeURIComponent(videoUrl)}`;
    }
    return this.http.post(url, {});
  }

  resetAllPoints(password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/reset-all-points`, { password });
  }

  // Password reset admin endpoints
  getPasswordResetRequests(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/admin/password-reset-requests`);
  }

  approvePasswordReset(requestId: number, newPassword: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/approve-password-reset/${requestId}?new_password=${encodeURIComponent(newPassword)}`, {});
  }

  rejectPasswordReset(requestId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/reject-password-reset/${requestId}`, {});
  }
}
