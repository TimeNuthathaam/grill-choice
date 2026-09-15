---
name: grill-choice
description: Help a user think through a plan, strategy, product, project, or major decision by asking only the highest-priority unresolved questions in rounds, then presenting concrete options in a local interactive HTML page where they can accept, reject, or comment. Use whenever the user asks to be challenged on an idea, plan, decision, requirements, priorities, trade-offs, or wants an easy way to choose among recommendations. All user-facing language must stay at or below Thai Grade 9 (ม.3), with short, simple examples when helpful.
---

# Grill Choice

Turn vague plans into decisions the user can make confidently. Keep all user-facing language at or below Thai Grade 9 (ม.3). This is a ceiling, not a target to exceed.

This skill includes the HTML workflow, template, and local server. Use the bundled files below; no separate `html-choice` installation or invocation is needed.

## ภาษาไม่เกินระดับ ม.3

ใช้กติกานี้กับคำถาม คำแนะนำ การ์ด HTML ปุ่ม และสรุปคำตอบทุกครั้ง:

- ใช้คำไทยที่พบในชีวิตประจำวัน ประโยคสั้น และบอกทีละเรื่อง
- ไม่สมมติว่าผู้ใช้รู้เรื่องธุรกิจ เทคโนโลยี หรือคำเฉพาะมาก่อน
- เปลี่ยนศัพท์ยากเป็นคำง่าย เช่น “ลีด” → “คนที่สนใจและทักมาถาม” ถ้าต้องใช้ชื่อเฉพาะ ให้บอกความหมายง่ายๆ ทันที
- บอกตรงๆ ว่าจะทำอะไร แล้วผู้ใช้จะเห็นอะไรเปลี่ยนไป ใช้ชื่อคนหรือสิ่งของให้ชัด
- ถ้าเรื่องยังนึกภาพยาก ให้แทรกตัวอย่างใกล้ตัวสั้นๆ หนึ่งตัวอย่าง ไม่ต้องใส่ทุกข้อ
- ตัวเลขที่สมมติขึ้นต้องบอกว่าเป็นตัวอย่าง อย่าเขียนเหมือนเป็นผลที่เกิดขึ้นจริง
- ก่อนส่ง ลองอ่านในมุมคนที่เพิ่งรู้เรื่องนี้ ถ้ายังต้องเดาความหมาย ให้เขียนใหม่ด้วยคำที่ง่ายกว่า โดยเก็บข้อเท็จจริงและข้อควรรู้ไว้ครบ

ตัวอย่าง:

> ❌ “กำหนด KPI เพื่อวัด Conversion ของลีด”
> ✅ “อยากนับว่ามีคนทักแล้วจองกี่คนไหม? ตัวอย่างสมมติ: มีคนทัก 10 คน แล้วจอง 2 คน”

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

Use this exact question shape. Keep every part easy to understand:

```
❓ **Q1 — <short title>**: <one focused question>
➡️ แนะนำ: <recommended answer and one short reason>
---
```

Keep questions specific. For example, ask “อยากให้คนที่เข้าหน้าเว็บทักมาถามก่อน หรือกดซื้อได้เลย?” before asking where to place ads or what the posts should say.

## Choice-page mode

Use a local page when the user would benefit from clicking through choices instead of parsing a long chat response.

### Write the decision cards

Create one card per independently selectable decision.

- Title: a short, natural Thai question.
- Body: no more than three short lines. Explain what changes if the user chooses it.
- Optional fields: `url` for a source/article, `img` for an image URL, `html` for safe already-prepared rich content.
- Do not put two decisions in one card. Split alternatives, optional features, and priorities into separate cards.
- Every card always has exactly these actions: `✅ เอาตามนี้`, `❌ ไม่เอาข้อนี้`, `✏️ ขอแก้` plus a comment box. Clicking `✏️ ขอแก้` must focus the comment box immediately.
- Lead with the recommendation, not a catalogue of possibilities. Use the page to collect a decision, not to dump research.

The Copy button must try the Clipboard API, then `execCommand`. If both fail, show a pre-selected text box for manual copying. Preserve all three paths when adapting the template.

### Generate and open the page

Read the bundled [references/choice-template.html](references/choice-template.html) before generating a page. It supplies the mobile layout, saved answers, and copy fallback. Resolve bundled paths from this skill's directory; the example below uses the default `~/.codex/skills/grill-choice` installation.

