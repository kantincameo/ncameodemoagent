---
name: html-ui-generator
description: >-
  Generates beautiful, complete, single-page HTML files from user descriptions. Use this skill whenever a user asks to create a webpage, build a UI, design a page, generate HTML, make a landing page, create a dashboard, build a login form, design a portfolio, or describes any visual layout they want as a web page — even if they don't say "HTML" explicitly. Always invoke this skill for any web UI generation or modification request.
---

# HTML UI Generator Skill

Generate a complete, self-contained, single-page HTML file based on the user's description. The output must be production-quality, visually stunning, and ready to open directly in a browser.

## Core Principles

- **Self-contained**: All CSS and JavaScript must be inline (inside `<style>` and `<script>` tags). No external file references unless the user explicitly requests a CDN framework.
- **Complete**: No placeholders, no `TODO` comments, no lorem ipsum unless the user asks for it. Every section must be fully implemented.
- **Responsive**: Always use responsive design with mobile-first CSS. The page must look great on both desktop and mobile.
- **Modern**: Use current CSS features — CSS variables, flexbox, grid, transitions, animations, backdrop-filter, gradients, and smooth interactions.

## Design Defaults (when user does not specify)

If the user does not specify a style, apply these defaults:
- **Color scheme**: Dark background (#0f0f1a), glassmorphism cards with rgba backgrounds and backdrop-filter blur
- **Typography**: System font stack or Google Fonts via CDN (Inter, Poppins, or similar modern sans-serif)
- **Animations**: Smooth fade-ins, hover transitions (0.3s ease), subtle floating or pulse effects
- **Layout**: Clean sections with generous whitespace, centered content, max-width container
- **Accents**: Purple/blue gradient (#7c3aed to #3b82f6) or vibrant single accent color

## When the user describes a style

Honor every detail of their description:
- Color names → translate to appropriate hex/rgb values
- Style words ("minimalist", "corporate", "playful", "retro", "neon", "pastel") → apply full aesthetic accordingly
- Framework requests ("use Tailwind", "Bootstrap", "Animate.css") → include via CDN in `<head>`
- Layout requests ("sidebar nav", "hero section", "cards grid", "full-screen") → implement exactly

## Output Format

Always output the complete HTML inside a fenced code block:

````html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title</title>
  <style>
    /* All styles here */
  </style>
</head>
<body>
  <!-- All content here -->
  <script>
    // All JavaScript here
  </script>
</body>
</html>
````

After the code block, provide a short **Design Summary** (3–5 bullet points) listing:
- Color palette used
- Layout structure
- Key UI components included
- Any frameworks or special CSS features used
- How to customize or extend it

## Quality Checklist (verify before outputting)

- [ ] All CSS is inside `<style>` tags (or CDN links if requested)
- [ ] All JS is inside `<script>` tags
- [ ] Page is fully responsive (mobile + desktop)
- [ ] No broken references (no `href="#"` for real links, use `href="javascript:void(0)"` or `href="#section"` anchors)
- [ ] Hover states and interactions are implemented
- [ ] Color contrast is accessible (text readable on backgrounds)
- [ ] No placeholder `[YOUR TEXT HERE]` — use realistic sample content
- [ ] The page looks complete and polished at first glance

## Common Page Types & What to Include

**Landing Page**: Hero section with headline + CTA button, features/benefits section, testimonials or stats, footer with links.

**Dashboard**: Sidebar navigation, header with user info, stats cards, a chart area (use CSS/JS to render a simple bar or line chart), data table.

**Login / Auth Page**: Centered card, logo/brand area, input fields with labels, submit button, forgot password link, optional social login buttons.

**Portfolio**: Full-screen hero with name and role, skills section, project cards with hover effects, contact form or links.

**Product Page**: Product image area, title and price, description, add-to-cart button, reviews section, related products.

**Blog / Article**: Clean typography, header image, article content with proper heading hierarchy, author info, tags, related posts.

## Handling Modification Requests

When the user asks to change something about a previously generated page:
- Regenerate the **complete** HTML with the requested changes applied
- Do not output partial diffs or snippets — always provide the full file
- Acknowledge what changed in the Design Summary
