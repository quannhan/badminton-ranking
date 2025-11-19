import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-scoring-rules',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './scoring-rules.component.html',
  styleUrls: ['./scoring-rules.component.scss']
})
export class ScoringRulesComponent {
  examples = [
    {
      stakeValue: 5,
      winnerPoints: 50,
      loserPoints: 25,
      description: 'Trận đấu với điểm cược 5 (mức thấp)'
    },
    {
      stakeValue: 10,
      winnerPoints: 100,
      loserPoints: 50,
      description: 'Trận đấu với điểm cược 10 (mức cao)'
    }
  ];
}
