# Website Technologies Scraper

A Python tool being developed to identify technologies used by websites
and provide evidence for each detection.

Built for the Veridion internship challenge.

## Current progress

- Prepared an initial script to request a single web page.
- The script prints the HTTP status, final URL, content type,
  and first 500 characters of the HTML response.
- Added a parser that extracts `src` attributes from HTML `<script>` tags.
- The current parser analyzes the included sample HTML snippet.
- Successful live fetching and technology detection still need verification.

Technology detection is not implemented yet. Extracting script sources
collects potential evidence for future detection rules.

## Requirements

- Python 3.
- No third-party dependencies for the current `main.py`.

## Setup

Create a virtual environment:

```sh
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```sh
source .venv/bin/activate
```

## Run

```sh
python main.py
```

The current script requests https://example.com.

## How it currently works

1. Sends an HTTP request using Python's built-in `urllib.request`.
2. Reads the response body and decodes it as UTF-8.
3. Prints response metadata and an HTML preview.
4. Passes `sample_html` to `ScriptParser`, based on `HTMLParser`.
5. Collects and prints the non-empty `src` attributes of script tags.

### Extracting script sources

Consider this HTML:

```html
<script src="/assets/app.js"></script>
<script src="https://cdn.example.com/analytics.js"></script>
<script>console.log("inline script");</script>
```

The first two tags reference separate script files. The third contains
inline JavaScript and has no `src` attribute.

`ScriptParser` inherits from `HTMLParser`, which handles reading HTML tags.
Its constructor calls `super().__init__()` to initialize the base parser
and creates an empty `script_sources` list for each parser instance.

When `parser.feed(html)` runs, the parser calls `handle_starttag(tag, attrs)`
for each opening tag it encounters. Our method:

1. Checks whether the tag is `script`.
2. Converts the list of attribute pairs into a dictionary with `dict(attrs)`.
3. Retrieves the `src` attribute using `.get("src")`.
4. Appends the value to `script_sources` if it is non-empty.

For the sample above, the expected list is:

```python
['/assets/app.js', 'https://cdn.example.com/analytics.js']
```

The parser does not execute JavaScript or download the script files.
It only extracts their references from the supplied HTML.
`/assets/app.js` is a relative reference and is currently kept unchanged.

In `main.py`, the code currently calls `parser.feed(sample_html)` to check
extraction against a known example. To analyze the downloaded page, use
`parser.feed(html)` instead. The network request still runs before the
sample test, so a request error can prevent the test from running.

An empty list means that the supplied HTML contained no script tags with
non-empty `src` attributes. It does not prove that the website uses no
JavaScript or other technologies.

Script sources can later provide evidence for identifying technologies,
but a generic filename such as `analytics.js` does not identify a specific
analytics product. Detection rules need recognizable, specific signals.

## Current limitations

- Uses one hardcoded URL.
- Assumes the response is UTF-8.
- Does not execute JavaScript or observe dynamically inserted scripts.
- Ignores inline script content.
- Keeps script references as written, without resolving relative URLs.
- Does not yet handle request errors explicitly.
- Does not detect technologies or save results.

## Next steps

- Verify script extraction using the sample HTML.
- Verify fetching and inspect a domain from the challenge dataset.
- Identify a technology using a clear, observable signal.
- Save the detection and its evidence as JSON.

## Development notes

### Initial approach

Start with one page and inspect the information available in an HTTP
response before adding detection rules or browser automation.

The first experiment uses Python's standard library to keep setup simple.
Further tools will be chosen based on observed needs.
