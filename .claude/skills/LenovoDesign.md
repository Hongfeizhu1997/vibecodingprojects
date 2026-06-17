# Design System Inspiration of Lenovo

## 1. Visual Theme & Atmosphere

Lenovo's design language is built on a single, unwavering conviction: **one red rules everything**. Signature Red (`#E2232A`) is not an accent — it is the brand's heartbeat, present in every communication and used to draw the eye to what matters most. Everything else retreats to black, white, and neutral grays, creating a stage on which that red can perform.

The overall atmosphere is **bold precision meeting human warmth**. Helvetica Neue provides the architectural backbone — rational, international, trustworthy. But Lenovo softens the pure corporate edge through its history of building machines for real people: the typography stays tight and confident but never cold. White space is used generously, not as decoration but as breath between statements.

The OneLenovo evolution adds a secondary dimension: a **Deep Purple** (`#4D144A`) that acts as a "harmonious companion" to Red — adding richness and premium depth without competing. Together they create a palette that is distinctly Lenovo and unlike any other tech brand.

**Key Characteristics:**
- Signature Red as the single dominant interactive and brand color
- Helvetica Neue with tight 95% headline leading — "engineered confidence"
- White and near-white backgrounds as the primary canvas
- L-pattern texture: repeating the "L" letterform creates ownable graphic texture
- Flat, clean surfaces — depth through color contrast, not shadow
- Product-hero photography on white fields with generous breathing room
- Red as typographic punctuation: headlines, CTAs, underlines, rule lines

## 2. Color Palette & Roles

### Primary Brand
- **Signature Red** (`#E2232A`): The singular brand color — CTAs, logo, active states, brand moments
- **Black** (`#000000`): Primary text, hero backgrounds, dominant statements
- **White** (`#FFFFFF`): Page backgrounds, card surfaces, negative space

### Neutral System
- **Charcoal Gray** (`#6F7170`): Secondary body text, metadata, captions
- **Light Warm Gray** (`#C4BEB6`): Dividers, disabled states, subtle borders
- **Off White** (`#D9D8D6`): Alternate section backgrounds, input fields
- **Near Black** (`#1A1A1A`): Primary body text on light backgrounds *(convention value — official spec uses `#000000`)*

### OneLenovo Accent System
- **Deep Purple** (`#4D144A`): Premium accent, section highlights, brand moments alongside Red
- **Deep Red** (`#64131E`): Hover/pressed state for Signature Red, dark hero overlays
- **Mid Red 2** (`#F26A52`): Warm gradient companion, data visualization, secondary highlights
- **Mid Red 3** (`#FFB9A2`): Tinted illustrations, soft data bars

### Tint Palette (Backgrounds & States)
- **Pale Red** (`#FAECEB`): Error states, alert backgrounds, light brand tint sections
- **Pale Red Mid** (`#F0C7BF`): Hover tint on red interactive elements
- **Pale Purple** (`#F1E1ED`): Premium feature callout backgrounds
- **Pale Purple Mid** (`#D9C1D8`): Purple tint section backgrounds
- **Pale Blue** (`#EAEEF5`): Neutral informational callouts
- **Pale Blue Mid** (`#C9D0F0`): Table row alternates, subtle data backgrounds

### Semantic
- **Error / Danger**: Signature Red (`#E2232A`) — Red already serves this role
- **Success**: `#6ABF4A` (Envy Green from extended palette, use sparingly)
- **Warning**: `#FF6A00` (Flame Orange, use sparingly)
- **Info**: `#3E8DDD` (Sapphire Blue, use sparingly)

### Interactive States
- **Button Default**: Signature Red `#E2232A`
- **Button Hover**: Deep Red `#64131E`
- **Button Pressed**: `#1E0013`
- **Focus Ring**: `#E2232A` at 2px solid
- **Link Default**: `#E2232A`
- **Link Visited**: `#64131E`
- **Disabled Text**: `#C4BEB6`
- **Disabled Background**: `#D9D8D6`

## 3. Typography Rules

### Font Families
- **Primary Display**: Montserrat Alternates Bold — used for logo and hero display moments
- **Primary Body**: Helvetica Neue — the core workhorse typeface across all communications
- **Online Fallback**: Lato, then Arial, then sans-serif
- **Chinese / CJK**: Han Yi Bold, Han Yi Medium, Han Yi Regular
- **Internal/Email**: Arial 10pt

```css
font-family: 'Helvetica Neue', 'Lato', Arial, sans-serif;
```

### Hierarchy

> ⚠️ **Note:** Specific px sizes and weights below are inferred from visual observation of Lenovo.com and common web practice — the official brand guide only specifies the typefaces, weight range (Ultralight–Medium), and 95% headline leading. Treat these values as reasonable starting points, not authoritative specs.

