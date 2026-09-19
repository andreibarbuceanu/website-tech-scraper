# Website Technologies Scraper

A Python tool being developed to identify technologies used by websites
and provide evidence for each detection.

Built for the Veridion internship challenge.

## Current progress

- Prepared an initial script to request a single web page.
- The script prints the HTTP status, final URL, content type,
  and first 500 characters of the HTML response.
- Added a parser that extracts `src` attributes from HTML `<script>` tags.
- The parser now analyzes the downloaded page HTML with `parser.feed(html)`.
- Relative script references are resolved with `urllib.parse.urljoin`.
- Added the first exact-URL detection rule for jQuery, with script URL evidence.
- Stores detections as dictionaries in a `detections` list.
- Exports `source_type`, `url`, `status`, and `technologies` to `results.json`.
- Catches `URLError`, saves its reason in an `error` field, and exits with code 1.
- Handles `HTTPError` separately to also save the numeric `http_status`.
- Verified jQuery detection earlier with a controlled HTML example.
- An earlier user run fetched `example.com` successfully (HTTP 200) and found
  no external script references or matching technologies in the returned HTML.
- An earlier run attempted `jcmobilecigars.com` from the challenge list and
  recorded a certificate verification failure in JSON.
- The latest saved result for `somalidisablesupport.com` records HTTP 406,
  `Not Acceptable`; the exact reason for the server response is not established.

Technology detection is currently limited to one known jQuery script URL.
Two challenge domains have been attempted; batch processing is not implemented.

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

Run from the project folder. The current script requests https://somalidisablesupport.com
and checks its downloaded HTML for the known jQuery script URL. It writes `results.json` in the
current working directory, replacing any existing file with that name.

## How it currently works

1. Sends an HTTP request using Python's built-in `urllib.request`.
2. Reads the response body and decodes it as UTF-8.
3. Prints response metadata and an HTML preview.
4. Passes the downloaded `html` to `ScriptParser`, based on `HTMLParser`.
5. Collects and prints the non-empty `src` attributes of script tags.
6. Prints absolute script URLs using the final page URL as the base.
7. Checks original script references against one exact jQuery URL and adds
   a structured detection to the `detections` list.
8. Prints the list and wraps it in a `result` dictionary with source metadata.
9. Saves `result` to `results.json`.

If the request raises `URLError`, the script instead saves an error result
and exits before parsing. See the error-handling section below.

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

In `main.py`, `parser.feed(html)` analyzes the downloaded page.
The earlier `sample_html` fixture has been removed from the script; its
jQuery example is documented below. A caught request error is exported
before the program exits without parsing.

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
        detection = {
            "technology": "jQuery",
            "evidence_type": "script_src",
            "evidence": source
        }
        detections.append(detection)
```

The loop checks each extracted `src`. When a reference matches the known
URL, it stores the technology and the matching reference as evidence.
The list is initialized with `detections = []` before the loop.
This connects a detection to an observable HTML signal.

During the earlier controlled sample test, the user's terminal output
confirmed a list containing the expected record:

```json
[
    {
        "technology": "jQuery",
        "evidence_type": "script_src",
        "evidence": "https://code.jquery.com/jquery-3.7.1.min.js"
    }
]
```

This confirms the rule works on `sample_html`; it does not establish that
`example.com` uses jQuery. The rule recognizes only this exact URL, so other
versions, hosts, relative references or query strings will not match.
It detects a script reference, not successful loading or execution of jQuery.

### Structured results and JSON output

Each detection is a Python dictionary with three fields:

- `technology`: the identified technology name.
- `evidence_type`: the source of the signal; `script_src` means a script's `src` attribute.
- `evidence`: the actual script reference that matched the rule.

`detections.append(detection)` adds the dictionary to the list. If no script
matches, the list remains empty and the exported object's `technologies`
field is `[]`.

The detections are wrapped in a dictionary identifying the analyzed source:

```python
result = {
    "source_type": "website",
    "url": final_url,
    "status": "success",
    "technologies": detections
}
```

`source_type` labels this as a website analysis. `url` identifies the final
page URL after redirects. `status: success` indicates completed analysis,
not necessarily a technology match. `technologies` contains the detection dictionaries
derived from that page's downloaded HTML.

The standard-library `json` module saves this result object:

```python
with open("results.json", "w", encoding="utf-8") as file:
    json.dump(result, file, ensure_ascii=False, indent=4)
