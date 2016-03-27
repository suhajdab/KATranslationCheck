import { Injectable, Injector } from 'angular2/core';
import 'rxjs/add/operator/map';
import Rx from 'rxjs/Rx';
import { KATCApp } from './index.ts';

@Injectable()
export class LanguageService {
    defaultLanguage: string = "de";

    constructor(private _injector: Injector) { }

    storageAvailable() {
        try {
            let storage = window.localStorage,
                let x = '__storage_test__';
            storage.setItem(x, x);
            storage.removeItem(x);
            return true;
        }
        catch (e) {
            return false;
        }
    }

    storeLanguage(lang: string) {
        if (this.storageAvailable()) {
            localStorage.setItem("katc-language", lang);
        }
    }

    getStoredLanguage(): string {
        if (this.storageAvailable()) {
            let storedLang = window.localStorage.getItem("katc-language");
            if (storedLang === null) {
                return this.defaultLanguage;
            }
            console.log(storedLang);
            return storedLang;
        } else {
            return this.defaultLanguage;
        }
    }


    allLanguages(): Map<string, string> {
        return [{ name: "Deutsch (DE)", code: "de" },
                { name: "Português (BR)", code: "pt-BR" },
                { name: "Polski (PL)", code: "pl" },
                { name: "Nederlands (NL)", code: "nl" },
                { name: "български (BG)", code: "bg" }]
    }

    getLanguageByCode(code: string): string {
        for (obj in this.allLanguages()) {
            if (obj.code == code) {
                return obj
            }
        }
        return null;
    }

    getCurrentLanguage(language: string, rulename: string) {
        let appPromise = this._injector.parent.get(KATCApp)
        return Rx.Observable.fromPromise(appPromise)
                .map((app) => app.language)
    }
}