| Role | Font | Size | Weight | Line Height | Letter Spacing |
|------|------|------|--------|-------------|----------------|
| Display Hero | Montserrat Alternates | 64px | 700 | 0.95 | -0.5px |
| Page Headline | Helvetica Neue | 48px | 300 | 0.95 ✓ | -0.3px |
| Section Heading | Helvetica Neue | 36px | 400 | 1.00 | -0.2px |
| Sub-heading | Helvetica Neue | 28px | 400 | 1.05 | -0.1px |
| Card Title | Helvetica Neue | 22px | 500 | 1.10 | normal |
| Large Body | Helvetica Neue | 18px | 300 | 1.55 | normal |
| Body | Helvetica Neue | 16px | 400 | 1.60 | normal |
| Body Emphasis | Helvetica Neue | 16px | 500 | 1.60 | normal |
| Small Body | Helvetica Neue | 14px | 400 | 1.50 | normal |
| Caption | Helvetica Neue | 13px | 400 | 1.40 | 0.1px |
| Caption Bold | Helvetica Neue | 13px | 500 | 1.40 | 0.1px |
| Label / Tag | Helvetica Neue | 12px | 500 | 1.33 | 0.5px |
| Micro | Helvetica Neue | 11px | 400 | 1.30 | 0.3px |
| Button | Helvetica Neue | 15px | 500 | 1.00 | 0.3px |
| Nav | Helvetica Neue | 14px | 400 | 1.00 | normal |

*(✓ = confirmed by official brand guide; all others are inferred)*

### Principles
- **95% leading at headline sizes**: Brand guide mandates headline leading at 95% of type size — tight, confident, authoritative
- **Light weight (300) for large display**: Use Ultralight/Light at 36px+ for an editorial, premium feel
- **Sentence case always**: Never all-caps for headlines in OneLenovo system — "Gotham Bold sentence case" is the stated rule
- **No decorative weights at small sizes**: Stick to 400 and 500 below 18px for legibility
- **Letter-spacing compressed at large sizes, neutral at body**: Negative tracking only at display, zero or slightly positive below 16px

## 4. Component Stylings

### Buttons

**Primary Red (Default CTA)**
- Background: `#E2232A`
- Text: `#FFFFFF`
- Font: Helvetica Neue 15px, weight 500, letter-spacing 0.3px
- Padding: 12px 28px
- Border Radius: 4px
- Hover: Background `#64131E`, transition 150ms ease
- Active: Background `#1E0013`
- Focus: 2px solid `#E2232A` outline, 2px offset

**Secondary Outlined**
- Background: transparent
- Text: `#E2232A`
- Border: 2px solid `#E2232A`
- Padding: 10px 26px
- Border Radius: 4px
- Hover: Background `#FAECEB`

**Ghost / Text Link**
- Background: transparent
- Text: `#E2232A`
- Underline on hover
- No border, no radius
- Arrow icon (→) as trailing element

**Dark / Inverse**
- Background: `#FFFFFF`
- Text: `#E2232A`
- Padding: 12px 28px
- Border Radius: 4px
- Used on dark/black backgrounds

**Disabled**
- Background: `#D9D8D6`
- Text: `#C4BEB6`
- Border: none
- Cursor: not-allowed

### Cards & Containers
- Background: `#FFFFFF`
- Border: 1px solid `#D9D8D6`
- Border Radius: 4px
- Shadow: `0 2px 8px rgba(0, 0, 0, 0.08)`
- Padding: 24px
- Hover: Border-color `#E2232A`, shadow `0 4px 16px rgba(226, 35, 42, 0.12)`

**Product Card**
- Image: full-width, 16:9 or 1:1 ratio, white/light bg
- Title: 22px, weight 500, `#1A1A1A`
- Spec line: 14px, weight 400, `#6F7170`
- Red CTA link at bottom
- Border top accent: 3px solid `#E2232A` on hover

### Input Fields
- Background: `#FFFFFF`
- Border: 1px solid `#C4BEB6`
- Border Radius: 4px
- Padding: 10px 14px
- Font: 16px, Helvetica Neue 400
- Placeholder: `#C4BEB6`
- Focus: Border 2px solid `#E2232A`, no shadow
- Error: Border 2px solid `#E2232A`, error text below in `#E2232A` 13px
- Disabled: Background `#D9D8D6`, text `#6F7170`

### Navigation
- Background: `#FFFFFF` (light) or `#000000` (dark hero variant)
- Height: 64px
- Border-bottom: 1px solid `#D9D8D6` (light)
- Logo: Lenovo wordmark in single color — `#000000` on light backgrounds, `#FFFFFF` on dark; red appears only in the brand rectangle beneath the wordmark, not within the letterforms
- Nav links: 14px, Helvetica Neue 400, `#1A1A1A`, hover color `#E2232A`
- Active link: `#E2232A` with 2px bottom border in `#E2232A`
- CTA button (rightmost): Primary Red button
- Mobile: Hamburger icon → full-screen drawer

### Tags & Labels
- Background: `#FAECEB`
- Text: `#E2232A`
- Padding: 4px 10px
- Border Radius: 2px
- Font: 12px, weight 500, letter-spacing 0.5px

### Red Rule Line
- A distinctive 3–4px horizontal rule in `#E2232A`
- Used to separate sections, accent headings, or bookend hero content
- Width: fixed (80px) under headings, or full-width between sections

