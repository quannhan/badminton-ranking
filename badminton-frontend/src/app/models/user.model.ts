export interface User {
  user_id: number;
  username?: string;
  email: string;
  display_name: string;
  gender?: 'M' | 'F';
  avatar?: string;
  phone_number?: string;
  level: 'A' | 'B' | 'C' | 'D';
  total_points: number;
  singles_points: number;
  doubles_points: number;
  is_admin: boolean;
  is_active: boolean;
  require_password_change?: boolean;
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
  level: 'A' | 'B' | 'C' | 'D';
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  require_password_change?: boolean;
  user: User;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetResponse {
  request_id: number;
  user_id: number;
  email: string;
  display_name: string;
  status: string;
  created_at: string;
}

export interface UpdateProfileRequest {
  display_name?: string;
  email?: string;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}
