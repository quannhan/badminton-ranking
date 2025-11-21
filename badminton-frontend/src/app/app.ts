import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, RouterLink } from '@angular/router';
import { AuthService } from './services/auth.service';
import { LanguageService, Language } from './services/language.service';
import { User } from './models/user.model';
import { TranslatePipe } from './pipes/translate.pipe';

@Component({
  selector: 'app-root',
  imports: [CommonModule, RouterOutlet, RouterLink, TranslatePipe],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  title = 'Metfone Badminton Ranking';
  currentUser: User | null = null;
  currentLanguage: Language = 'vi';

  constructor(
    public authService: AuthService,
    public languageService: LanguageService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.authService.currentUser.subscribe((user: User | null) => {
      this.currentUser = user;
    });
    
    this.languageService.currentLanguage$.subscribe(lang => {
      this.currentLanguage = lang;
    });
  }

  setLanguage(lang: Language): void {
    this.languageService.setLanguage(lang);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  getAvatarUrl(): string {
    console.log('Navbar - currentUser.avatar:', this.currentUser?.avatar?.substring(0, 50));
    console.log('Navbar - currentUser.gender:', this.currentUser?.gender);
    if (this.currentUser?.avatar) {
      return this.currentUser.avatar;
    }
    return this.currentUser?.gender === 'F' 
      ? '/assets/avatars/avatar_female.jpg' 
      : '/assets/avatars/avatar_male.png';
  }
}
 