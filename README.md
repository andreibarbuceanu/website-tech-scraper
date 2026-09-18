# Website Technologies Scraper

A Python tool being developed to identify technologies used by websites
and provide evidence for each detection.

Built for the Veridion internship challenge.

## Current progress

- Created and activated a Python virtual environment.
- Prepared an initial script to request a single web page.
- The script prints the HTTP status, final URL, content type,
  and first 500 characters of the HTML response.
- First successful request: pending verification.

Technology detection is not implemented yet.

## Requirements

- Python 3.14.6 is used locally.
- No third-party dependencies at this stage.

## Setup

Create a virtual environment:

    python3 -m venv .venv

Activate it on macOS/Linux:

    source .venv/bin/activate

## Run

    python main.py

The initial script requests https://example.com.

## How it currently works

1. Sends an HTTP request using Python's built-in urllib.request.
2. Reads the response body and decodes it as UTF-8.
3. Prints response metadata and an HTML preview.

## Current limitations

- Uses one hardcoded URL.
- Assumes the response is UTF-8.
- Does not execute JavaScript.
- Does not yet handle request errors explicitly.
- Does not detect technologies or save results.

## Next steps

- Verify the first request.
- Inspect a domain from the challenge dataset.
- Identify a technology using a clear, observable signal.
- Save the detection and its evidence as JSON.

## Development notes

### Initial approach

Start with one page and inspect the information available in an HTTP
response before adding detection rules or browser automation.

The first experiment uses Python's standard library to keep setup simple.
Further tools will be chosen based on observed needs.
