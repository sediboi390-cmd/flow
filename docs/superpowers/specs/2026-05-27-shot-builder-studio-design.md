# Shot Builder Studio — Design Spec
**Date:** 2026-05-27  
**Status:** Approved  
**Target file:** `storyboard/index.html` (replaces existing storyboard)

---

## 1. Overview

**Shot Builder Studio** is a fully interactive, browser-based storyboard builder for faceless content creators. It allows creators to plan YouTube explainers, TikTok/Shorts, cinematic sequences, tutorials, and ad/promo videos by building storyboard panels using one of four creation modes.

It ships as a single self-contained HTML file (`storyboard/index.html`), replacing the existing static fight-scene storyboard. It requires no build tools, no server, and no dependencies beyond two Google Fonts (Inter + DM Sans) and JSZip (all CDN).

**Visual aesthetic:** Calm, minimalist design — warm off-white backgrounds, white card surfaces, soft warm borders, and a muted accent palette chosen for low eye-strain and long creative sessions. See Section 11 for the full design system.

> **Design revision note (2026-05-27):** Original dark cinematic theme was replaced with a calm minimalist palette following user feedback. The new design prioritises readability and visual comfort over dramatic atmosphere.

---

## 2. Architecture

### Layout

```
┌─────────────────────────────────────────────────────┐
│  HEADER — Shot Builder Studio                        │
│  [Project Name]  [Save] [Export] [Projects]          │
├──────────┬──────────────────────────────────────────┤
│          │  TIMELINE (horizontal scroll, act groups) │
│  LEFT    ├──────────────────────────────────────────┤
│ SIDEBAR  │                                           │
│          │  PANEL GRID (main canvas)                 │
│ - Modes  │  drag-to-reorder panels                   │
│ - Tools  │                                           │
│ - Export │                                           │
│          ├──────────────────────────────────────────┤
│          │  PANEL EDITOR (bottom drawer, on select)  │
└──────────┴──────────────────────────────────────────┘
```

### Tech Stack
- **Pure HTML/CSS/JS** — single file, no build tools, no framework
- **SVG** — panel illustrations (keyword-driven auto-generation + templates)
- **Canvas API** — sketch mode drawing
- **LocalStorage** — auto-save and multi-project management
- **JSZip (CDN)** — ZIP export for all panels as PNGs
- **`window.print()` + CSS `@media print`** — PDF export
- **Blob URL** — HTML export
- **Canvas `toDataURL()`** — PNG export per panel

---

## 3. Four Creation Modes

### Mode 1 — ✨ Text-to-Panel
User types a natural language description. A keyword parser extracts intent and auto-generates a matching SVG scene in animated-realism style.

**Keyword library:**
- **Subjects:** hero, villain, narrator, product, crowd, hands, host
- **Locations:** alley, office, street, rooftop, forest, studio, room
- **Lighting:** dark, bright, neon, sunset, spotlight, silhouette
- **Shot types:** wide, close-up, medium, aerial, POV, over-shoulder
- **Actions:** walking, running, fighting, talking, revealing, pointing

**Flow:**
```
Input:  "hero walks into a dark alley, low angle, wide shot"
         ↓ keyword parser
Detects: subject=hero, location=alley, lighting=dark, angle=low, shot=wide
         ↓ SVG template engine
Output: Generated SVG panel — silhouette + background + lighting atmosphere
```

### Mode 2 — 🎬 Templates
Visual gallery of 20+ preset panels organised by video type:

| Category | Templates |
|----------|-----------|
| **Cinematic** | Wide establishing, ECU face, Two-shot, Action punch, Chase |
| **YouTube/Explainer** | Talking head, Text overlay, Product reveal, Split screen, Zoom in |
| **Tutorial** | Step callout, Hand pointing, Screen recording frame, Before/after |
| **TikTok/Shorts** | Vertical frame, Hook opener, CTA closer, Reaction shot |

Click a template → drops into timeline as a fully formed panel ready to customise.

