import {Component, Pipe, PipeTransform} from 'angular2/core';
import {bootstrap} from 'angular2/platform/browser';
import 'rxjs/add/operator/map';
import {Http, HTTP_PROVIDERS, HTTP_BINDINGS} from 'angular2/http';

/**
 * Display info about a rule, e.g. headline, the rule itself etc
 */
@Component({
    selector: 'rule-details',
    template: `
    <div class="row" *ngIf="rule">
        <h1>{{rule.name}}</h1>
        <div class="row">
          <div class="panel panel-default">
            <div class="panel-body">
              {{rule.description}}
            </div>
          </div>
        </div>
    </div>
    `,
    styles: [],
    inputs: ['rule']
})
export class RuleInfoComponent {
    rule: any
}

@Component({
    selector: 'hits',
    template: `
    <rule-details [rule]="rule"></rule-details>
    <div class="row hit" *ngFor="#hit of hits; #idx = index">
        <button class="btn-danger btn report-button">Report error</button>
        <a target="_blank" href="{{hit.crowdinLink}}" class="btn-success btn translate-button">Translate on Crowdin</a>
        <h3><span class="hitno">Hit #{{idx + 1}}:</span> <code class="hittext">{{hit.hit}}</code></h3>

        <h6>Comment:</h6>
        <div class="tcomment" [innerHTML]="hit.tcomment"></div>

        <h4>Translated text:</h4>
        <pre class="translated">{{hit.msgstr}}</pre>
        <h4>Original text:</h4>
        <pre class="original">{{hit.msgid}}</pre>

        <div class="imagelist" *ngIf="hit.origImages">
          <button class="btn-primary btn show-images-button">Show images</button>
          <h4>Original images</h4>
          <a class="image-link" href="{{img}}" *ngFor="#img of hit.origImages">{{img}}</a>
          <h4>Translated images</h4>
          <a class="image-link" href="{{img}}" *ngFor="#img of hit.translatedImages">{{img}}</a>
        </div>
        <hr/>
    </div>
    `,
    styles: [
        ".hitno {font-weight: bold;}",
        ".highlight { background-color: yellow }",
        ".report-button, .translate-button {float: right;}",
        ".tcomment {margin-left: 25px; color: #444;}"
    ]
    inputs: ['hits'],
    directives: [RuleInfoComponent]
})
export class HitListComponent {
    hits: any
    rule: any
    
    constructor(public http: Http) {
        this.http.get("additional-spaces-after-for-italic-word.json")
            .map(res => res.json())
            .subscribe(data => {
                this.rule = data.rule;
                this.hits = data.hits;
            },
            error => alert("Could not load overview data: " + error.status))
    }
}

   
bootstrap(HitListComponent, [HTTP_BINDINGS]);
