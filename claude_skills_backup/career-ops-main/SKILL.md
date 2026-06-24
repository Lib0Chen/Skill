---
name: career-ops-main
description: "AI-powered job search pipeline: portal scanning, application tracking, offer evaluation, CV generation, and batch processing. Designed for job seekers who want systematic career ops management."
---

# Career-Ops

Read `CLAUDE.md` in this directory for the full system documentation.

**Key capabilities:**
- `portals.yml` — configure job portals to scan
- `data/applications.md` — application tracker
- `data/pipeline.md` — inbox of pending URLs
- `scan.mjs` — zero-token portal scanner (Greenhouse/Ashby/Lever APIs)
- `generate-pdf.mjs` / `generate-latex.mjs` — CV generation
- `analyze-patterns.mjs` — pattern analysis
- `interview-prep/` — company-specific interview intel

**Quickstart:** Read `CLAUDE.md` → check `portals.yml` → run `node scan.mjs`
