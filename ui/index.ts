import {bootstrap} from 'angular2/platform/browser';
import {Component, provide, OnChanges, SimpleChange} from 'angular2/core';
import { RouteConfig, ROUTER_DIRECTIVES, ROUTER_PROVIDERS } from 'angular2/router';
import {LocationStrategy, Location, HashLocationStrategy, Router } from 'angular2/router'; 
import {OverviewComponent} from "./overview.ts";
import {HitListComponent} from "./hits.ts";
import {LintComponent} from "./lint.ts";
import {LanguageService} from "./utils.ts";
import {Http, HTTP_PROVIDERS, HTTP_BINDINGS} from 'angular2/http';


@Component({
  selector: 'foobar',
  template: `<h3><a [routerLink]="['Lint results']">Nothing will happen when clicking here</a></h3>`,
  directives: [ROUTER_DIRECTIVES],
  providers: [ROUTER_PROVIDERS]
})
export class FoobarComponent {
}

@Component({
  selector: 'katc',
  template:`
  <!-- navigation -->
  <nav class="navbar navbar-default navbar-fixed-top" role="navigation">
      <div class="container">
          <div class="navbar-header page-scroll">
              <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-ex1-collapse">
                  <span class="sr-only">Toggle navigation</span>
                  <span class="icon-bar"></span>
                  <span class="icon-bar"></span>
                  <span class="icon-bar"></span>
              </button>
              <div class="navbar-brand page-scroll">    
                  <a style="color: #5e5e5e;" [routerLink]="['Home']">KATranslationCheck Deutsch</a>
                  <div style="padding-left: 8px; display: inline-block;">
                      <select [(ngModel)]="language" (change)="onLanguageChange($event)">>
                          <option *ngFor="#langobj of languages" [value]="langobj.code">{{langobj.name}}</option>
                      </select>
                  </div>
              </div>
          </div>
          <div class="collapse navbar-collapse navbar-ex1-collapse">
              <ul class="nav navbar-nav">
                  <li class="hidden">
                      <a class="page-scroll" href="#page-top"></a>
                  </li>
                  <li>
                      <a [routerLink]="['Home']">Rules</a>
                  </li>
                  <li>
                      <a [routerLink]="['Lint results']">Lint</a>
                  </li>
              </ul>
          </div>
          <!-- /.navbar-collapse -->
      </div>
      <!-- /.container -->
  </nav>
  <div id="maincontainer" class="container">
  <foobar></foobar>
    <router-outlet></router-outlet>
  </div>
  `,
  directives: [ROUTER_DIRECTIVES, FoobarComponent],
  providers: [ROUTER_PROVIDERS],
  bindings: [LanguageService]
})
@RouteConfig([
    {
        path: '/',
        name: 'Home',
        component: OverviewComponent,
        useAsDefault: true
    },
    {
      path: '/overview/:filename',
      name: 'Overview',
      component: OverviewComponent,
    },
    {
      path: '/hits/:mname/:filename', //Machine name
      name: 'Hitlist',
      component: HitListComponent
    },
    {
      path: '/lint',
      name: 'Lint results',
      component: LintComponent
    }
    {
        path: '/**',
        name: 'Catchall',
        redirectTo: ['Home']
    }
])
export class KATCApp implements OnChanges {
    language: string = "de";
    languages: any;

    onLanguageChange(evt) {
        console.log(evt.target.value);
        this.language = evt.target.value;
        this._router.renavigate();
    }

    ngOnChanges(changes: { [propName: string]: SimpleChange }) {
        console.log(changes)
        if("language" in changes) {
            console.log("New language: " + changes["language"])
        }
    }

    constructor(private _langService: LanguageService, private _router : Router) {
        this.languages = _langService.allLanguages();
    }
}

bootstrap(KATCApp, [
  HTTP_BINDINGS,
  ROUTER_PROVIDERS,
  provide(LocationStrategy, { useClass: HashLocationStrategy })])
  //