## 5. Layout Principles

### Spacing System
- Base unit: **8px**
- Scale: 4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96, 128px
- Section vertical padding: 80px desktop, 48px tablet, 40px mobile

### Grid
- Max content width: **1200px** (1280px on wide viewports)
- Columns: 12-column grid with 24px gutters
- Side margins: 24px (mobile), 40px (tablet), auto (desktop, centered)
- No visible grid lines — whitespace creates separation

### Whitespace Philosophy
- **Red as punctuation, space as context**: Lenovo uses generous white space to let products breathe, with red lines and elements creating hierarchy
- **Product photography on white fields**: Never busy backgrounds behind product shots
- **One red moment per section**: Each content block has a single red focal element — CTA, headline accent, or rule line

### Border Radius Scale
- Sharp (0px): Data tables, technical grids
- Micro (2px): Tags, labels, badges
- Standard (4px): Buttons, cards, inputs, containers
- Medium (8px): Featured panels, image containers
- Large (16px): Full-bleed image modules
- Pill: Not used for buttons (Lenovo CTAs are rectangular, not pill-shaped)

## 6. Depth & Elevation

> ⚠️ **Note:** Shadow values below are inferred — the official brand guide describes a flat-first philosophy but does not publish specific box-shadow tokens.

| Level | Shadow / Treatment | Use |
|-------|--------------------|-----|
| Flat (0) | No shadow | Navigation, body sections, tables |
| Lifted (1) | `0 2px 8px rgba(0,0,0,0.08)` *(inferred)* | Cards, product tiles, dropdown menus |
| Floating (2) | `0 4px 16px rgba(0,0,0,0.12)` *(inferred)* | Modal overlays, sticky headers on scroll |
| Brand Glow | `0 4px 16px rgba(226,35,42,0.15)` *(inferred)* | Hovered product cards, focused red CTAs |
| Red Accent | 3px solid `#E2232A` top or left border | Active states, selected items, featured panels |

**Shadow Philosophy**: Lenovo's surfaces are largely flat. Depth is achieved through background-color contrast (white card on gray section) and the "brand glow" — a red-tinted shadow that only appears when the user interacts with a key element. This keeps the interface clean while making interactive moments feel charged and deliberate.

### Elevation via Color
- White on Off White: card-level separation
- Off White on White: section alternation
- Black section: hero/statement moments, inverts all text to white, CTAs to White or Red

## 7. Do's and Don'ts

### Do
- Use Signature Red (`#E2232A`) for ALL primary interactive elements — CTAs, links, active states
- Keep headlines at 95% line-height for that tight, confident brand voice
- Use Helvetica Neue Light (300) for large display text — premium editorial feel
- Alternate sections: white → off-white → black for rhythm and pacing
- Include exactly one red focal element per content section
- Use the L-pattern texture for branded backgrounds and event materials
- Write CTAs in sentence case — never ALL CAPS
- Add a 3–4px red rule line beneath section headings or above hero content
- Use Deep Purple (`#4D144A`) as a premium pairing with Red in special moments

### Don't
- Don't use Red for purely decorative purposes — it must signal action or brand
- Don't use more than one accent color per component (no Red + Purple together on same button)
- Don't use pill-shaped buttons — Lenovo CTAs are rectangular with 4px radius
- Don't use Helvetica Neue weight 700 or 900 — the scale stops at Medium (500)
- Don't use busy, patterned, or photographic backgrounds behind product images
- Don't apply wide letter-spacing to headlines — compress at large sizes
- Don't use all-caps for running text or headlines
- Don't use shadows heavier than `0 4px 16px rgba(0,0,0,0.12)` — the system is flat-first
- Don't put Red text on Red background
- Don't use the extended colors (Sapphire Blue, Envy Green, Flame Orange) without a semantic reason

## 8. Responsive Behavior

### Breakpoints
| Name | Width | Key Changes |
|------|-------|-------------|
| Mobile | <480px | Single column, 40px section padding |
| Mobile Large | 480–768px | Wider single column, 2-col product grid |
| Tablet | 768–1024px | 2–3 column grid, 48px section padding |
| Desktop Small | 1024–1280px | Full layout, 12-col grid |
| Desktop | 1280–1440px | Max content width 1200px, centered |
| Wide | >1440px | Locked at 1280px content width, open margins |

### Touch Targets
- Primary buttons: min 44px height
- Navigation links: 48px height touch area
- Cards: full-card tap target on mobile
- Form inputs: min 44px height

### Collapsing Strategy
- Hero headlines: 64px → 48px → 36px → 28px
- Navigation: horizontal links → hamburger → full-screen drawer
- Product grids: 4-col → 3-col → 2-col → 1-col
- Red rule lines: maintain width proportionally, never disappear
- Section padding reduces from 80px → 48px → 40px as viewport shrinks
- Cards stack vertically, never truncate text — use "show more" pattern instead

