import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TournamentService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Get tournament rules
  getTournamentRules(): Observable<any> {
    return this.http.get(`${this.apiUrl}/tournament/rules`);
  }

  // Update tournament rules - super admin only
  updateTournamentRules(rules: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/tournament/rules`, { rules });
  }
}
