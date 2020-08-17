# Fetching paper abstracts for downstream NLP

## Dependencies

Target language is Python `3.7` and requires only one library:

```bash
pip install feedparser
```

## How to Run

All of the possible configurations {arXiv, Semantic Scholar} and {DOI, DOIs} are shown below.

Run the script with one, or multiple IDs/DOIs and choose Semantic Scholar or arXiv:

```bash
python scripts/fetch_abs.py --source=ss "10.32470/CCN.2018.1154-0"  # Use DOI
python scripts/fetch_abs.py --source=arxiv "1808.01058"  # Use arXiv ID
```

For multiple IDs just include multiple quote strings.

To change the file location for the data to be sent:

```bash
python scripts/fetch_abs.py --dump_path=<x>/<y> --source=ss "10.1126/science.aag2612"
```

To output the raw data:

```bash
python scripts/fetch_abs.py --raw --source=arxiv "1511.00787"
```

Otherwise, only write out the following to the file:

* Abstract
* Title
* DOI / arXivID
* Authors

## Methodology

This script only uses basic Python modules and not 3rd party/external libraries (save FeedParser because dealing with XML is a pain). I have provided basic unit tests to ensure that the responses from the API are not null, and that there is no rate limiting. Further unit testing might be conducted in a similar, atomic fashion.

The script supports some edge cases: like the file/directory not already existing, writing over old data, or null DOIs, but further testing would certainly make this more robust.
