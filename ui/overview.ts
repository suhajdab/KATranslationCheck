import {Component, Injectable, Injector } from 'angular2/core';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/mergeMap';
import {Http, HTTP_PROVIDERS, HTTP_BINDINGS} from 'angular2/http';
import {LanguageService} from './utils.ts';
import {ExerciseSearchComponent} from './search.ts';
import { RouterLink, ROUTER_PROVIDERS, ROUTER_DIRECTIVES, Router, CanReuse, RouteParams } from 'angular2/router';

@Injectable()
export class OverviewService {
    constructor(private _http: Http,
                private _langService : LanguageService) {}

    getOverviewData(filename: string = null) {
        let urlProto = filename == null ? `index.json` : `${filename}/index.json`;
        let langObs = this._langService.getCurrentLanguage();
        return langObs.mergeMap((language) =>
            this._http.get(`${language}/${urlProto}`)
                    .map(res => res.json())
        )
    }
}

@Component({
    selector: 'rule-overview',
    template: `
    <h3>Statistics by rule</h3>
    <div *ngFor="#rule of rulestats">
        <div class="row">
            <a class="{{rule.color}}" (click)="viewHitlist(rule)"> <!-- , -->
                {{rule.name}}</a> ({{rule.num_hits}} hits)
        </div>
    </div>
    `
    inputs: ['rulestats', 'filename'],
    directives: [ROUTER_DIRECTIVES],
    providers: [ROUTER_PROVIDERS]
})
export class RuleOverviewComponent {
    rulestats: any;
    filename: string;

    constructor(injector: Injector) {
        this.router = injector.parent.get(Router);
    }

    viewHitlist(rule) {
        //this._router.navigate();
        this.router.navigate(['Hitlist', { mname: rule.machine_name,
            filename: this.filename === null ? "" : this.filename }])
    }
}

@Component({
    selector: 'file-overview',
    template: `
    <h3>Statistics by file</h3>
    <div *ngFor="#fileinfo of filestats">
        <div class="row">
            <a (click)="viewFile(fileinfo.filename)">{{fileinfo.filename}}</a>
            <span>(
                <span class="text-danger" *ngIf="fileinfo.errors">{{fileinfo.errors}} errors,</span>
                <span class="text-warning" *ngIf="fileinfo.warnings">{{fileinfo.warnings}} warnings,</span>
                <span class="text-primary" *ngIf="fileinfo.hits">{{fileinfo.hits}} hits,</span>
                <span class="text-success" *ngIf="fileinfo.infos">{{fileinfo.infos}} infos,</span>
                <span class="text-muted" *ngIf="fileinfo.notices">{{fileinfo.notices}} notices</span>
            )</span>
            <a href="{{fileinfo.translation_url}}" target="_blank">
                <span class="label label-success">Translate on Crowdin</span>
            </a>
        </div>
    </div>
    `,
    inputs: ['filestats']
})
export class FileOverviewComponent {
    filestats: any

    constructor(injector: Injector) {
        this.router = injector.parent.get(Router);
    }

    viewFile(filename) {
        this.router.navigate(['Overview', {filename: filename}])
    }
}

@Component({
    selector: 'overview',
    template: `
    <div id="timestamprow" class="row" *ngIf="data">
          <p *ngIf="data.pageTimestamp">Page generated at {{data.pageTimestamp}}</p>
          <p *ngIf="data.downloadTimestamp">Translations downloaded at {{data.downloadTimestamp}}</p>
    </div>
    <h2 *ngIf="filename === null">KATC overview</h2>
    <h2 *ngIf="filename !== null">KATC overview for <code class="hittext">{{filename}}</code></h2>
    <rule-overview [rulestats]="rulestats" [filename]="filename"></rule-overview>
    <file-overview [filestats]="filestats" *ngIf="filestats"></file-overview>
    <search-tcomment></search-tcomment>    
    `,
    directives: [FileOverviewComponent, RuleOverviewComponent, ExerciseSearchComponent],
    bindings: [OverviewService]
})
export class OverviewComponent implements CanReuse {
    data: any
    rulestats: any
    filestats: any
    filename: string = null

    routerCanReuse() { return false; }

    viewHitlist(rule) {
        //this._router.navigate();
        this.router.navigate(['Hitlist', {
            mname: rule.machine_name,
            filename: this.filename === null ? "" : this.filename
        }])
    }

    constructor(public overviewService: OverviewService, injector: Injector) {
        let routeParams = injector.parent.get(RouteParams);
        //filename Might be null for total overview
        this.filename = routeParams.get("filename")
        this.overviewService.getOverviewData(this.filename)
            .subscribe((data) => {
                this.rulestats = data.stats;
                this.filestats = data.files;
                this.data = data;},
            error => alert("Could not load overview data: " + error.status))
    }
}
