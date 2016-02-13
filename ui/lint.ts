import {bootstrap} from 'angular2/platform/browser';
import {Component} from 'angular2/core';
import 'rxjs/add/operator/map';
import {Http, HTTP_PROVIDERS, HTTP_BINDINGS} from 'angular2/http';
import { Injectable } from 'angular2/core';
import { CanReuse } from 'angular2/router';
import { LanguageService } from './utils.ts';

@Injectable()
export class LintService {
    constructor(private _http: Http,
                private _langService: LanguageService) { }

  getLintResults(language: string) {
      let langObs = this._langService.getCurrentLanguage();
      return langObs.mergeMap((language) =>
           this._http.get(`${language}/lint.json`)
               .map(res => res.json())
      )
  }
}

@Component({
  selector: 'lint-results',
  template:`
  <div class="row">
    <h1>Showing {{lintEntries?.length}} lint errors for {{lang}}</h1>
  </div>
  <div *ngFor="#lintEntry of lintEntries" class="row">
    <h3><a target="_blank" href="{{lintEntry.url}}">Lint error at {{lintEntry.date}}</a></h3>
    <h4>Lint message</h4>
    <pre class="lint-entry">{{lintEntry.text}}</pre>
    <h4>Original</h4>
    <pre class="lint-entry">{{lintEntry.msgid}}</pre>
    <h4>Translated</h4>
    <pre class="lint-entry">{{lintEntry.msgstr}}</pre>
    <h4>Context</h4>
    <pre class="lint-entry">{{lintEntry.comment}}</pre>
  </div>
  `,
  bindings: [LintService]
})
export class LintComponent implements CanReuse {
    lang: string

    routerCanReuse() { return true; }

    constructor(public lintService: LintService) {
        this.lang = "de";
        if (window.location.hash) {
            this.lang = window.location.hash.slice(1);
        }

        lintService.getLintResults(this.lang)
            .subscribe(data => this.lintEntries = data,
                       error => alert("Could not load lint data: " + error.status))
    }
}