### Mode 3 — ✏️ Sketch
Simple drawing canvas per panel:
- **Tools:** pen, marker, eraser, rectangle, circle, arrow, text
- **Colours:** preset palette matching calm minimalist theme
- **Layers:** auto-filled warm off-white background layer + drawing layer
- Sketch saved as embedded PNG data URL inside the panel object

### Mode 4 — 📋 Card
Form-based panel creation — fastest mode:

```
Shot Label:           [________________________]
Shot Type:            [Wide ▼] [Medium ▼] [Close-up ▼] [Aerial ▼] [POV ▼]
Camera Angle:         [Low ▼]  [Eye-level ▼] [High ▼] [Dutch ▼]
Camera Move:          [Static ▼] [Pan ▼] [Dolly ▼] [Handheld ▼] [Zoom ▼]
Duration:             [____] seconds
Background/Location:  [Alley ▼] [Office ▼] [Street ▼] [Rooftop ▼] [Studio ▼] [Custom ▼]
Lighting:             [Dark ▼] [Bright ▼] [Neon ▼] [Sunset ▼] [Spotlight ▼] [Silhouette ▼]
Emotion:              [Tense ▼] [Excited ▼] [Sad ▼] [Mysterious ▼] [Happy ▼] [Angry ▼] [Suspenseful ▼]
Characters in shot:   [checkboxes from Character Manager]
Visual Style:         [Animated Realism ▼] [Minimal ▼] [Sketch ▼] [Comic ▼] [Cinematic ▼] [Flat Design ▼]
Video Style:          [YouTube ▼] [TikTok/Shorts ▼] [Cinematic ▼] [Tutorial ▼] [Documentary ▼] [Ad/Promo ▼]
Description:          [________________________]
Motion Notes:         [________________________]
Audio Notes:          [________________________]
```

Card mode generates a styled SVG panel driven by the selected field values (lighting, emotion, background, visual style all affect the rendered SVG output).

---

## 4. Character Manager

Defined at **project level**, not per-panel. Up to 6 characters per project.

Each character has:
- **Name** (e.g. "Hero", "Host", "Product")
- **Role** (hero / villain / narrator / host / product / extra)
- **Color accent** (chosen from preset palette — drives silhouette stroke color in SVG)

Per-panel, characters are selected via checkboxes. The SVG generator uses the selected characters and their color accents to place the correct silhouettes in the panel.

---

## 5. Timeline & Panel Management

- Panels displayed in a **horizontal timeline** (top) and **grid below**
- Panels grouped into **Acts** (default: Act I, Act II, Act III — renameable, addable)
- **Drag & drop** to reorder panels within or across acts
- Per-panel actions: **Edit**, **Duplicate**, **Delete** (with confirmation)
- **Add Panel** button always visible at end of each act
- Running total duration displayed in timeline header

---

## 6. Save / Load

- **Auto-save** to LocalStorage every 30 seconds
- **Manual save** via Ctrl+S or Save button
- On page load: detects existing project → "Resume?" or "Start New?" prompt
- **Project Manager modal** — supports multiple saved projects:
  - List of projects with last-edited timestamp
  - Open, rename, delete, or create new
- **Export JSON** — full project as `.json` file (backup/transfer)
- **Import JSON** — drag & drop or file picker

---

## 7. Export

| Export | Format | Method |
|--------|--------|--------|
| Shareable HTML | `.html` | Blob URL — full standalone page, calm minimalist style |
| PDF | `.pdf` | CSS `@media print` + `window.print()` |
| PNG (single panel) | `.png` | Canvas `toDataURL()` |
| PNG (all panels ZIP) | `.zip` | JSZip + Canvas `toDataURL()` per panel |
| JSON backup | `.json` | JSON.stringify project data |

**Export modal fields:**
- Project title
- Author name
- Toggle: include audio notes
- Toggle: include motion guides

---

## 8. Phased Delivery

| Phase | Scope |
|-------|-------|
| **Phase 1** | Card mode + Templates + Timeline + Character Manager + Save/Load + HTML & PDF export |
| **Phase 2** | Text-to-Panel (keyword SVG generator) + PNG export + ZIP export |
| **Phase 3** | Sketch mode + Project Manager modal + JSON import/export |

