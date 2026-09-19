import json
from urllib.request import urlopen, Request
from urllib.parse import urljoin
from html.parser import HTMLParser
from urllib.error import URLError, HTTPError


class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.script_sources: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            attributes = dict(attrs)
            source = attributes.get("src")

            if source:
                self.script_sources.append(source)



def analyze_website(url):
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    try:
        with urlopen(request, timeout=15) as response:
            final_url = response.url
            html = response.read().decode("utf-8")

            print("Status HTTP:", response.status)
            print("URL final:", final_url)

    except HTTPError as error:
        return {
            "source_type": "website",
            "url": url,
            "status": "error",
            "http_status": error.code,
            "error": str(error.reason),
            "technologies": []
        }

    except URLError as error:
        return {
            "source_type": "website",
            "url": url,
            "status": "error",
            "error": str(error.reason),
            "technologies": []
        }

    parser = ScriptParser()
    parser.feed(html)

    print("Scripturi găsite:", parser.script_sources)

    for source in parser.script_sources:
        full_url = urljoin(final_url, source)
        print("Adresă completă:", full_url)

    detections = []

    for source in parser.script_sources:
        if source == "https://code.jquery.com/jquery-3.7.1.min.js":
            detection = {
                "technology": "jQuery",
                "evidence_type": "script_src",
                "evidence": source
            }

            detections.append(detection)

    return {
        "source_type": "website",
        "url": final_url,
        "status": "success",
        "technologies": detections
    }


url = "https://somalidisablesupport.com"
result = analyze_website(url)

print("Rezultat:", result)

with open("results.json", "w", encoding="utf-8") as file:
    json.dump(result, file, ensure_ascii=False, indent=4)