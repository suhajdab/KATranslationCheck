
import {Component, provide, OnChanges, SimpleChange} from '@angular/core';
import { RouteConfig, RouterModule } from '@angular/router';
import {LocationStrategy, Location, HashLocationStrategy, Router } from '@angular/router';

import {OverviewComponent} from "./overview.ts";
import {HitListComponent, RuleErrorsComponent} from "./hits.ts";
import {LintComponent} from "./lint.ts";
import {LanguageService} from "./utils.ts";

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
                  <li>
                      <a [routerLink]="['Rule errors']">Rule errors</a>
                  </li>
              </ul>
          </div>
          <!-- /.navbar-collapse -->
      </div>
      <!-- /.container -->
  </nav>
  <div id="maincontainer" class="container">
    <router-outlet></router-outlet>
  </div>
  `,
  styles: ["#maincontainer {margin-top: 80px}"],
  directives: [ROUTER_DIRECTIVES],
  providers: [ROUTER_PROVIDERS]
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
    },
    {
      path: '/ruleerrors',
      name: 'Rule errors',
      component: RuleErrorsComponent
    },
    {
        path: '/**',
        name: 'Catchall',
        redirectTo: ['Home']
    }
])
export class KATCComponent {
    language: string;
    languages: any;

    onLanguageChange(evt) {
        console.log(evt.target.value);
        this.language = evt.target.value;
        this._langService.storeLanguage(this.language);
        this._router.renavigate();
    }

    constructor(private _langService: LanguageService,
                private _router : Router) {
        this.languages = _langService.allLanguages();
        this.language = this._langService.getStoredLanguage();
    }
}

