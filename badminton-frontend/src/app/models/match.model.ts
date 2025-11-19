export interface MatchPlayer {
  user_id: number;
  display_name: string;
  team: number;
  result: 'WIN' | 'LOSE' | 'PENDING';
  points_earned: number;
}

export interface Match {
  match_id: number;
  reporter_id: number;
  reporter_name?: string;
  match_type: 'SINGLES' | 'DOUBLES_MEN' | 'DOUBLES_WOMEN' | 'DOUBLES_MIXED';
  stake_value: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  admin_notes?: string;
  notes?: string;
  match_video_url?: string;
  created_at: string;
  approved_at?: string;
  players: MatchPlayer[];
}

export interface CreateMatchRequest {
  match_type: 'SINGLES' | 'DOUBLES_MEN' | 'DOUBLES_WOMEN' | 'DOUBLES_MIXED';
  stake_value: number;
  team1_player_ids: number[];
  team2_player_ids: number[];
  winning_team?: number; // 1 or 2, optional for admin pre-approval
  notes?: string;
  match_video_url?: string;
}

export interface ReportMatchRequest {
  match_type: 'SINGLES' | 'DOUBLES_MEN' | 'DOUBLES_WOMEN' | 'DOUBLES_MIXED';
  stake_value: number;
  team1_player_ids: number[];
  team2_player_ids: number[];
  winning_team: number; // 1 or 2
  notes?: string;
  match_video_url?: string;
}

