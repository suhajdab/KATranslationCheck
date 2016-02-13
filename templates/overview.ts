import {Component, Injectable, Injector } from 'angular2/core';
import {bootstrap} from 'angular2/platform/browser';
import 'rxjs/add/operator/map';
import {Http, HTTP_PROVIDERS, HTTP_BINDINGS} from 'angular2/http';
import { RouterLink, ROUTER_PROVIDERS, ROUTER_DIRECTIVES, Router, CanReuse, RouteParams } from 'angular2/router';

@Injectable()
export class OverviewService {
    constructor(public http: Http) { }

    getHits(language: string, filename: string = null) {
        let url = filename == null ? `index.json` :
                    `${filename}/index.json`;
        console.log(url);
        return this.http.get(url)
                        .map(res => res.json())
    }
}

@Component({
    selector: 'rule-overview',
    template: `
    <h2>Statistics by rule</h2>
    <div *ngFor="#rule of rulestats">
        <div class="row">
            <a class="{{rule.color}}" (click)="viewHitlist(rule)"> <!-- , -->
                {{rule.name}}</a> ({{rule.num_hits}} hits)
        </div>
    </div>
    `
    inputs: ['rulestats'],
    directives: [ROUTER_DIRECTIVES],
    providers: [ROUTER_PROVIDERS]
})
export class RuleOverviewComponent {
    rulestats: any;

    constructor(injector: Injector) {
        this.router = injector.parent.get(Router);
    }

    viewHitlist(rule) {
        //this._router.navigate();
        this.router.navigate(['Hitlist', { mname: rule.machine_name }])
    }
}

@Component({
    selector: 'file-overview',
    template: `
    <h2>Statistics by file</h2>
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
    <rule-overview [rulestats]="rulestats"></rule-overview>
    <file-overview [filestats]="filestats" *ngIf="filestats"></file-overview>
    `,
    directives: [FileOverviewComponent, RuleOverviewComponent],
    bindings: [OverviewService]
})
export class OverviewComponent implements CanReuse {
    data: any
    rulestats: any
    filestats: any

    constructor(public overviewService: OverviewService, injector: Injector) {
        let routeParams = injector.parent.get(RouteParams);
        let filename = routeParams.get("filename"); //Might be null for total overview
        this.overviewService.getHits("de", filename)
            .subscribe(data => {
                this.rulestats = data.stats;
                this.filestats = data.files;
                this.data = data;},
            error => alert("Could not load overview data: " + error.status))
    }
}