Phase 1 delivers a fully usable, impressive tool. Phases 2 and 3 add power features.

---

## 9. Consistency Rules

- **Background/Location** uses the same keyword set across all 4 modes — panels look consistent regardless of creation mode
- **Visual Style** drives SVG rendering in all modes
- **Video Style** drives template suggestions and default export aspect ratio (16:9 vs 9:16)
- **Character Manager** color accents are respected by the SVG generator in all modes
- All panels share the same data model regardless of which mode created them

---

## 10. Data Model (per panel)

```json
{
  "id": "uuid",
  "act": 1,
  "order": 0,
  "creationMode": "card | template | text | sketch",
  "label": "Wide Establishing Shot",
  "shotType": "wide",
  "cameraAngle": "low",
  "cameraMove": "static",
  "duration": 5,
  "background": "alley",
  "lighting": "dark",
  "emotion": "tense",
  "characters": ["hero", "villain"],
  "visualStyle": "animated-realism",
  "videoStyle": "cinematic",
  "description": "Two figures face each other in a rain-soaked alley.",
  "motionNotes": "Slow dolly push over 10 seconds.",
  "audioNotes": "Rain ambience, distant thunder, low drone.",
  "sketchDataUrl": null,
  "templateId": null,
  "textPrompt": null
}
```

---

## 11. Design System

### Philosophy
Calm, minimal, eye-friendly. Designed for long creative sessions — no harsh contrasts, no aggressive colours. Every element should feel quiet and purposeful.

### Colour Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg` | `#F7F6F3` | Page background — warm off-white |
| `--surface` | `#FFFFFF` | Cards, drawers, header |
| `--border` | `#E8E5DF` | All borders and dividers |
| `--sidebar` | `#F2F0EC` | Sidebar background |
| `--text` | `#2D2D2D` | Primary text |
| `--muted` | `#9A9590` | Labels, secondary text, placeholders |
| `--teal` | `#4A8C8C` | Primary accent — active states, selections, CTA |
| `--sage` | `#6B8F71` | Act II accent, success states |
| `--clay` | `#A0714F` | Sketch mode, warm highlights |
| `--lavender` | `#7B7BA8` | Template mode, secondary character |
| `--red-soft` | `#C0524A` | Destructive actions (delete) only |

### Typography

| Font | Weight | Usage |
|------|--------|-------|
| **Inter** | 300, 400, 500, 600 | All UI text — body, labels, buttons |
| **DM Sans** | 300, 400, 500 | Logo, headings, panel titles |

### Component Rules
- **Border radius:** 6–10px on cards, 6px on inputs, 20px on pills/chips
- **Shadows:** Only on hover — `0 4px 20px rgba(0,0,0,0.07)`, never resting
- **Borders:** `1px solid var(--border)` everywhere — no thick outlines
- **Transitions:** 0.13–0.15s ease on all interactive states
- **Selected state:** `border-color: var(--teal)` + `box-shadow: 0 0 0 2px rgba(74,140,140,0.18)`
- **Spacing:** 8px base unit, multiples of 4

### Panel Scene Backgrounds (per mode)
| Mode | Background colour | Feel |
|------|------------------|------|
| Card | `#EDECEA` | Warm neutral |
| Template | `#EAE9F0` | Cool lavender tint |
| Text-to-Panel | `#E8F0E9` | Sage green tint |
| Sketch | `#F5EFE9` | Warm clay tint |

### SVG Illustration Style
- White or light-filled silhouettes with muted accent colour strokes (not solid black)
- Soft tinted backgrounds (no pure white or pure black scenes)
- Stroke weights: 1–1.5px for figures, 0.6–1px for background details
- All scene SVGs should feel light and airy, not heavy or dramatic

---

## 12. Out of Scope

- No backend / server
- No user accounts / cloud sync
- No AI/LLM API calls (keyword parser is local JS only)
- No video export
- No audio playback
