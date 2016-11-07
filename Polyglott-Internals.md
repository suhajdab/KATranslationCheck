# Polyglott internals

## Database backend

Polyglott uses Uli Köhler's YakDB - a database specialized in high performance indexing and ease of use. When using the polyglott indexer, you need to ensure a YakDB instance runs on the same computer (basically you just need to run `yakserver` in a background shell.

## Tables

Table 1 ("record table") contains `English ->  {Language: Translation}` mappings.n 
This table is built using YakDB's NUL-separated append merge operator, so you can just write `Language\x1DTranslation` values to this table disregarding all previous writes to the same key. The values are then merged automatically.

Table 2 ("index table") contains `Translation -> English` mappings for lookup.

## Indexing

The indexer reads PO files from the `cache` directory - the available languages are automatically determined.
For each PO file, all strings where the `msgstr` is empty or contains only whitespace are removed.

For each remaining string the PO file, two huge YakDB PUT requests are assembled:
For the record table, `English -> Language\x1DTranslation` is written for every PO entry.
For the index table, `Translation -> English` is written for every PO entry.

## Compaction

In order to speed up querying and reduce disk space usage, after the indexing process, a full-table compaction is requested for both tables. This ensures that all record table merge operator operations are performed ahead-of-time and the YakDB disk logs are cleared.

## Search process

When a search request is issued, the backend first looks up the query in the index table. This gives either no result (in which case an empty JSON dictionary is returned) or an english string.
The english string is subsequently looked up in the record table, yielding a NUL-separated list of `Language\x1DTranslation` mappings. Those are simply split and put into a dictionary which is then returned to the user as JSON.
