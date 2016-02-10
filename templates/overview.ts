import {Component} from 'angular2/core';
import {bootstrap} from 'angular2/platform/browser';
import 'rxjs/add/operator/map';
import {Http, HTTP_PROVIDERS, HTTP_BINDINGS} from 'angular2/http';

@Component({
    selector: 'rule-overview',
    template: `
    <h2>Statistics by rule</h2>
    <div *ngFor="#rule of rulestats">
        <div class="row">
            <a href="{{rule.machine_name}}.html" class="{{rule.color}}">
                {{rule.name}}</a> ({{rule.num_hits}} hits)
        </div>
    </div>
    `
    inputs: ['rulestats']
})
export class RuleOverviewComponent {
    rulestats: any;
}

@Component({
    selector: 'file-overview',
    template: `
    <h2>Statistics by file</h2>
    <div *ngFor="#filename, fileinfo of filestats">
        <div class="row">
            <span>(
                <span class="text-danger" *ngIf="fileinfo.errors">{{fileinfo.errors}} errors</span>,
                <span class="text-warning" *ngIf="fileinfo.warnings">{{fileinfo.warnings}} warnings</span>,
                <span class="text-primary" *ngIf="fileinfo.hits">{{fileinfo.hits}} hits</span>,
                <span class="text-success" *ngIf="fileinfo.infos">{{fileinfo.infos}} infos</span>,
                <span class="text-muted" *ngIf="fileinfo.notices">{{fileinfo.notices}} notices</span>,
            )</span>
        </div>
    </div>
    `,
    inputs: ['filestats']
})
export class FileOverviewComponent {
    filestats: any
}

@Component({
    selector: 'overview',
    template: `
    <div id="timestamprow" class="row">
          <p *ngIf="data.pageTimestamp">Page generated at {{data.pageTimestamp}}</p>
          <p *ngIf="data.downloadTimestamp">Translations downloaded at {{data.downloadTimestamp}}</p>
    </div>
    <rule-overview [rulestats]="rulestats"></rule-overview>
    <file-overview [filestats]="filestats"></file-overview>
    `
})
export class OverviewComponent {
    data: any
    rulestats: any
    filestats: any

    constructor(public http: Http) {
        this.http.get("index.json")
            .map(res => res.json())
            .subscribe(data => {
                this.rulestats = data.stats;
                this.filestats = data.files;
                this.data = data;
                console.log(this.data)},
            error => alert("Could not load overview data: " + error.status))
    }
}

bootstrap(OverviewComponent, [HTTP_BINDINGS]);
