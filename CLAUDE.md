# CLAUDE.md

This file provides guidance for AI assistants working with this codebase.

## Project Overview

This is **jongjunlee12.github.io** - a GitHub Pages personal website hosting a single-page Korean-language presentation titled "성수, 쉼의 생태계" (Seongsu, Ecosystem of Rest). The site presents a master plan proposal for creating urban healing/rest spaces in Seongsu-dong, Seoul.

## Repository Structure

```
jongjunlee12.github.io/
├── index.html          # Main (and only) page - slide-based presentation
├── CLAUDE.md           # This file
└── .git/               # Git configuration
```

This is a minimal static site with no build process, dependencies, or configuration files.

## Technology Stack

- **HTML5** with Korean language content (`lang="ko"`)
- **Tailwind CSS** via CDN (`https://cdn.tailwindcss.com`)
- **Google Fonts** - Nanum Square font family
- **No JavaScript** - Pure CSS presentation
- **No build tools** - Direct static hosting

## Architecture & Design Patterns

### Slide-Based Layout
The site uses a slide presentation format with:
- `.slide-container` - Main wrapper (max-width 1280px, centered)
- `.slide` - Individual slides with 16:9 aspect ratio (`padding-top: 56.25%`)
- `.slide-content` - Absolute positioned content layer

### Layout Variants
1. **Centered content slides** - Default full-width centered layout
2. **Split slides** - Two-column grid layout (`.split-slide`)
   - `.split-image` - Background image side
   - `.split-content` - Text content side

### Color System
Uses Slate color palette from Tailwind:
- Background: Slate 50 (`#f8fafc`)
- Primary text: Slate 800/900 (`#1e293b`, `#0f172a`)
- Secondary text: Slate 600/700 (`#475569`, `#334155`)
- Accents: Blue and Green highlight classes

### Highlight Classes
- `.highlight-blue` - Blue 50 bg with Blue 800 text
- `.highlight-green` - Green 50 bg with Green 800 text

## Content Structure (10 Slides)

1. **Title slide** - Project name and tagline
2. **Vision overview** - "One ecosystem, two types of rest"
3. **'비움' (Emptiness) spaces** - Open urban spaces concept
4. **'채움' (Fullness) spaces** - Cultural/sensory spaces concept
5. **Sound Library** - Audio meditation space
6. **Scent Archive** - Olfactory experience space
7. **Analogue Lounge** - Digital detox space
8. **Light & Shadow Museum** - Visual meditation space
9. **Ecosystem map** - User journey overview
10. **Closing message** - Core philosophy statement

## Development Workflow

### Making Changes
1. Edit `index.html` directly
2. Test locally by opening in browser
3. Commit and push to deploy (GitHub Pages auto-deploys from main branch)

### Local Testing
```bash
# Simple local server (if needed)
python -m http.server 8000
# Or just open index.html directly in browser
```

### Deployment
- Automatic via GitHub Pages
- Site URL: `https://jongjunlee12.github.io`
- Deploys on push to main branch

## Code Conventions

### CSS
- Custom styles defined in `<style>` block within `<head>`
- Uses CSS custom properties sparingly
- Relies on Tailwind utility classes for inline styling
- Uses `clamp()` for responsive typography

### HTML
- Semantic slide structure with numbered headers (`.slide-header`)
- Placeholder images from `placehold.co` service
- Inline background images via `style` attribute

### Language
- All content is in **Korean**
- Font: Nanum Square (Korean web font)

## Important Notes for AI Assistants

1. **Single file codebase** - All code is in `index.html`
2. **No dependencies to install** - Uses CDN for all external resources
3. **Presentation format** - Changes should maintain slide aspect ratios and layout structure
4. **Korean content** - Preserve Korean text and appropriate font support
5. **Placeholder images** - Current images are placeholders; real images should replace `placehold.co` URLs
6. **No build process** - Direct edit and commit workflow

## Common Tasks

### Adding a new slide
1. Copy an existing slide `<div>` block
2. Update `slide-header` number
3. Modify content and styling

### Changing colors
- Update custom CSS classes in `<style>` block
- Or use Tailwind utility classes directly

### Replacing placeholder images
- Replace `placehold.co` URLs with actual image URLs
- Maintain aspect ratios for proper display

## Git Workflow

- **Main branch**: Production (auto-deployed)
- **Commit messages**: Descriptive, in English preferred
- **No CI/CD configuration** - GitHub Pages handles deployment
