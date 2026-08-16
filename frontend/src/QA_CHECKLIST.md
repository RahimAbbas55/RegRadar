# RegRadar Frontend — Manual QA Checklist

Run through this checklist after any significant frontend change, with both the backend API (`uvicorn api.main:app --reload`) and Qdrant running.

## States verified

- [x] **Empty state** — loads with orienting text and 3 clickable example questions
- [x] **Example question click** — populates input without auto-sending
- [x] **Send via button click** — real query, correct answer + citations returned
- [x] **Send via Enter key** — same behavior as button click
- [x] **Loading state** — pulsing dot indicator + "Searching the FCA Handbook…" while awaiting response; input and button disabled during this window
- [x] **Successful answer** — paper card renders, citation stamps show correct provision ID, correct Rule/Guidance tag and color
- [x] **Error state (backend down)** — distinct maroon-bordered card, clearly different from a real answer
- [x] **Empty query submission** — blocked client-side (whitespace-only input does nothing on send)
- [x] **Mobile viewport (~375px)** — layout doesn't overflow, citation stamps stack, input/button remain usable
- [x] **Keyboard: auto-focus** — input focused on page load
- [x] **Keyboard: Tab navigation** — input → Ask button → citation stamps, all reachable, visible focus ring on each
- [x] **CORS** — frontend (localhost:5173) successfully calls backend (localhost:8000) cross-origin

## Known gaps (deliberately out of scope for Stage 12)

- No message persistence — refreshing the page clears conversation history (acceptable for this stage; not a chat product with accounts)
- No automated component tests — manual QA only; a reasonable future addition would be Vitest + React Testing Library
- Citation stamp source text is shown via native `title` tooltip only — Stage 14 will replace this with a proper expandable citation panel
- No streaming — full answer arrives at once after the ~2-5s pipeline completes; Stage 13 addresses this

## Last run
Date: 2026-08-16
Result: All checks passed