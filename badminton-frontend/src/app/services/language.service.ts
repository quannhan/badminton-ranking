import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type Language = 'vi' | 'en';

@Injectable({
  providedIn: 'root'
})
export class LanguageService {
  private currentLanguageSubject = new BehaviorSubject<Language>('vi');
  public currentLanguage$ = this.currentLanguageSubject.asObservable();

  constructor() {
    // Load saved language from localStorage
    const savedLang = localStorage.getItem('app_language') as Language;
    if (savedLang && (savedLang === 'vi' || savedLang === 'en')) {
      this.currentLanguageSubject.next(savedLang);
    }
  }

  getCurrentLanguage(): Language {
    return this.currentLanguageSubject.value;
  }

  setLanguage(lang: Language): void {
    this.currentLanguageSubject.next(lang);
    localStorage.setItem('app_language', lang);
  }

  toggleLanguage(): void {
    const newLang = this.currentLanguageSubject.value === 'vi' ? 'en' : 'vi';
    this.setLanguage(newLang);
  }
}
