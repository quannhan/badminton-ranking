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
