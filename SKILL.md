---
name: grill-choice
description: Help a user think through a plan, strategy, product, project, or major decision by asking only the highest-priority unresolved questions in rounds, then presenting concrete options in a local interactive HTML page where they can accept, reject, or comment. Use whenever the user asks to be challenged on an idea, plan, decision, requirements, priorities, trade-offs, or wants an easy way to choose among recommendations.
---

# Grill Choice

Turn vague plans into decisions the user can make confidently. This skill is self-contained: do not require another skill to interview the user or generate the choice page.

## Choose the right mode

- Use **interview mode** when key decisions are still unknown. Ask questions before proposing downstream work.
- Use **choice-page mode** when there are several concrete recommendations, alternatives, priorities, or revisions the user should select from. It can follow an interview round or be used immediately when the facts are already clear.
- If the user only needs a simple answer, reply normally. Do not manufacture an interview or HTML page.

## Interview mode

Build a private decision tree. A decision is ready only when the decisions it depends on are settled. The current **frontier** is every ready but unresolved decision.

1. Work in rounds. In each round, ask every question on the current frontier and nothing downstream.
2. State verified facts yourself. Ask the user only for choices, preferences, constraints, or goals that only they can decide.
3. Give a recommended answer for every question, so answering is low effort.
4. Wait for the user's answers. Then update the decision tree and ask the next frontier. Never assume a skipped choice is settled.
5. Finish when the frontier is empty. Summarize the resulting plan and ask for confirmation before carrying it out.

Use this exact question shape:

```
❓ **Q1 — <short title>**: <one focused question>
➡️ แนะนำ: <recommended answer and one short reason>
---
```

Keep questions specific. For example, ask “เป้าหมายหลักของหน้าแรกคือเก็บลีดหรือปิดการขายทันที?” before asking about ad channels or copy variants.

## Choice-page mode

Use a local page when the user would benefit from clicking through choices instead of parsing a long chat response.

### Write the decision cards

Create one card per independently selectable decision.

- Title: a short, natural Thai question.
- Body: no more than three short lines. Explain what changes if the user chooses it.
- Optional fields: `url` for a source/article, `img` for an image URL, `html` for safe already-prepared rich content.
- Do not put two decisions in one card. Split alternatives, optional features, and priorities into separate cards.
- Every card always has exactly these actions: `✅ เอาตามนี้`, `❌ ไม่เอาข้อนี้`, `✏️ ขอแก้` plus a comment box.
- Lead with the recommendation, not a catalogue of possibilities. Use the page to collect a decision, not to dump research.

### Generate and open the page

Read the bundled template at `references/choice-template.html` before generating a page. It supplies mobile layout, persistent choices, and clipboard fallback.

1. Create an archive directory:

```bash
mkdir -p "$HOME/Downloads/grill-choice"
```

2. Prepare the decision cards as a JSON array. Example:

```json
[
  {
    "title": "เริ่มจากกลุ่มลูกค้าหลักกลุ่มเดียวไหม?",
    "body": "โฟกัสกลุ่มเดียวก่อนทำให้ข้อความคมและวัดผลได้ง่ายขึ้น",
    "url": ""
  }
]
```

3. Render `latest.html` using a short Python invocation. Substitute the JSON, title, and page key with values for this session. Escape user-provided text through `json.dumps`; never interpolate raw text into JavaScript.

```bash
python3 - <<'PY'
import json
from pathlib import Path

skill_dir = Path.home() / '.codex' / 'skills' / 'grill-choice'
archive = Path.home() / 'Downloads' / 'grill-choice'
points = [
    {"title": "เริ่มจากกลุ่มลูกค้าหลักกลุ่มเดียวไหม?", "body": "โฟกัสกลุ่มเดียวก่อนทำให้ข้อความคมและวัดผลได้ง่ายขึ้น"}
]
html = (skill_dir / 'references' / 'choice-template.html').read_text('utf-8')
html = html.replace('__TITLE__', 'ตัดสินใจเรื่องแผนคอนเทนต์')
html = html.replace('__POINTS_JSON__', json.dumps(points, ensure_ascii=False))
html = html.replace('__PAGE_KEY__', json.dumps('content-plan-01'))
(archive / 'latest.html').write_text(html, encoding='utf-8')
PY
```

4. Start the bundled local-only service and open the resulting URL in the browser:

```bash
python3 "$HOME/.codex/skills/grill-choice/scripts/ensure-choice-service.py" "$HOME/Downloads/grill-choice" 8767
```

Open `http://127.0.0.1:8767/`. The page saves responses beside the HTML as `<page-key>.state.json`; read that file after the user says they have finished.

## After the user responds

Translate every accepted, rejected, and commented card into the next concrete action. If a comment creates a new unresolved prerequisite, return to interview mode and ask only the newly exposed frontier questions. Do not silently treat a comment as approval.

## Boundaries

- The server binds only to `127.0.0.1`; do not expose the page to a LAN or the public internet unless the user explicitly requests that separately.
- Keep the choice page as a decision aid, not a replacement for a discussion where safety, consent, budgets, or irreversible commitments are at stake.
