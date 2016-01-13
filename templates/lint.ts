import {bootstrap} from 'angular2/platform/browser';
import {Component} from 'angular2/core';
import 'rxjs/add/operator/map';
import {Http, HTTP_PROVIDERS, HTTP_BINDINGS} from 'angular2/http';

@Component({
  selector: 'my-app',
  template:`
  <div class="row">
    <!--<h1>Showing {{lintEntries|length}} lint errors</h1>-->
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
  `
})
export class LintComponent {
   constructor(public http: Http) {
      var jsonName = 'lint-de.json';
      if(window.location.hash) {
        jsonName = 'lint-' + window.location.hash.slice(1) + '.json'
      }
      this.http.get(jsonName)
          .map(res => res.json())
          .subscribe(data => this.lintEntries = data)
   }
}

bootstrap(LintComponent, [HTTP_BINDINGS]);

/*
Copyright 2016 Google Inc. All Rights Reserved.
Use of this source code is governed by an MIT-style license that
can be found in the LICENSE file at http://angular.io/license
*/
