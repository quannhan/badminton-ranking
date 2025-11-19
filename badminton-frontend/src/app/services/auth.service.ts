import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, switchMap, map, catchError, throwError } from 'rxjs';
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
    const token = localStorage.getItem('access_token');
    
    // Initialize with stored user (without avatar)
    this.currentUserSubject = new BehaviorSubject<User | null>(
      storedUser ? JSON.parse(storedUser) : null
    );
    this.currentUser = this.currentUserSubject.asObservable();
    
    // If user is logged in, fetch full user info including avatar
    if (storedUser && token) {
      this.getProfile().subscribe({
        next: (user) => {
          console.log('Fetched full user profile on init:', user);
        },
        error: (err) => {
          console.error('Failed to fetch user profile on init:', err);
          // If token is invalid, clear everything
          this.logout();
        }
      });
    }
  }

  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    // Backend expects JSON body with email and password
    const body = {
      email: credentials.username,  // Using username field as email
      password: credentials.password
    };

    console.log('Login request body:', body);

    return this.http.post<any>(`${this.apiUrl}/users/login`, body).pipe(
      tap((tokenResponse: any) => {
        console.log('Token response:', tokenResponse);
        localStorage.setItem('access_token', tokenResponse.access_token);
      }),
      catchError(error => {
        console.error('Login error:', error);
        return throwError(() => error);
      }),
      switchMap((tokenResponse: any) => {
        return this.http.get<User>(`${this.apiUrl}/users/me`).pipe(
          tap((user: User) => {
            console.log('User from /users/me:', user);
            // Don't store avatar in localStorage to avoid quota exceeded error
            // Store user info without avatar
            const userToStore = {
              user_id: user.user_id,
              email: user.email,
              display_name: user.display_name,
              gender: user.gender,
              level: user.level,
              total_points: user.total_points,
              singles_points: user.singles_points,
              doubles_points: user.doubles_points,
              is_admin: user.is_admin,
              last_played_date: user.last_played_date
            };
            localStorage.setItem('currentUser', JSON.stringify(userToStore));
            // Store full user with avatar in memory
            this.currentUserSubject.next(user);
          }),
          catchError(error => {
            console.error('Get user info error:', error);
            return throwError(() => error);
          }),
          map((user: User) => ({
            access_token: tokenResponse.access_token,
            token_type: tokenResponse.token_type,
            user: user
          }))
        );
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
    return this.http.get<User>(`${this.apiUrl}/users/me`).pipe(
      tap((user: User) => {
        // Update current user subject with full user info including avatar
        this.currentUserSubject.next(user);
      })
    );
  }

  getUserProfile(userId: number): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/users/profile/${userId}`);
  }

  getAllUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.apiUrl}/users/all`);
  }

  uploadAvatar(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/users/upload-avatar`, formData).pipe(
      tap((response) => {
        console.log('Upload response:', response);
        // Refresh current user after avatar upload
        this.getProfile().subscribe(user => {
          console.log('Updated user after upload:', user);
        });
      })
    );
  }

  deleteAvatar(): Observable<any> {
    return this.http.delete(`${this.apiUrl}/users/delete-avatar`).pipe(
      tap(() => {
        // Refresh current user after avatar deletion
        this.getProfile().subscribe(user => {
          console.log('Updated user after delete:', user);
        });
      })
    );
  }

  // Admin user management
  getPendingUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.apiUrl}/admin/pending-users`);
  }

  approveUser(userId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/approve-user/${userId}`, {});
  }

  rejectUser(userId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/reject-user/${userId}`, {});
  }

  // Password reset
  forgotPassword(email: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/users/forgot-password`, { email });
  }

  changePassword(oldPassword: string, newPassword: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/users/change-password`, {
      old_password: oldPassword,
      new_password: newPassword
    });
  }

  updateProfile(displayName?: string, email?: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/users/update-profile`, {
      display_name: displayName,
      email: email
    }).pipe(
      tap(() => {
        // Refresh current user after profile update
        this.getProfile().subscribe();
      })
    );
  }
}
