#!/usr/bin/env python3
# The contents of this file are subject to the Common Public Attribution
# License Version 1.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# https://github.com/TechIdiots-LLC/tippr/blob/master/LICENSE.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for
# the specific language governing rights and limitations under the License.
#
# The Original Code is Tippr.
#
# The Initial Developer of the Original Code is TechIdiots LLC.
# Copyright (c) 2026 TechIdiots LLC. All Rights Reserved.
###############################################################################
"""Bring every catalog up to date with the template (tippr_i18n/r2.pot).

Make the template first, in the tippr repository (it writes
../i18n/tippr_i18n/r2.pot, or wherever r2.lib.translation.I18N_PATH points):

    cd tippr/r2 && make i18n

then here:

    python3 update_catalogs.py          (or: make update)

For each tippr_i18n/<lang>/LC_MESSAGES/r2.po it:
  - merges in the template's strings (msgmerge): new ones are untranslated,
    changed ones keep their old translation marked fuzzy (with the previous
    English, "#| msgid", to compare), removed ones are dropped;
  - (not en) clears translations that are just the English, which only hide
    what's untranslated (the site shows the English for those anyway);
  - fixes leftover reddit branding: /r/ and r/ links become /v/;
  - marks fuzzy any translation whose placeholders (%(name)s, %s, {name})
    don't match the English, which would fail or show the wrong value.
The site only uses translations that aren't fuzzy. Needs GNU gettext
(msgmerge) and polib (pip install polib).
"""

import glob
import os
import re
import subprocess
import sys
import tempfile

import polib

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOGS = os.path.join(HERE, "tippr_i18n")
TEMPLATE = os.path.join(CATALOGS, "r2.pot")

PLACEHOLDER = re.compile(
    r"%\([A-Za-z_][A-Za-z0-9_]*\)[sdifr]|%[sdif]|\{[A-Za-z_][A-Za-z0-9_]*\}")
FIXES = [
    (re.compile(r"(?<![A-Za-z0-9])/r/"), "/v/"),
    (re.compile(r"(?<![A-Za-z0-9/])r/(?=[%{A-Za-z0-9])"), "/v/"),
    (re.compile(r"\bredditors?\b"), "users"),
    (re.compile(r"\bReddit\b"), "Tippr"),
    (re.compile(r"\breddit\b"), "tippr"),
]
DROP_HEADERS = ("X-Crowdin-Project", "X-Crowdin-File", "X-Crowdin-Language",
                "X-Generator", "Generated-By")


def placeholders(text):
    return sorted(PLACEHOLDER.findall(text or ""))


def fix(text):
    for rx, rep in FIXES:
        text = rx.sub(rep, text)
    return text


def merge(path):
    """msgmerge the catalog at path with the template, in place."""
    with tempfile.NamedTemporaryFile(suffix=".po", delete=False,
                                     dir=os.path.dirname(path)) as tmp:
        out = tmp.name
    try:
        subprocess.check_call(["msgmerge", "--quiet", "--no-wrap",
                               "--previous", path, TEMPLATE, "-o", out])
        os.replace(out, path)
    finally:
        if os.path.exists(out):
            os.unlink(out)


def tidy(path, lang):
    po = polib.pofile(path, wrapwidth=0)
    stats = dict(copies=0, branded=0, broken=0)
    po.metadata["Project-Id-Version"] = "tippr"
    po.metadata["Report-Msgid-Bugs-To"] = \
        "https://github.com/TechIdiots-LLC/tippr-i18n/issues"
    if "reddit" in po.metadata.get("Last-Translator", ""):
        po.metadata["Last-Translator"] = "tippr translators"
    for header in DROP_HEADERS:
        po.metadata.pop(header, None)
    po.header = ""
    for entry in [e for e in po if e.obsolete]:
        po.remove(entry)
    for e in po:
        plural = bool(e.msgid_plural)
        values = list(e.msgstr_plural.values()) if plural else [e.msgstr]
        if not any(values):
            continue
        fuzzy = "fuzzy" in e.flags
        if lang != "en" and not fuzzy and values[0] == e.msgid and \
                (not plural or values[-1] == e.msgid_plural):
            if plural:
                e.msgstr_plural = {k: "" for k in e.msgstr_plural}
            else:
                e.msgstr = ""
            stats["copies"] += 1
            continue
        if plural:
            new = {k: fix(v) if v else v for k, v in e.msgstr_plural.items()}
            if new != e.msgstr_plural:
                e.msgstr_plural = new
                stats["branded"] += 1
            values = list(new.values())
        else:
            new = fix(e.msgstr)
            if new != e.msgstr:
                e.msgstr = new
                stats["branded"] += 1
            values = [new]
        if fuzzy:
            continue
        allowed = [placeholders(e.msgid)]
        if plural:
            allowed.append(placeholders(e.msgid_plural))
        for value in values:
            found = placeholders(value)
            # a plural form may leave the count out ("one comment")
            if value and found not in allowed and not (
                    plural and set(found) <= set(placeholders(e.msgid_plural))):
                e.flags.append("fuzzy")
                stats["broken"] += 1
                break
    po.save(path)
    return stats


def main(langs):
    if not os.path.exists(TEMPLATE):
        sys.exit("%s is missing: run `make i18n` in tippr/r2 first" % TEMPLATE)
    paths = sorted(glob.glob(os.path.join(CATALOGS, "*", "LC_MESSAGES", "r2.po")))
    for path in paths:
        lang = path.split(os.sep)[-3]
        if langs and lang not in langs:
            continue
        merge(path)
        stats = tidy(path, lang)
        po = polib.pofile(path)
        print("%-8s %3d%% translated (%d fuzzy); cleared %d English copies, "
              "fixed %d links, %d mismatched placeholders now fuzzy" % (
                  lang, po.percent_translated(), len(po.fuzzy_entries()),
                  stats["copies"], stats["branded"], stats["broken"]))


if __name__ == "__main__":
    main(sys.argv[1:])
