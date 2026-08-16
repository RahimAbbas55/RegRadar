# RegRadar Frontend

React + TypeScript chat interface for RegRadar, an FCA Handbook compliance assistant. Built with Vite.

## What it does

A single-page chat UI that sends compliance questions to the RegRadar backend API and renders
grounded, cited answers. Every cited provision appears as a "citation stamp" — a small tagged
chip showing the provision ID and whether it's a binding Rule or non-binding Guidance, color-coded
accordingly.

## Stack

- React 18 + TypeScript
- Vite (dev server + build)
- CSS Modules (no CSS framework — a small, deliberate design token system in `src/index.css`)

## Running locally

Requires the RegRadar backend running first (see the root `README.md`).

```bash
npm install
npm run dev
```

Visit `http://localhost:5173`.

## Configuration

The frontend expects the backend API URL via an environment variable:

VITE_API_BASE_URL=http://localhost:8000

Copy `.env.example` to `.env` and adjust if your backend runs elsewhere. Defaults to
`http://localhost:8000` if unset.

## Project structure

src/
├── api/
│ ├── client.ts # typed fetch wrapper for POST /query
│ └── types.ts # request/response types, mirrors backend Pydantic schemas
├── components/
│ ├── ChatLayout.tsx # main chat UI: message list, input, state management
│ ├── ChatLayout.module.css
│ ├── CitationStamp.tsx # citation chip — the signature visual element
│ └── CitationStamp.module.css
├── types/
│ └── chat.ts # ChatMessage type used for local conversation state
├── index.css # design tokens (color, type, spacing) + global styles
└── App.tsx

## Design system

Defined as CSS custom properties in `src/index.css`:

- **Color**: deep ink navy background, cool paper-grey message cards, muted brass accent.
  Two citation-tag colors — maroon for binding Rules, slate-teal for Guidance.
- **Type**: serif display face (headings), grotesk body face, monospace for provision IDs.
- **Signature element**: the citation stamp — see `CitationStamp.tsx`.

## State management

Plain React `useState` — conversation history is held in memory only and resets on page
refresh. No routing, no global state library; the app is a single view and doesn't need
either yet.

## Known gaps / next steps

- No message persistence across page reloads
- No automated component tests (manual QA only — see `QA_CHECKLIST.md`)
- Citation source text currently shown via native `title` tooltip on hover; a proper
  expandable citation panel is planned (Stage 14)
- No streaming — the full answer arrives at once after the backend pipeline completes
  (typically 2-5 seconds warm); streaming is planned (Stage 13)

## QA

See `QA_CHECKLIST.md` for the manual verification checklist covering empty/loading/error
states, mobile responsiveness, and keyboard accessibility. Run through it after any
significant change to this app.

## Build

```bash
npm run build
```

Outputs to `dist/`. Not yet wired into a deployment pipeline — planned for Stage 15
(Docker + AWS EC2 + CI/CD).