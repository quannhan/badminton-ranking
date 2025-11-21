import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RankingService } from '../../services/ranking.service';
import { OverallRanking, Ranking } from '../../models/ranking.model';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
  selector: 'app-rankings',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslatePipe],
  templateUrl: './rankings.component.html',
  styleUrls: ['./rankings.component.scss']
})
export class RankingsComponent implements OnInit {
  selectedLevel: string = 'ALL';
  selectedType: string = 'overall';
  overallRankings: OverallRanking[] = [];
  typeRankings: Ranking[] = [];
  loading = false;
  error = '';

  matchTypes = [
    { value: 'overall', labelKey: 'rankings.overall' },
    { value: 'SINGLES', labelKey: 'match.singles' },
    { value: 'DOUBLES_MEN', labelKey: 'match.doubles_men' },
    { value: 'DOUBLES_WOMEN', labelKey: 'match.doubles_women' },
    { value: 'DOUBLES_MIXED', labelKey: 'match.doubles_mixed' }
  ];

  levels = ['A', 'B', 'C'];

  constructor(private rankingService: RankingService) {}

  ngOnInit(): void {
    this.loadRankings();
  }

  loadRankings(): void {
    this.loading = true;
    this.error = '';

    if (this.selectedType === 'overall') {
      this.rankingService.getOverallRankings(this.selectedLevel).subscribe({
        next: (data: OverallRanking[]) => {
          this.overallRankings = data;
          this.loading = false;
        },
        error: (error: any) => {
          this.error = 'Không thể tải bảng xếp hạng';
          this.loading = false;
        }
      });
    } else {
      this.rankingService.getRankingsByType(this.selectedType, this.selectedLevel).subscribe({
        next: (data: Ranking[]) => {
          this.typeRankings = data;
          this.loading = false;
        },
        error: (error: any) => {
          this.error = 'Không thể tải bảng xếp hạng';
          this.loading = false;
        }
      });
    }
  }

  onFilterChange(): void {
    this.loadRankings();
  }

  getMedalClass(rank: number): string {
    if (rank === 1) return 'gold';
    if (rank === 2) return 'silver';
    if (rank === 3) return 'bronze';
    return '';
  }
}
