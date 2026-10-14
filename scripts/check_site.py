#!/usr/bin/env python3
"""Small offline smoke check for the static website; standard library only."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys


ROOT = Path(__file__).resolve().parents[1] / "site"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids = set()
        self.refs = []
        self.errors = []
        self.h1_count = 0
        self.lang = ""
        self.viewport = ""
        self.description = ""
        self.title = ""
        self.in_title = False

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if "id" in attrs:
            value = attrs["id"]
            if not value or value in self.ids:
                self.errors.append("Empty or duplicate ID: {!r}".format(value))
            self.ids.add(value)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "h1":
            self.h1_count += 1
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            if attrs.get("name") == "viewport":
                self.viewport = attrs.get("content", "")
            if attrs.get("name") == "description":
                self.description = attrs.get("content", "")
        if tag == "img" and "alt" not in attrs:
            self.errors.append("Image missing alt attribute")
        if "data-draft" in attrs:
            self.errors.append("Unresolved data-draft marker")
        for attribute in ("href", "src"):
            if attribute in attrs:
                self.refs.append(attrs[attribute] or "")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def main():
    pages = {}
    for path in sorted(ROOT.rglob("*.html")):
        page = Page(path)
        source = path.read_text(encoding="utf-8")
        page.feed(source)
        page.close()
        if not source.lstrip().lower().startswith("<!doctype html>"):
            page.errors.append("Missing HTML5 doctype")
        if not page.lang:
            page.errors.append("Missing document language")
        if not page.title.strip() or not page.description:
            page.errors.append("Missing title or description")
        if "width=device-width" not in (page.viewport or ""):
            page.errors.append("Missing responsive viewport")
        if page.h1_count != 1:
            page.errors.append("Expected exactly one h1")
        pages[path.resolve()] = page

    if (ROOT / "index.html").resolve() not in pages:
        print("FAIL: site/index.html is missing")
        return 1

    for page in pages.values():
        for reference in page.refs:
            if not reference.strip() or reference == "#":
                page.errors.append("Empty/placeholder link or asset reference")
                continue
            try:
                url = urlsplit(reference)
            except ValueError:
                page.errors.append("Invalid URL: " + reference)
                continue
            if url.scheme in ("https", "http", "mailto", "tel") or url.netloc:
                continue
            if url.scheme:
                page.errors.append("Unexpected URL scheme: " + reference)
                continue
            if url.path.startswith("/"):
                target = ROOT / unquote(url.path).lstrip("/")
            elif url.path:
                target = page.path.parent / unquote(url.path)
            else:
                target = page.path
            target = target.resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                page.errors.append("Reference leaves site/: " + reference)
                continue
            if target.is_dir():
                target /= "index.html"
            if not target.is_file():
                page.errors.append("Missing local file: " + reference)
            elif url.fragment and target in pages:
                if unquote(url.fragment) not in pages[target].ids:
                    page.errors.append("Missing local fragment: " + reference)

    failures = 0
    for page in pages.values():
        for error in page.errors:
            print("FAIL {}: {}".format(page.path.relative_to(ROOT), error))
            failures += 1
    if failures:
        return 1
    print("PASS: {} HTML page(s); local references and document checks.".format(len(pages)))
    print("External URLs and visual accessibility require separate review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
