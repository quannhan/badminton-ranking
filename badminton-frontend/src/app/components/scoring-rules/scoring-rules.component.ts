import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
  selector: 'app-scoring-rules',
  standalone: true,
  imports: [CommonModule, TranslatePipe],
  templateUrl: './scoring-rules.component.html',
  styleUrls: ['./scoring-rules.component.scss']
})
export class ScoringRulesComponent {
  examples = [
    {
      stakeValue: 2,
      winnerPoints: 20,
      loserPoints: 10,
      descriptionKey: 'scoring.example_low'
    },
    {
      stakeValue: 5,
      winnerPoints: 50,
      loserPoints: 25,
      descriptionKey: 'scoring.example_medium'
    },
    {
      stakeValue: 10,
      winnerPoints: 100,
      loserPoints: 50,
      descriptionKey: 'scoring.example_high'
    }
  ];
}