### Image Behavior
- Product images maintain 1:1 or 16:9 aspect ratio, never crop
- Hero images go full-bleed at all breakpoints
- White/neutral backgrounds on product shots persist at all sizes
- Lazy load all below-fold images

## 9. Agent Prompt Guide

### Quick Color Reference
- Primary CTA / Brand: Signature Red `#E2232A`
- Hover / Dark Red: `#64131E`
- Page Background: `#FFFFFF`
- Alt Section Background: `#D9D8D6`
- Dark / Hero Background: `#000000`
- Primary Text: `#1A1A1A`
- Secondary Text: `#6F7170`
- Disabled / Subtle: `#C4BEB6`
- Premium Accent: Deep Purple `#4D144A`
- Light Red Tint: `#FAECEB`
- Focus Ring: 2px solid `#E2232A`
- Card Shadow: `0 2px 8px rgba(0,0,0,0.08)`
- Brand Glow: `0 4px 16px rgba(226,35,42,0.15)`

### Example Component Prompts

- "Create a Lenovo hero section on a white background. Headline: 48px Helvetica Neue weight 300, line-height 0.95, letter-spacing -0.3px, color `#1A1A1A`. Subline: 18px weight 300, color `#6F7170`, line-height 1.55. Two CTAs: primary red button (`#E2232A`, white text, 12px 28px padding, 4px radius) and ghost text link with red `→`. Add a 4px horizontal rule in `#E2232A` beneath the headline."

- "Build a Lenovo product card: white background, 1px `#D9D8D6` border, 4px radius. Product image top half on white field (1:1 ratio). Title 22px Helvetica Neue weight 500 `#1A1A1A`. Spec text 14px weight 400 `#6F7170`. Bottom: red text link 'Learn more →' in `#E2232A`. On hover: border-color transitions to `#E2232A`, add `0 4px 16px rgba(226,35,42,0.12)` shadow."

- "Design Lenovo navigation: 64px height, white background, 1px bottom border `#D9D8D6`. Left: Lenovo wordmark. Center: nav links 14px Helvetica Neue 400 `#1A1A1A`, active link in `#E2232A` with 2px bottom underline. Right: primary red CTA button. On scroll >64px, add `0 2px 8px rgba(0,0,0,0.08)` shadow."

- "Create a Lenovo black hero section: background `#000000`, headline 48px Helvetica Neue weight 300 line-height 0.95 white. Subline 18px weight 300 `#C4BEB6`. CTA: white background, `#E2232A` text, 4px radius. Add L-pattern texture overlay at 5% opacity in white behind hero content."

- "Build a Lenovo data table: header row background `#1A1A1A`, header text white 13px weight 500 letter-spacing 0.5px. Body rows alternate white / `#D9D8D6`. Cell text 14px weight 400 `#1A1A1A`. Left column in weight 500. No border-radius. Add 3px left border in `#E2232A` on selected row."

### Iteration Guide
1. Every primary action gets Signature Red (`#E2232A`) — no other color takes that role
2. Headlines use Helvetica Neue Light (300) at large sizes — this is the premium signal
3. Line-height for headlines = 0.95 (95% of font size) — tight is right for Lenovo
4. Section rhythm: white → off-white → black, repeat; Red elements punctuate each
5. Cards use standard box shadow, add brand-glow on hover — subtle but charged
6. Deep Purple (`#4D144A`) is a premium reserve — use for special sections, not utility
7. One red moment per section: either a CTA, a rule line, an active state, or a headline accent
8. Buttons are rectangular (4px radius), never pill-shaped
9. Typography never all-caps; sentence case throughout
10. L-pattern textures can be used as background elements at very low opacity (3–8%) for brand richness without competing with content

---

## 10. HTML Presentation Engine (Slide Deck Template)

When generating an HTML slide deck using this design system, **always use the complete engine below verbatim**. Do not rewrite the navigation logic — common AI-generated mistakes (stuck `animating` lock, missing initial `.active` class, wheel events swallowed by inner scroll) will break navigation silently.

### Required HTML Shell

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>Presentation Title</title>
  <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;500;700&display=swap" rel="stylesheet"/>
  <style>
    /* paste Lenovo design tokens + slide engine CSS here */
    html,body{height:100%;overflow:hidden;font-family:'Lato','Helvetica Neue',Arial,sans-serif;}
    .deck{position:relative;width:100%;height:100%;}
    .slide{
      position:absolute;inset:0;
      display:flex;align-items:center;justify-content:center;
      opacity:0;pointer-events:none;
      transition:opacity .5s ease,transform .5s ease;
      transform:translateY(60px);
      overflow-y:hidden;      /* ← MUST be hidden; auto creates a scroll container that swallows wheel events before they reach document */
    }
    .slide.active{opacity:1;pointer-events:auto;transform:translateY(0);}
    .slide.exit-up{opacity:0;transform:translateY(-60px);}
    .slide.exit-down{opacity:0;transform:translateY(60px);}
    /* CRITICAL: first slide must also receive .active via JS init, not hardcoded */
  </style>
</head>
<body>

