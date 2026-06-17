import json

with open('dom_analysis.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('summarize_dom.txt', 'w', encoding='utf-8') as out:
    for site, items in data.items():
        out.write(f"--- {site.upper()} ---\n")
        if not items:
            out.write("  NO ITEMS\n")
            continue
        for item in items[:3]:
            out.write(f"  Class: {item.get('className')}\n")
            out.write(f"  ParentClass: {item.get('parentClass')}\n")
            text = item.get('text', '').replace('\n', ' ')[:100]
            out.write(f"  Text: {text}\n")
