import {Component, Injectable, Injector } from 'angular2/core';
import {Http, HTTP_PROVIDERS, HTTP_BINDINGS} from 'angular2/http';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/mergeMap';
import {LanguageService} from './utils.ts';
import { RouterLink, ROUTER_PROVIDERS, ROUTER_DIRECTIVES, Router, CanReuse, RouteParams } from 'angular2/router';


class HitCount {
    constructor(public rule, public count: number) {
    }
}

@Component({
    selector: 'search-tcomment',
    template: `
    <h3>Search by comment (Experts only!)</h3>
    <div id="commentSearch" style="margin-bottom: 40px;">
        <form>
            <label for="searchTermInput">Search term</label>
            <input type="text" id="searchTermInput" class="form-control" [(ngModel)]="term">
            <button class="btn btn-info" (click)="searchTComment()" style="margin-top: 10px;">
                Search by tcomment
            </button>
        </form>
        <h5 *ngIf="working">
            <span class="glyphicon glyphicon-time"></span>
            Working...
        </h5>
        <div style="margin-top: 10px">
            <div *ngFor="#hitcount of hits">
                <a class="{{hitcount.rule.color}}" (click)="viewHitlist(hitcount.rule)">
                    {{hitcount.rule.name}}</a> ({{hitcount.count}} hits)
            </div>
        </div>
    </div>
    `
    directives: [ROUTER_DIRECTIVES],
    providers: [ROUTER_PROVIDERS]
})
export class ExerciseSearchComponent {
    filename: string;
    term: string = "combining-like-terms";
    hits: HitCount[];
    working: boolean;
    router: Router;

    constructor(injector: Injector, private _http: Http, private _langService: LanguageService) {
        this.router = injector.parent.get(Router);
        console.log("Init");
    }

    /**
     * Search every rule hit for each rule
     */
    searchTComment() {
        this.hits = [];
        this.working = true;
        this.getAllRuleURLs().mergeMap((url) => {
            var rule = null;
            return this._http.get(url)
                .map(res => res.json())
                .do(data => rule = data.rule)
                .flatMap(data => data.hits)
                .filter(hit => hit.hasOwnProperty("tcomment"))
                .count(hit => hit.tcomment.includes(this.term))
                .filter(count => count > 0)
                .map(count => new HitCount(rule, count))
        }).toArray().subscribe(hits => this.hits = hits,
            err => console.error(err),
            () => this.working = false)
    }

    viewHitlist(rule) {
        //this._router.navigate();
        this.router.navigate(['Hitlist', {
            mname: rule.machine_name,
            filename: this.filename === null ? "" : this.filename,
            tcommentFilter: this.term
        }])
    }

    private getAllRuleURLs() {
        let langObs = this._langService.getCurrentLanguage();
        return langObs.mergeMap((language) => {
            return this._http.get(`/${language}/index.json`)
                .map(res => res.json())
                .flatMap(data => data.stats)
                .filter(stat => stat.num_hits > 0)
                .map(stat => `/${language}/${stat.machine_name}.json`)
        }
        )
    }
}