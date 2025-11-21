import { Pipe, PipeTransform } from '@angular/core';
import { LanguageService } from '../services/language.service';
import { translate } from '../translations/translations';

@Pipe({
  name: 'translate',
  standalone: true,
  pure: false
})
export class TranslatePipe implements PipeTransform {
  constructor(private languageService: LanguageService) {}

  transform(key: string): string {
    const lang = this.languageService.getCurrentLanguage();
    return translate(key, lang);
  }
}