<!-- Navigation chrome -->
<nav class="nav-bar">
  <div class="nav-logo">Lenovo</div>
  <div style="margin-left:auto;display:flex;align-items:center;gap:16px;">
    <span id="counter" style="font-size:12px;color:#6F7170;font-family:monospace;"></span>
  </div>
</nav>
<div id="progress" class="progress"></div>
<div id="dots" class="dot-nav"></div>

<!-- Slide deck -->
<div class="deck">
  <!-- SLIDE 1 -->
  <section class="slide" data-title="Cover">
    <div class="s-inner"><!-- slide content --></div>
  </section>

  <!-- SLIDE 2 -->
  <section class="slide" data-title="Agenda">
    <div class="s-inner"><!-- slide content --></div>
  </section>

  <!-- add more slides... -->
</div>

<!-- ═══ SLIDE ENGINE — DO NOT MODIFY ═══ -->
<script>
(function(){
  const slides   = document.querySelectorAll('.slide');
  const dotsEl   = document.getElementById('dots');
  const counter  = document.getElementById('counter');
  const progress = document.getElementById('progress');
  const total    = slides.length;
  let current    = 0;
  let animating  = false;

  /* Build dot nav */
  slides.forEach((s, i) => {
    const d = document.createElement('div');
    d.className = 'dot' + (i === 0 ? ' active' : '');
    d.title = s.dataset.title || ('Slide ' + (i + 1));
    d.addEventListener('click', () => goTo(i));
    dotsEl.appendChild(d);
  });

  function updateChrome() {
    counter.textContent = (current + 1) + ' / ' + total;
    progress.style.width = ((current + 1) / total * 100) + '%';
    dotsEl.querySelectorAll('.dot').forEach((d, i) => d.classList.toggle('active', i === current));
  }

  function goTo(target) {
    if (animating || target === current || target < 0 || target >= total) return;
    animating = true;
    const dir  = target > current ? 1 : -1;
    const prev = slides[current];
    const next = slides[target];

    /* Reset enter-animations on destination slide */
    next.querySelectorAll('.anim').forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
    });

    /* Position next off-screen without transition */
    next.style.transition = 'none';
    next.classList.remove('active', 'exit-up', 'exit-down');
    next.style.opacity   = '0';
    next.style.transform = dir > 0 ? 'translateY(60px)' : 'translateY(-60px)';

    void next.offsetHeight; /* force reflow */

    next.style.transition = ''; /* re-enable CSS transition */

    /* Exit current */
    prev.classList.remove('active');
    prev.classList.add(dir > 0 ? 'exit-up' : 'exit-down');

    /* Enter next */
    next.style.opacity   = '1';
    next.style.transform = 'translateY(0)';
    next.classList.add('active');

    /* Fire stagger animations */
    setTimeout(() => {
      next.querySelectorAll('.anim').forEach(el => {
        el.style.opacity   = '';
        el.style.transform = '';
      });
    }, 50);

    current = target;
    updateChrome();

    /* Release lock after transition completes */
    setTimeout(() => {
      prev.classList.remove('exit-up', 'exit-down');
      prev.style.opacity   = '';
      prev.style.transform = '';
      animating = false;
    }, 600); /* must be >= CSS transition duration */
  }

  /* Keyboard */
  document.addEventListener('keydown', e => {
    if (['ArrowDown','ArrowRight','PageDown',' '].includes(e.key)) { e.preventDefault(); goTo(current + 1); }
    if (['ArrowUp','ArrowLeft','PageUp'].includes(e.key))          { e.preventDefault(); goTo(current - 1); }
    if (e.key === 'Home') { e.preventDefault(); goTo(0); }
    if (e.key === 'End')  { e.preventDefault(); goTo(total - 1); }
  });

  /* Mouse wheel — cooldown prevents accidental double-skip */
  let wheelCD = false;
  document.addEventListener('wheel', e => {
    if (wheelCD) return;
    wheelCD = true;
    if (e.deltaY > 30)       goTo(current + 1);
    else if (e.deltaY < -30) goTo(current - 1);
    setTimeout(() => { wheelCD = false; }, 800);
  }, { passive: true });

  /* Touch swipe */
  let touchY = 0;
  document.addEventListener('touchstart', e => { touchY = e.touches[0].clientY; }, { passive: true });
  document.addEventListener('touchend',   e => {
    const dy = touchY - e.changedTouches[0].clientY;
    if (Math.abs(dy) > 50) dy > 0 ? goTo(current + 1) : goTo(current - 1);
  }, { passive: true });

  /* ── INIT — activate first slide ── */
  goTo(0);   /* intentionally bypasses the current===target guard via fresh state */
  /* Fallback: if goTo(0) is skipped due to guard, force-activate */
  if (!slides[0].classList.contains('active')) {
    slides[0].classList.add('active');
    slides[0].style.opacity   = '1';
    slides[0].style.transform = 'translateY(0)';
    updateChrome();
  }
})();
</script>
</body>
</html>
```

### Critical Rules for Generating Slide Decks

1. **Never hardcode `class="active"` on any `.slide`** — the JS engine sets it. Hardcoding causes the `animating` guard to block all navigation on first click.
2. **Never set `overflow: hidden` on `body` inside a slide** — `body` already has it; inner slides need `overflow-y: auto` to allow tall content to scroll.
3. **The `setTimeout(..., 600)` lock release must match or exceed the CSS `transition` duration** — if you shorten the transition to `.3s`, change the timeout to `350`.
4. **Always use `document` for `keydown`/`wheel` listeners**, never a child element — otherwise focus state can silently swallow events.
5. **`goTo(0)` on init replaces `slides[0].classList.add('active')`** — do not mix both patterns.

---

## 11. Slide Deck Narrative Template

A well-structured business presentation follows a proven narrative arc. Use this template as the default starting point for any Lenovo business deck.

### Standard Slide Order

| # | Slide Type | Purpose | Slide Classes |
|---|------------|---------|---------------|
| 1 | **Cover / Title** | Capture attention, establish context | `slide-dark` (black bg) |
| 2 | **Organisation** | Ground the audience in the team structure | `slide-white` |
| 3 | **Context / Background** | Current state, problem statement | `slide-offwhite` |
| 4 | **Key Initiatives / Priorities** | What matters most — ATL items | `slide-offwhite` |
| 5 | **Current State / AI in Practice** | Show existing wins and tools | `slide-white` |
| 6 | **Why Now / Strategic Data** | Data-driven urgency | `slide-dark` |
| 7 | **Framework / Maturity Model** | Establish shared vocabulary | `slide-dark` |
| 8 | **Roadmap / Timeline** | How we get there | `slide-offwhite` |
| 9 | **Tooling / Capability Matrix** | What tools support the journey | `slide-offwhite` |
| 10 | **Success Factors & Risks** | Governance, risk awareness | `slide-dark` |
| 11 | **Call to Action / Next Steps** | Clear action item | `slide-dark` |

### Narrative Arc Principles

1. **Establish context before making asks** — Org chart → Background → Initiatives
2. **Lead with wins (AI in Practice)** — Build credibility before presenting gaps
3. **Data creates urgency (Why Now)** — Gartner/McKinsey stats establish rationale
4. **Framework creates shared language** — Maturity models help align stakeholders
5. **End with clear action** — Never leave the audience wondering "what now?"

### Background Rhythm

Alternate slide backgrounds for visual rhythm:

```
slide-white  →  slide-offwhite  →  slide-dark  →  repeat
   (clean)        (warm)          (bold)         (contrast)
