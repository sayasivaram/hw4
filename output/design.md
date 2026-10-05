# Visual Design (Problem 10)

How the Campus Customs website was styled into a distinct, collegiate-branded site, and why each choice was made.

---

## Brand identity: original, not Yale's actual marks

Yale's official seal and wordmark are trademarked, so instead of reproducing them, two **original** collegiate-style motifs were designed from scratch:

- **`BulldogMark`** (`frontend/src/components/BulldogMark.tsx`) -- a simplified bulldog face, built as a single-color SVG (`currentColor`), used in the navbar watermark, the homepage trust strip, and the footer. The first version read as an abstract blob rather than a recognizable bulldog and was redrawn with clearer ears/jowls/snout geometry.
- **`CrestMark`** (`frontend/src/components/CrestMark.tsx`) -- a generic shield-and-monogram crest (not Yale's seal), used as the navbar brand mark in place of plain text initials.

Both are reusable, recolorable components rather than static image assets, so they render crisply at any size and can be restyled from CSS alone.

## Color palette and collegiate texture

The existing Yale-Blue/gold palette (`index.css` custom properties: `--yale-blue`, `--yale-blue-dark`, `--yale-gold`) was extended with a **preppy tartan background texture**, applied site-wide via `body`/`.plaid-bg` and a darker `.plaid-bg-dark` variant for navy sections. This went through two iterations:

1. **First attempt**: a uniform two-layer grid (same stripe width on both axes) -- this read as plain graph paper, not plaid.
2. **Final version**: an authentic tartan *sett* -- asymmetric navy and gray bands of different widths, plus two offset thin "overcheck" threads (a gold pinstripe and a navy hairline) layered on both axes within one 96px repeat. Because the bands are asymmetric and the threads are offset rather than centered, the pattern reads as woven plaid rather than a checkerboard, and the overlapping semi-transparent layers naturally darken at the intersections the way real woven tartan does.

Both variants are kept subtle (low alpha) specifically so body text and product cards sitting on top of the texture stay fully legible -- verified by screenshot at both desktop and mobile widths.

## Real campus photography, treated to match the brand

Two user-supplied photos of Yale's campus (Harkness Tower, Sterling Memorial Library) were added to `frontend/public/images/campus/`. Rather than using them at full color (which would clash with the blue/white/gray palette -- green leaves, blue sky), a reusable **navy duotone treatment** (`.photo-duotone` in `index.css`) was built: `grayscale(1)` on the image itself, plus an absolutely-positioned `mix-blend-mode: multiply` navy overlay at ~55% opacity. This makes any photo dropped into a `.photo-duotone` wrapper automatically match the site's palette without per-image editing.

These photos are used in two places:
- The **hero section** background (behind the existing navy gradient overlay), replacing a flat color gradient with real campus imagery.
- A new **"Rooted on Old Campus" section** on the homepage, featuring both photos side by side in gold-bordered frames against the dark tartan background, with copy tying the brand's aesthetic directly to the Gothic architecture.

## Homepage structure (Aritzia-inspired ordering)

The homepage was deliberately reordered to follow the "hero → browse by category → full catalogue" flow common to sites like Aritzia, rather than leading with static marketing copy:

1. **Hero** -- a punchy title/subhead over the duotone campus photo, with a primary CTA.
2. **Shop by Category** (`CategoryTiles.tsx`) -- clickable tiles using real product photos as backgrounds, not icons, each linking to a pre-filtered Products page (`?category=...`). Categories are derived from the catalogue's messy `garment_type` text via a shared classifier (`utils/categories.ts`), the same one used for category chip filters on the Products page.
3. **The Full Catalogue** -- an 8-product preview grid with a "view all" link, so a visitor sees real inventory immediately rather than having to click through first.
4. **Rooted on Old Campus** -- the campus photography section described above.
5. **Trust strip** -- three short credibility points (officially licensed, made for campus life, a New Haven original), each paired with the bulldog mark.

## Product card "pop" on hover

Per the explicit ask, `ProductCard.css` was given a spring-eased hover state: the whole card lifts and scales slightly (`translateY(-6px) scale(1.035)`) with a deepening navy-tinted shadow and a blue border, the product image zooms in underneath the overflow-hidden frame, and a "View Details" label slides up from the bottom edge -- all on a `cubic-bezier` spring easing rather than a linear transition, so it feels like a deliberate "pop" rather than a plain fade.

## Verified

All of the above was checked in the live, running app (not just by reading the CSS) at both desktop and 375px mobile viewport widths: the tartan texture, the duotone photos in both the hero and the heritage section, the category tiles linking correctly to filtered Products views, and the card hover effect.