1. Create an archive directory:

```bash
mkdir -p "$HOME/Downloads/html-choice"
```

2. Prepare the decision cards as a JSON array. Example:

```json
[
  {
    "title": "เริ่มจากกลุ่มลูกค้าหลักกลุ่มเดียวไหม?",
    "body": "เริ่มจากลูกค้ากลุ่มเดียวก่อน จะเขียนให้ตรงใจได้ง่ายขึ้น\nตัวอย่าง: ทำโพสต์สำหรับคนที่เพิ่งรู้จักร้าน",
    "url": ""
  }
]
```

3. Render a named page and `latest.html` using a short Python invocation. Substitute the cards and title for this session. Escape the title for HTML and serialize JavaScript values with `json.dumps`, escaping `<` so card text cannot close the script tag. Keep `url` and `img` to trusted HTTP(S) URLs; only use `html` for trusted, prepared markup.

```bash
python3 - <<'PY'
import json, re
from datetime import datetime
from html import escape
from pathlib import Path

skill_dir = Path.home() / '.codex' / 'skills' / 'grill-choice'
archive = Path.home() / 'Downloads' / 'html-choice'
archive.mkdir(parents=True, exist_ok=True)
points = [
    {"title": "เริ่มจากกลุ่มลูกค้าหลักกลุ่มเดียวไหม?", "body": "เริ่มจากลูกค้ากลุ่มเดียวก่อน จะเขียนให้ตรงใจได้ง่ายขึ้น\nตัวอย่าง: ทำโพสต์สำหรับคนที่เพิ่งรู้จักร้าน"}
]
title = 'ตัดสินใจเรื่องแผนคอนเทนต์'
page_key = f"{datetime.now():%Y%m%d-%H%M%S-%f}-{re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-') or 'choice'}"
template = skill_dir / 'references' / 'choice-template.html'
values = {
    '__TITLE__': escape(title),
    '__POINTS_JSON__': json.dumps(points, ensure_ascii=False).replace('<', r'\u003c'),
    '__PAGE_KEY__': json.dumps(page_key),
}
html = re.sub(r'__(?:TITLE|POINTS_JSON|PAGE_KEY)__', lambda m: values[m.group()], template.read_text('utf-8'))
(archive / f'{page_key}.html').write_text(html, encoding='utf-8')
(archive / 'latest.html').write_text(html, encoding='utf-8')
print(f'http://127.0.0.1:8767/{page_key}.html')
PY
```

4. Start the bundled local-only service and open the resulting URL in the browser:

```bash
python3 "$HOME/.codex/skills/grill-choice/scripts/ensure-choice-service.py" "$HOME/Downloads/html-choice" 8767
```

Open `http://127.0.0.1:8767/<page-key>.html`. The page saves responses beside the HTML as `<page-key>.state.json`; read that file after the user says they have finished. Tell the user in simple Thai: “กดเลือกทีละข้อ แล้วกด ‘คัดลอกคำตอบ’ นำมาวางในแชทได้เลย”

Use port **8767** and the shared `~/Downloads/html-choice/` archive. Keep each named page and its state; only `latest.html` and the root URL change to the newest page. The HTML has no CDN or external font dependency. Optional remote images and links still need network access.

### Bundled files

| Path | Purpose |
|---|---|
| [references/choice-template.html](references/choice-template.html) | Mobile cards, comments, saved answers, and Copy fallbacks |
| [scripts/choice-server.py](scripts/choice-server.py) | Local page hosting and GET/POST `/state` |
| [scripts/ensure-choice-service.py](scripts/ensure-choice-service.py) | Starts the local server when port 8767 is free |
| [scripts/check-choice.py](scripts/check-choice.py) | Run with `python3` to check standalone rendering and saved answers |

## After the user responds

Translate every accepted, rejected, and commented card into the next concrete action. If a comment creates a new unresolved prerequisite, return to interview mode and ask only the newly exposed frontier questions. Do not silently treat a comment as approval.

## Boundaries

- The server binds only to `127.0.0.1`; do not expose the page to a LAN or the public internet unless the user explicitly requests that separately.
- Keep the choice page as a decision aid, not a replacement for a discussion where safety, consent, budgets, or irreversible commitments are at stake.
