# Polyglott server
[PolyglottServer.py](https://github.com/KA-Advocates/KATranslationCheck/blob/master/PolyglottServer.py) is the server component for KAPolyglott. It implements a simple HTTP API to load translations and a videos map.

The server backend works with [YakDB](https://github.com/ulikoehler/YakDB), a fast NoSQL database specialized in indexing.

## API examples :
**Input:**
   http://localhost:7798/translate.json?s=Einfache%20Addition

**Response:**
   
`{
ar: "พื้นฐานการบวก",
de: "Einfache Addition",
fr: " Les bases de l'addition ",
en: "Basic addition"
}`

##Example for Video-Map
**Input:**
   http://localhost:7798/videos.json?id=basic-addition

**Response:**

`{
fr: "https://www.youtube.com/watch?v=7CKiA8d_x2U",
hi: "https://www.youtube.com/watch?v=B-LhPELGA-8",
el: "https://www.youtube.com/watch?v=CRw6SfrA11I",
mn: "https://www.youtube.com/watch?v=SAG78hNi9sQ",
cs: "https://www.youtube.com/watch?v=6WwRwxkLuP0",
ka: "https://www.youtube.com/watch?v=TMgP0C7JAg4",
de: "https://www.youtube.com/watch?v=G8YSITorz8E",
ja: "https://www.youtube.com/watch?v=OLKKUfW-eSc",
nb: "https://www.youtube.com/watch?v=yhAWMAZlVEM",
ta: "https://www.youtube.com/watch?v=dbLvcNe0p8g",
ar: "https://www.youtube.com/watch?v=B5k-CoJfmLs",
he: "https://www.youtube.com/watch?v=MZ2TVE7bYlE",
en: "https://www.youtube.com/watch?v=AuX7nPBqDts",
bn: "https://www.youtube.com/watch?v=izVE03egWV8",
bg: "https://www.youtube.com/watch?v=IrdMDufjFvg",
sr: "https://www.youtube.com/watch?v=stdoQSAFZng"
}`

## Example for /pofilter API

Returns a PO file based on the given crowdin filepath that contains filtered PO data.
Please see [the source code](https://github.com/KA-Advocates/KATranslationCheck/blob/master/pofilter.py#L12) for documentation on which tools (query option) are available. The default `tool=id_to_str` contains untranslated strings.
Based on Hitoshi Yamauchi's pofilter script.
Works only for cached files.

[https://qa.kadeutsch.org/pofilter/2_high_priority_content/learn.math.3rd-engage-ny-eureka.articles.pot?lang=de&tool=id_to_str](https://qa.kadeutsch.org/pofilter/2_high_priority_content/learn.math.3rd-engage-ny-eureka.articles.pot?lang=de&tool=id_to_str)

## Example for /po API

Returns the raw PO file. This file is updated periodically for most languages, and the service is much faster than exporting from Crowdin. Works only for cached files

[https://qa.kadeutsch.org/po/2_high_priority_content/learn.math.3rd-engage-ny-eureka.articles.pot?lang=de](https://qa.kadeutsch.org/po/2_high_priority_content/learn.math.3rd-engage-ny-eureka.articles.pot?lang=de)

## pofiles.json API

This API is non-parametric and allows you to retrieve a sorted list of filenames.

[https://qa.kadeutsch.org/pofiles.json](https://qa.kadeutsch.org/pofiles.json)

```json
[
"1_high_priority_platform/_other_.pot",
"1_high_priority_platform/about.donate.pot",
"1_high_priority_platform/about.privacy_policy.pot",
"1_high_priority_platform/about.terms_of_service.pot",
....
```