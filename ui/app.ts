import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { BrowserModule } from '@angular/platform-browser';

import {NgModule} from '@angular/core';

import {Http,  HttpModule} from '@angular/http';
import {LocationStrategy, Location, HashLocationStrategy, Router } from '@angular/router';

import {LanguageService} from "./utils.ts";
import {HitListService} from "./hits.ts";
import {KATCComponent} from "./KATC.ts";
import {CommentFilterPipe} from "./hits.ts";

@NgModule({
  imports:      [ BrowserModule, HttpModule, RouterModule ],
  declarations: [ KATCComponent ],
  bootstrap:    [ KATCComponent ],
  providers:    [ LanguageService, HitListService ],
  declarations: [CommentFilterPipe]
})
export class KATCModule {}

const platform = platformBrowserDynamic();
platform.bootstrapModule(KATCModule);
