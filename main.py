from urllib.request import urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser

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

url = "https://example.com"



with urlopen(url, timeout=15) as response:
    final_url = response.url
    html = response.read().decode("utf-8")

    print("Status HTTP:", response.status)
    print("URL final:", response.url)
    print("Tip conținut:", response.headers.get("Content-Type"))
    print("Primele 500 de caractere:")
    print(html[:500])



sample_html = """
<html>
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="/assets/app.js"></script>
    <script src="https://cdn.example.com/analytics.js"></script>
    <script>console.log("inline script");</script>
</html>
"""

parser = ScriptParser()
parser.feed(sample_html)

print("Scripturi găsite:", parser.script_sources)

for source in parser.script_sources:
    full_url = urljoin(final_url, source)
    print("Adresă completă:", full_url)


for source in parser.script_sources:
    if source == "https://code.jquery.com/jquery-3.7.1.min.js":
        print("Tehnologie identificată: jQuery")
        print("Dovadă:", source)