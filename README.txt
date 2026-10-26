tippr-i18n: tippr's translations
================================

One catalog per language, tippr_i18n/<lang>/LC_MESSAGES/r2.po, made from the
template tippr_i18n/r2.pot (every string in tippr's code). The installer and
the Docker image build them (make: r2.mo, plus r2.data, the language's name
and how complete it is). Languages under half translated show "(*)" in the
language list; the site shows English for anything not translated.

Updating after the code changes
-------------------------------

1. Make the template, in the tippr repository:

       cd tippr/r2 && make i18n

   (it writes r2.pot into the tippr_i18n package it imports: this
   repository's tippr_i18n/ when it's installed from this checkout, as the
   installer does, in /home/tippr/src/i18n)

2. Bring the catalogs up to date (needs GNU gettext and `pip install polib`):

       make update

   New strings come in untranslated; changed ones keep their old translation
   marked fuzzy, with the previous English ("#| msgid") to compare; strings
   the code no longer has are dropped. update_catalogs.py also clears
   "translations" that are just the English, fixes leftover reddit links
   (/r/ -> /v/), and marks fuzzy any translation whose placeholders don't
   match the English.

Translating
-----------

Edit a language's r2.po in any PO editor (Poedit, Lokalize, Weblate ...):

- fill in msgstr for untranslated strings;
- check the fuzzy ones against their English, fix them and remove the
  "fuzzy" flag (the site doesn't use fuzzy translations);
- keep placeholders exactly as in the English: %(name)s, %s, {name}, and
  Markdown links [text](/path);
- a community is a "vault" (/v/name); members are "users".

Then check it with `msgfmt --check-format -o /dev/null <file>` and send a
pull request. A language's display names and plural rules are in its
catalog's header (Display-Name, Display-Name-en, Plural-Forms).

Where this came from
--------------------

This is a fork of reddit's translation files
(https://github.com/reddit-archive/reddit-i18n), which reddit archived along
with the rest of its open-source code. Those translations were made by
reddit's volunteer translators through Crowdin; tippr has since moved them to
its own strings (vaults, scales, AI labels and the rest) and keeps them up to
date here, so pull requests are welcome. Crowdin isn't used any more.
