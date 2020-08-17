#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script for fetching and writing paper data to a file.
Support for querying DOIs in Semantic Scholar and arXiv. Then processes
this data so it will be ready for NLP.

TODOs if exteding for more use:
- create a class for this (remove globals)
- have better defaut naming of dumps
"""

import argparse
import json
import os
import requests

import feedparser


def ss_parse(content):
    """ Strips out extraneous information from fetched results.

    Removes all citations, and extraneous info from the response and just gives back:
        * Abstract
        * Title
        * DOI
        * Authors
    """
    data = json.loads(content)
    return json.dumps(
        {
            "abstract": data["abstract"],
            "title": data["title"],
            "doi": data["doi"],
            "id": None,
            "authors": [author["name"] for author in data["authors"]],
        },
        indent=4, sort_keys=True,
    )


def ar_parse(src):
    """ Parses XML content from arXiv."""
    xml = feedparser.parse(src)
    return json.dumps(
        {
            "abstract": xml.entries[0].summary,
            "authors": [author.name for author in xml.entries[0].authors],
            "title": xml.entries[0].title,
            "id": xml.entries[0].id,
            "doi": None,
        },
        indent=4, sort_keys=True,
    )


def fetch(url, id):
    """ Fetch content from url."""
    resp = requests.get(url.format(id=id))
    return _test_response(resp).content


def write_to_file(data, transform, filename):
    """ Writes data to a file.

    If the file/directory does not exist, creates it. Otherwise, write to the file.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as fout:
        for d in data:
            fout.write(transform(d))


def _test_response(resp):
    """ Checks the response is not None."""
    if resp is None:
        raise RuntimeError("Query came back null. Check the DOI.")
    if resp.status_code == 429:
        print("We're being rate limited. Please reduce the call rate.")
        exit(1)
    return resp


def _test_dois(dois):
    """ Tests that all DOIs are valid.

    Make sure DOI is not None or "".
    """
    if not all(doi for doi in dois):
        raise RuntimeError
    return dois


# Global entries for data sources
SOURCES = {
    "ss": {
        "url": "http://api.semanticscholar.org/v1/paper/{id}",
        "parser": ss_parse
    },
    "arxiv": {
        "url": "https://export.arxiv.org/api/query?search_query={id}",
        "parser": ar_parse,
    },
}


def main(args):
    """ Handle inputs, fetch the data, process, and write to file.

    Determine if the request is for Semantic Scholar or for arXiv. Based on this,
    make the appropriate queries, sanitize the data, and then write it to a file.
    """
    data = [fetch(SOURCES[args.source]["url"], doi) for doi in _test_dois(args.doi)]
    parser = SOURCES[args.source]["parser"] if not args.raw else lambda c: str(c)
    write_to_file(data, parser, args.dump_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        default=None,
        required=True,
        choices=["arxiv", "ss"],
        help="Either 'arxiv' or 'ss'.",
    )
    parser.add_argument("--raw", action="store_true", help="Leave the data unparsed.")
    parser.add_argument(
        "--dump_path", default="data/temp.json", help="Location to dump results data."
    )
    parser.add_argument("doi", default=None, nargs="+", help="Publication identifiers")

    args = parser.parse_args()
    main(args)
