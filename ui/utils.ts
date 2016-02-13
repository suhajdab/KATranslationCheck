import { Injectable, Injector } from 'angular2/core';
import 'rxjs/add/operator/map';
import Rx from 'rxjs/Rx';
import { KATCApp } from './index.ts';

@Injectable()
export class LanguageService {
    constructor(private _injector: Injector) { }

    allLanguages(): Map<string, string> {
        return [{ name: "Deutsch", code: "de" },
                { name: "Português (BR)", code: "pt" }]
    }

    getCurrentLanguage(language: string, rulename: string) {
        let appPromise = this._injector.parent.get(KATCApp)
        return Rx.Observable.fromPromise(appPromise)
                .map((app) => app.language)
    }
}