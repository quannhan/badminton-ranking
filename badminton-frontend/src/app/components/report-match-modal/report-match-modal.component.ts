import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormArray } from '@angular/forms';
import { MatchService } from '../../services/match.service';
import { AuthService } from '../../services/auth.service';
import { ReportMatchRequest } from '../../models/match.model';
import { User } from '../../models/user.model';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
  selector: 'app-report-match-modal',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, TranslatePipe],
  templateUrl: './report-match-modal.component.html',
  styleUrls: ['./report-match-modal.component.scss']
})
export class ReportMatchModalComponent implements OnInit {
  @Input() show = false;
  @Output() close = new EventEmitter<void>();
  @Output() matchReported = new EventEmitter<void>();

  reportForm!: FormGroup;
  allUsers: User[] = [];
  loading = false;
  error = '';

  matchTypes = [
    { value: 'SINGLES', labelKey: 'match.singles' },
    { value: 'DOUBLES_MEN', labelKey: 'match.doubles_men' },
    { value: 'DOUBLES_WOMEN', labelKey: 'match.doubles_women' },
    { value: 'DOUBLES_MIXED', labelKey: 'match.doubles_mixed' }
  ];

  stakeValues = [
    { value: 2, labelKey: 'stake.water_bet' },
    { value: 5, label: '5' },
    { value: 10, label: '10' }
  ];

  constructor(
    private fb: FormBuilder,
    private matchService: MatchService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.initForm();
    this.loadAllUsers();
  }

  initForm(): void {
    this.reportForm = this.fb.group({
      match_type: ['SINGLES', Validators.required],
      stake_value: [5, Validators.required],
      team1_player_ids: this.fb.array([this.fb.control(null, Validators.required)]),
      team2_player_ids: this.fb.array([this.fb.control(null, Validators.required)]),
      winning_team: [1, Validators.required],
      notes: [''],
      match_video_url: ['']
    });

    this.reportForm.get('match_type')?.valueChanges.subscribe(type => {
      this.adjustPlayerArrays(type);
    });
  }

  get team1Players(): FormArray {
    return this.reportForm.get('team1_player_ids') as FormArray;
  }

  get team2Players(): FormArray {
    return this.reportForm.get('team2_player_ids') as FormArray;
  }

  adjustPlayerArrays(matchType: string): void {
    const requiredPlayers = matchType === 'SINGLES' ? 1 : 2;
    
    while (this.team1Players.length < requiredPlayers) {
      this.team1Players.push(this.fb.control(null, Validators.required));
    }
    while (this.team1Players.length > requiredPlayers) {
      this.team1Players.removeAt(this.team1Players.length - 1);
    }

    while (this.team2Players.length < requiredPlayers) {
      this.team2Players.push(this.fb.control(null, Validators.required));
    }
    while (this.team2Players.length > requiredPlayers) {
      this.team2Players.removeAt(this.team2Players.length - 1);
    }
  }

  loadAllUsers(): void {
    this.authService.getAllUsers().subscribe({
      next: (users) => {
        this.allUsers = users;
      },
      error: (err) => {
        console.error('Error loading users:', err);
      }
    });
  }

  onSubmit(): void {
    if (this.reportForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = '';

    const formValue = this.reportForm.value;
    const matchData: ReportMatchRequest = {
      match_type: formValue.match_type,
      stake_value: formValue.stake_value,
      team1_player_ids: formValue.team1_player_ids.filter((id: any) => id !== null),
      team2_player_ids: formValue.team2_player_ids.filter((id: any) => id !== null),
      winning_team: formValue.winning_team
    };

    this.matchService.reportMatch(matchData).subscribe({
      next: () => {
        this.loading = false;
        this.matchReported.emit();
        this.closeModal();
      },
      error: (err) => {
        this.error = err.error?.detail || 'Có lỗi xảy ra khi báo cáo trận đấu';
        this.loading = false;
      }
    });
  }

  closeModal(): void {
    this.reportForm.reset({
      match_type: 'SINGLES',
      stake_value: 5,
      winning_team: null
    });
    this.initForm();
    this.error = '';
    this.close.emit();
  }
}
