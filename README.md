# Website Technologies Scraper

A Python tool being developed to identify technologies used by websites
and provide evidence for each detection.

Built for the Veridion internship challenge.

## Current progress

- Prepared an initial script to request a single web page.
- The script prints the HTTP status, final URL, content type,
  and first 500 characters of the HTML response.
- Added a parser that extracts `src` attributes from HTML `<script>` tags.
- The parser currently analyzes `sample_html`, a controlled HTML example.
- Relative script references are resolved with `urllib.parse.urljoin`.
- Added the first exact-URL detection rule for jQuery, with script URL evidence.
- The user's terminal run confirmed page fetching and the expected sample detection.

Technology detection is currently limited to one known jQuery script URL
in the sample. Detection on the challenge domains is not implemented yet.

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
6. Prints absolute script URLs using the final page URL as the base.
7. Checks original script references against one exact jQuery URL and prints
   the technology name and matching URL as evidence.

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
Original references remain in the list; a separate loop prints absolute URLs.

In `main.py`, `parser.feed(sample_html)` analyzes the controlled example.
The actual sample also includes the jQuery script shown below.
The earlier network request still executes first, so a request error can
prevent the sample test from running.

An empty list means that the supplied HTML contained no script tags with
non-empty `src` attributes. It does not prove that the website uses no
JavaScript or other technologies.

Script sources can later provide evidence for identifying technologies,
but a generic filename such as `analytics.js` does not identify a specific
analytics product. Detection rules need recognizable, specific signals.

### Resolving script URLs

`final_url = response.url` records the page URL after redirects.
`urljoin(final_url, source)` builds a complete URL from each script reference.
For a base of `https://example.com`, `/assets/app.js` becomes
`https://example.com/assets/app.js`. Already absolute URLs remain unchanged.
This constructs addresses without downloading or validating script files.

### First technology detection: jQuery

The controlled sample contains:

```html
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
```

The first rule uses an exact string comparison:

```python
for source in parser.script_sources:
    if source == "https://code.jquery.com/jquery-3.7.1.min.js":
        print("Tehnologie identificată: jQuery")
        print("Dovadă:", source)
```

The loop checks each extracted `src`. When a reference matches the known
URL, it prints the technology and the matching reference as evidence.
This connects a detection to an observable HTML signal.

The user's terminal output confirmed the expected result:

```text
Tehnologie identificată: jQuery
Dovadă: https://code.jquery.com/jquery-3.7.1.min.js
```

This confirms the rule works on `sample_html`; it does not establish that
`example.com` uses jQuery. The rule recognizes only this exact URL, so other
versions, hosts, relative references or query strings will not match.
It detects a script reference, not successful loading or execution of jQuery.
Results are currently printed, not stored as structured records.

## Current limitations

- Uses one hardcoded URL.
- Assumes the response is UTF-8.
- Does not execute JavaScript or observe dynamically inserted scripts.
- Ignores inline script content.
- Does not account for HTML `<base href>` when resolving relative URLs.
- Does not yet handle request errors explicitly.
- Detects only one exact jQuery URL in the controlled sample.
- Does not save results or analyze the challenge dataset yet.

## Next steps

- Store each detection and its evidence in a structured record.
- Save the detection and its evidence as JSON.
- Inspect a domain from the challenge dataset and evaluate detection on real HTML.
- Expand detection rules to cover additional verified signals.

## Development notes

### Initial approach

Start with one page and inspect the information available in an HTTP
response before adding detection rules or browser automation.

The first experiment uses Python's standard library to keep setup simple.
Further tools will be chosen based on observed needs.