```

- **slide-white**: Content-heavy slides (tables, org charts, details)
- **slide-offwhite**: Initiative slides, roadmaps (softer, less formal)
- **slide-dark**: Hero moments (cover, strategy, CTAs) — white text pops

---

## 12. Content Composition Patterns

Beyond individual components, these patterns define how content is organized at the slide level.

### ATL / BTL Partition (Initiative Slides)

**Above the Line (ATL)** = funded, approved, committed initiatives
**Below the Line (BTL)** = wish-list, future consideration, dependent on funding

```html
<!-- Budget summary bar — sits above the tables -->
<div class="budget-bar anim">
  <span style="font-weight:700;">Leasing</span>
  <span>Budget: <strong>$375K</strong></span>
  <span>Ask: <strong>$1.52M</strong></span>
  <span class="gap-negative">Gap: –$645K</span>
  <span style="margin-left:auto;"><!-- Owner pills --></span>
</div>

<!-- ATL table -->
<div>
  <div style="font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.5px;text-transform:uppercase;color:var(--charcoal);margin-bottom:6px;">Above the line</div>
  <table class="f-table"><!-- ... --></table>
</div>

<!-- BTL table -->
<div style="margin-top:20px;">
  <div style="display:inline-flex;align-items:center;gap:8px;margin-bottom:6px;">
    <span style="font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.5px;color:var(--charcoal);">Below the line</span>
    <span class="tag tag-neutral" style="font-size:10px;">1</span>
  </div>
  <table class="f-table"><!-- ... --></table>
</div>
```

**CSS for budget-bar:**
```css
.budget-bar{
  display:flex;align-items:center;gap:14px;padding:10px 16px;
  background:rgba(0,0,0,.03);border-radius:var(--radius);font-size:13px;
  flex-wrap:wrap;margin-bottom:16px;border-left:3px solid var(--red);
}
.budget-bar strong{color:var(--near-black);}
.budget-bar .gap-negative{color:var(--red);font-weight:700;}
```

### Owner Pills Pattern

Use color-coded pills to distinguish Biz Owner from DT Owner at a glance:

| Role | Background | Text Color |
|------|------------|------------|
| Biz Owner | `#e0f2e9` (pale green) | `#15803d` (dark green) |
| DT Owner | `#fef3e2` (pale amber) | `#c2610c` (dark amber) |
| New Feature ★ | `#FAECEB` (pale red) | `#E2232A` (red) |

```html
<span class="owner-pill" style="background:#e0f2e9;color:#15803d;font-size:10px;">Andrew Stokes</span>
<span class="owner-pill" style="background:#fef3e2;color:#c2610c;font-size:10px;">Danny Hu</span>
```

