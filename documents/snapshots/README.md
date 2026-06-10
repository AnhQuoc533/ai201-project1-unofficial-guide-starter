# Local snapshots (ingestion fallback)

Some sources in the Documents table cannot be scraped reliably from every
environment:

- **JavaScript single-page apps** (e.g. `gomason.com` athletics, `mason360.gmu.edu`)
  render their content client-side, so a plain HTTP fetch returns an empty
  shell or an ad-blocker page — no real text.
- **WAF / bot-blocked hosts** (e.g. `reddit.com`, `fairfaxva.gov`) return
  `403 Forbidden` to non-browser / datacenter traffic.

`ingest.py` handles this with a **snapshot fallback**: each source may declare a
`snapshot` filename. When the live fetch fails or returns unusable content
(too short, an ad-block page, or only template placeholders), the loader reads
the matching `.txt` file from this folder instead.

## How to add a snapshot

1. Open the source URL in your own browser.
2. Select the main content (the article / post / schedule — not the nav or
   footer), copy it, and paste it into the matching file below as plain text.
3. Re-run `python ingest.py`. The loader will pick it up automatically.

| Source # | URL | Snapshot file | Status |
|----------|-----|---------------|--------|
| 2 | reddit.com r/EngineeringStudents thread | `02-reddit.txt` | needs paste from browser |
| 7 | gomason.com free admission | `07-athletics.txt` | ✅ captured |
| 9 | fairfaxva.gov CUE Bus | `09-cue-bus.txt` | needs paste from browser |
| 10 | mason360.gmu.edu events | `10-mason360.txt` | needs paste from browser |

Snapshots are committed so the indexing run is reproducible even after the live
pages change.
