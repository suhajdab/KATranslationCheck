import {bootstrap} from 'angular2/platform/browser';
import {Component, provide} from 'angular2/core';
import { RouteConfig, ROUTER_DIRECTIVES, ROUTER_PROVIDERS } from 'angular2/router';
import {LocationStrategy, Location, HashLocationStrategy } from 'angular2/router'; 
import 'rxjs/add/operator/map';
import {OverviewComponent} from "./overview.ts";
import {HitListComponent} from "./hits.ts";
import {LintComponent} from "./lint.ts";
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
              <a class="navbar-brand page-scroll" href="/">KATranslationCheck Deutsch</a>
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
      path: '/hits/:mname', //Machine name
      name: 'Hitlist',
      component: HitListComponent
    },
    {
      path: '/lint',
      name: 'Lint results',
      component: LintComponent
    }
])
export class KATCApp {
}

bootstrap(KATCApp, [
  HTTP_BINDINGS,
  ROUTER_PROVIDERS,
  provide(LocationStrategy, { useClass: HashLocationStrategy })])
  //