**CSS:**
```css
.owner-pill{
  padding:2px 10px;border-radius:2px;font-size:10px;font-weight:700;
  letter-spacing:.3px;
}
```

### Star ★ Marker (New FY Items)

Use ★ to mark items that are new for the fiscal year. This creates visual distinction without changing the card structure.

```html
<span>AP Integration <span class="star">★</span></span>

<!-- With tooltip context -->
<span class="sub-item new">Project ARDIC <span class="star">★</span></span>
```

**CSS:**
```css
.star{display:inline-block;color:var(--red);font-weight:700;font-size:.85em;margin-left:2px;vertical-align:middle;}
.sub-item.new{background:var(--pale-red);color:var(--red);border-color:rgba(226,35,42,.15);font-weight:500;}
```

### mono-label (Sub-section Labels)

Use `mono-label` for fine-grained section categorization within a slide. It sits between `section-label` (large section) and content.

```html
<div style="font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.5px;color:var(--success);margin-bottom:10px;">Success factors</div>
<div style="font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.5px;color:var(--red);margin-bottom:10px;">Risks &amp; mitigations</div>
```

### FY Delivery / Plan Dual Block

For org chart or initiative slides, show both what's been delivered and what's planned:

```html
<div class="fy-delivery">
  <div class="fy-delivery-label">FY25/26 Delivered</div>
  80% MLA migrated into EaaS; 4/5 ISG-Leasing Migrated
</div>
<div class="fy-plan">
  <div class="fy-plan-label">FY26/27 Plan</div>
  MSA, IaaS Migration
</div>
```

**CSS:**
```css
.fy-delivery{
  margin-top:8px;padding:7px 9px;
  background:linear-gradient(135deg,rgba(10,207,131,.08),rgba(26,188,254,.08));
  border:1px solid rgba(10,207,131,.25);border-radius:6px;
  font-size:11px;color:rgba(0,0,0,.6);line-height:1.45;
}
.fy-delivery-label{
  font-family:var(--font-mono);font-size:9px;font-weight:600;
  letter-spacing:.5px;text-transform:uppercase;color:#0acf83;margin-bottom:3px;
}
.fy-plan{
  margin-top:6px;padding:7px 9px;
  background:linear-gradient(135deg,rgba(162,89,255,.07),rgba(242,78,30,.07));
  border:1px solid rgba(162,89,255,.22);border-radius:6px;
  font-size:11px;color:rgba(0,0,0,.6);line-height:1.45;
}
.fy-plan-label{
  font-family:var(--font-mono);font-size:9px;font-weight:600;
  letter-spacing:.5px;text-transform:uppercase;color:#a259ff;margin-bottom:3px;
}
```

---

## 13. Information Hierarchy Guide

### Text Hierarchy Levels

Lenovo typography has 5 distinct hierarchy levels for content organization:

| Level | Class | Size/Weight | Use When |
|-------|-------|-------------|----------|
| **1. Hero** | `.slide-title` | 48px, weight 300 | Slide headlines only |
| **2. Subtitle** | `.slide-subtitle` | 18px, weight 300 | Supporting context under headline |
| **3. Section** | `.section-label` | 11px, weight 700, uppercase | Major slide sections, with red underline |
| **4. Component** | `.branch-head`, `.card-title` | 14-22px, weight 500 | Card titles, branch headers |
| **5. Body** | `.ai-desc`, `.tl-desc` | 12-14px, weight 400 | Descriptive text, captions |
| **6. Meta** | `text-xs`, `.mono-label` | 11-13px, weight 400-500 | Labels, timestamps, metadata |

### When to Use Which Level

**Slide Header Block (always present):**
```html
<div class="section-label anim">Organisation</div>
<h2 class="slide-title anim">Lease Operation Team — structure</h2>
<p class="slide-subtitle anim">Hierarchical org chart with FY26/27 new-development features marked ★</p>
```

**Card Title + Body:**
```html
<div class="ai-card">
  <div class="ai-tag">AI-Build</div>
  <div class="ai-title">Automated Batch Invoice Checker</div>
  <div class="ai-desc">Scans 1,000 invoices per second for validation and anomaly detection</div>
</div>
```

**Org Chart Branch:**
```html
<div class="branch-head">
  <span class="branch-code">LOT-AR</span> Billing
</div>
<div class="sub-list">
  <span class="sub-item new">R.DaaS <span class="star">★</span></span>
  <!-- ... -->
</div>
```

### Color Usage by Hierarchy

- **Primary text** (`#1A1A1A`): Headlines, card titles, branch headers
- **Charcoal** (`#6F7170`): Subtitles, descriptions, meta information
- **Red** (`#E2232A`): CTAs, tags, star markers, section labels (underline only)
- **White** (`#FFFFFF`): Text on dark backgrounds

---

## 14. Business Table Templates

### Standard Initiative Table (ATL/BTL)

