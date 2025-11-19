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
