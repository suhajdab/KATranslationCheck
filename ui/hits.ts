import {Component, OnInit, Injectable} from 'angular2/core';
import {bootstrap} from 'angular2/platform/browser';
import 'rxjs/add/operator/map';
import {Http, HTTP_PROVIDERS, HTTP_BINDINGS} from 'angular2/http';
import { LanguageService } from './utils.ts';
import { RouteParams, ROUTER_DIRECTIVES, Router, CanReuse } from 'angular2/router';

@Injectable()
export class HitListService {
    constructor(private _http: Http,
                private _langService: LanguageService) { }

    getHits(rulename: string, filename: string) {
        let langObs = this._langService.getCurrentLanguage();
        return langObs.mergeMap((language) => {
            let url = filename ? `${language}/${filename}/${rulename}.json`
                : `${language}/${rulename}.json`;
            return this._http.get(url)
                .map(res => res.json())
        })
    }
}

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
    directives: [RuleInfoComponent],
    bindings: [HitListService]
})
export class HitListComponent implements CanReuse, OnInit {
    rule: any
    hits: any
    constructor(private _hitListService: HitListService,
                private _routeParams: RouteParams) {
    }

    routerCanReuse() { return false;}

    ngOnInit() {
        let mname = this._routeParams.get("mname")
        let filename = this._routeParams.get("filename")
        console.log(`Route machine name: ${mname}`)
        console.log(`Route filename: ${filename}`)
        this._hitListService.getHits(mname, filename)
            .subscribe(data => {
                this.rule = data.rule;
                this.hits = data.hits;
            },
            error => alert("Could not load hit data: " + error.status))
    }
}

@Injectable()
export class RuleErrorService {
    constructor(private _http: Http,
        private _langService: LanguageService) { }

    getRuleErrors() {
        let langObs = this._langService.getCurrentLanguage();
        return langObs.mergeMap((language) => {
            return this._http.get(`${language}/ruleerrors.json`)
                .map(res => res.json())
        })
    }
}

/**
 * Show rule parsing errors
 */
@Component({
    selector: 'rule-details',
    template: `
    <div class="row" *ngIf="rule_errors !== null && rule_errors.length > 0" *ngFor="#error of rule_errors">
        {{error}}
    </div>
    <div class="row" *ngIf="rule_errors !== null && rule_errors.length == 0">
        <h3 style="color: green">No rule errors</h3>
    </div>
    <div class="row" *ngIf="rule_errors === null">
        <h3>Loading...</h3>
    </div>
    `,
    bindings: [RuleErrorService]
})
export class RuleErrorsComponent {
    rule_errors: Array<string> = null;

    constructor(private _ruleErrorService : RuleErrorService) {
        this._ruleErrorService.getRuleErrors().subscribe(data => {
            this.rule_errors = data;
        },
        error => alert("Could not load hit data: " + error.status))
    }
}