```html
<div class="section-label anim">Initiatives</div>
<h2 class="slide-title anim">FY26/27 key projects</h2>
<p class="slide-subtitle anim">Leaser capability roadmap — prioritized by business impact</p>

<!-- Above the line -->
<div>
  <div style="font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.5px;text-transform:uppercase;color:var(--charcoal);margin-bottom:6px;">Above the line</div>
  <div style="overflow-x:auto;">
    <table class="f-table" style="min-width:920px;">
      <thead>
        <tr>
          <th style="width:38px;">ITEM</th>
          <th style="width:17%;">CAPABILITY</th>
          <th style="width:28%;">BIZ BENEFIT</th>
          <th style="width:90px;">BIZ OWNER</th>
          <th style="width:80px;">DT OWNER</th>
          <th style="width:52px;text-align:right;">SIZING</th>
          <th>COMMENT</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="row-label" style="text-align:center;">2-1</td>
          <td style="font-weight:600;color:var(--black);">Credit Control E2E</td>
          <td>Ensure seamless credit application, decision-making, and control process.</td>
          <td><span class="owner-pill" style="background:#e0f2e9;color:#15803d;font-size:10px;">Andrew Stokes</span></td>
          <td><span class="owner-pill" style="background:#fef3e2;color:#c2610c;font-size:10px;">Danny Hu</span></td>
          <td style="text-align:right;font-weight:600;color:var(--black);">$75K</td>
          <td style="font-size:11px;color:rgba(0,0,0,.5);line-height:1.35;">Dependency: Linkredit IT capacity.</td>
        </tr>
        <!-- more rows -->
      </tbody>
    </table>
  </div>
</div>
```

### Tool / Capability Matrix

```html
<div class="cards-grid c3">
  <div class="mx-card">
    <div class="mx-head">Beginner</div>
    <div class="mx-list">
      Microsoft Copilot (M365 suite)<br>
      Power Automate templates<br>
      Pre-built Power BI dashboards
    </div>
  </div>
  <div class="mx-card">
    <div class="mx-head">Intermediate</div>
    <div class="mx-list">
      Custom Power Automate flows<br>
      Python scripting for data prep<br>
      Azure Cognitive Services APIs
    </div>
  </div>
  <div class="mx-card">
    <div class="mx-head">Advanced</div>
    <div class="mx-list">
      Custom ML models (Azure ML)<br>
      GPT-4 / Claude API integrations<br>
      End-to-end automation pipelines
    </div>
  </div>
</div>
```

### AI Tool Card

```html
<a class="ai-card" href="https://..." target="_blank">
  <div class="ai-tag">AI-Build</div>
  <div class="ai-title">Automated Batch Invoice Checker</div>
  <div class="ai-desc">Scans 1,000 invoices per second for validation and anomaly detection</div>
</a>
```

### CSS for All Table Components

```css
/* Standard table */
.f-table{width:100%;border-collapse:collapse;font-size:13px;}
.f-table thead{background:var(--near-black);color:var(--white);}
.f-table th{
  padding:8px 10px;font-size:11px;font-weight:700;
  letter-spacing:.5px;text-transform:uppercase;text-align:left;
}
.f-table td{padding:8px 10px;border-bottom:1px solid var(--off-white);}
.f-table tbody tr:nth-child(even){background:rgba(0,0,0,.02);}
.f-table tbody tr:hover{background:var(--pale-red);}
.row-label{font-weight:600;color:var(--black);background:rgba(0,0,0,.02);}

/* Owner pill */
.owner-pill{
  padding:2px 10px;border-radius:2px;font-size:10px;font-weight:700;
  letter-spacing:.3px;
}

/* Matrix card */
.mx-card{
  background:var(--white);border:1px solid var(--off-white);
  border-radius:var(--radius);padding:14px 16px;
  box-shadow:var(--shadow-sm);
  transition:border-color .2s,box-shadow .2s,transform .2s;
}
.mx-card:hover{border-color:var(--red);box-shadow:var(--shadow-red);transform:translateY(-2px);}
.mx-head{font-size:12px;font-weight:500;color:var(--red);margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px;}
.mx-list{font-size:12px;color:var(--charcoal);line-height:1.6;}

/* AI card */
.ai-card{
  display:block;text-decoration:none;
  background:var(--white);border:1px solid var(--off-white);
  border-radius:var(--radius);padding:14px 16px;
  box-shadow:var(--shadow-sm);
  transition:border-color .2s,box-shadow .2s,transform .2s;
  color:inherit;
}
.ai-card:hover{border-color:var(--red);box-shadow:var(--shadow-red);transform:translateY(-2px);}
.ai-card .ai-title{font-size:14px;font-weight:500;color:var(--near-black);margin-bottom:4px;}
.ai-card .ai-desc{font-size:12px;color:var(--charcoal);line-height:1.4;}
.ai-tag{
  display:inline-flex;align-items:center;gap:4px;
  font-size:10px;font-weight:700;letter-spacing:.5px;
  padding:2px 8px;border-radius:2px;
  background:var(--pale-purple);color:var(--purple);
  margin-bottom:6px;
}
```