```

`w` creates the file or overwrites its previous contents. UTF-8 and
`ensure_ascii=False` preserve readable Unicode characters; `indent=4`
formats the output for readability. The `with` block closes the file
automatically. Unlike the in-memory list, the saved file remains after the
program exits.

For a successful analysis with no detections, the output has this format:

```json
{
    "source_type": "website",
    "url": "https://example.com",
    "status": "success",
    "technologies": []
}
```

The earlier `example.com` run returned HTTP 200, an empty script-source list,
and no detections. On success, an empty `technologies` list means the current rule found
no match; it does not establish that the website uses no technologies.
This is a single-page result, not a completed output for the challenge dataset.

The obsolete list-only JSON write has been removed. The script now writes
the `result` object once on either success or a caught `URLError`.

### Request errors and failure output

The HTTP request and response reading are inside a `try` block. The handlers
are checked in this order:

1. `except HTTPError as error`: handles HTTP error responses and records
   `error.code` as `http_status`, plus `str(error.reason)` as `error`.
2. `except URLError as error`: handles other URL errors, such as DNS,
   connection or certificate verification failures, and records the reason.

`HTTPError` is a subclass of `URLError`, so it must come first to preserve
the separate HTTP handling. Python executes only the first matching handler.
An HTTP code describes the response but does not identify or resolve its
underlying cause.

For a non-HTTP `URLError`, the result is built as follows:

```python
result = {
    "source_type": "website",
    "url": url,
    "status": "error",
    "error": str(error.reason),
    "technologies": []
}
```

On failure, `url` is the requested address because a final response URL
may not be available. `str(error.reason)` converts the reason to text
that can be serialized as JSON. After writing this result, the script
calls `raise SystemExit(1)` to stop with a failure exit code. Parsing and
the success-output block do not run.

The inspected `results.json` contains the latest failed attempt:

```json
{
    "source_type": "website",
    "url": "https://somalidisablesupport.com",
    "status": "error",
    "http_status": 406,
    "error": "Not Acceptable",
    "technologies": []
}
```

The earlier certificate problem on `jcmobilecigars.com` remains unresolved and HTTPS certificate verification
remains enabled. The error alone does not establish whether the cause is
the website, a network intermediary, or the local trust configuration.

With `status: error`, the empty technology list means analysis could not
be completed, unlike a successful analysis with no matches. Saving the
failure replaces the previous run's result rather than leaving stale data.
Errors outside the current handler can still interrupt the program without
updating the output.

### Why there are three JSON-writing blocks

There is a save block for HTTP errors, another for other URL errors, and
one for successful analysis. Only one is reached per run on these paths:
each error handler saves its result and calls `SystemExit(1)`, so execution
cannot reach the success save afterward. On success, neither error handler
runs. This differs from the earlier obsolete code that wrote two results
sequentially in the same run.

The repeated writing code can later be moved to a shared function or a
single common save step. That refactoring has not been implemented yet.

## Current limitations

- Uses one hardcoded URL.
- Assumes the response is UTF-8.
- Does not execute JavaScript or observe dynamically inserted scripts.
- Ignores inline script content.
- Does not account for HTML `<base href>` when resolving relative URLs.
- Handles `HTTPError` and `URLError`, but not all failures (for example, direct timeouts,
  decoding errors, or file-write errors).
- Detects only one exact jQuery URL in the downloaded HTML.
- Detection compares original script references, not the absolute URLs printed earlier.
- Overwrites the output on each run and does not handle file-write errors explicitly.
- Processes only one hardcoded URL, not the full challenge dataset.

## Next steps

- Obtain a successful fetch from a challenge domain and inspect its script references.
- Expand detection rules to cover additional verified signals.
- Extend error handling and later process multiple domains with per-domain results.
- Refactor repeated JSON-writing code into a shared save operation.

## Development notes

### Initial approach

Start with one page and inspect the information available in an HTTP
response before adding detection rules or browser automation.

The first experiment uses Python's standard library to keep setup simple.
Further tools will be chosen based on observed needs.
