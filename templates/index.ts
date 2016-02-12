import {bootstrap} from 'angular2/platform/browser';
import {Component} from 'angular2/core';
import { RouteConfig, ROUTER_DIRECTIVES, ROUTER_PROVIDERS } from 'angular2/router';
import 'rxjs/add/operator/map';
import {OverviewComponent} from "./overview.ts";
import {HitListComponent} from "./hits.ts";
import {LintComponent} from "./lint.ts";
import {Http, HTTP_PROVIDERS, HTTP_BINDINGS} from 'angular2/http';

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
              <a class="navbar-brand page-scroll" href="/">KATranslationCheck Deutsch</a>
          </div>
          <div class="collapse navbar-collapse navbar-ex1-collapse">
              <ul class="nav navbar-nav">
                  <li class="hidden">
                      <a class="page-scroll" href="#page-top"></a>
                  </li>
                  <li>
                      <a [routerLink]="['Overview']">Rules</a>
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
    <router-outlet></router-outlet>
  </div>
  `,
  directives: [ROUTER_DIRECTIVES],
  providers: [
    ROUTER_PROVIDERS
  ]
})
@RouteConfig([
    {
      path: '/overview',
      name: 'Overview',
      component: OverviewComponent,
      useAsDefault: true
    },
    {
      path: '/rule/:rulemname',
      name: 'Rule hits',
      component: HitListComponent
    },
    {
      path: '/lint',
      name: 'Lint results',
      component: LintComponent
    }
])
export class KATCApp {
   constructor() {

   }
}

bootstrap(KATCApp, [HTTP_BINDINGS]);

/*
Copyright 2016 Google Inc. All Rights Reserved.
Use of this source code is governed by an MIT-style license that
can be found in the LICENSE file at http://angular.io/license
*/
