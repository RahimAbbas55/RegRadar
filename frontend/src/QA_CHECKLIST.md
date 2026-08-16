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

## Stage 13-14 additions (streaming + citation panels)

- [x] **Streaming response** — answer text appears token-by-token, not all at once
- [x] **Sources arrive before text** — citation stamps render immediately, before any answer text streams in
- [x] **Loading indicator timing** — pulsing "Searching…" dots show only before the first token arrives, not during active streaming (no overlap)
- [x] **Streaming error handling** — malformed SSE lines are skipped rather than crashing the stream
- [x] **Citation click-to-expand** — clicking a stamp reveals full provision text in an attached panel
- [x] **Multiple citations independent** — expanding one stamp does not collapse others (deliberate choice for compliance cross-referencing use case)
- [x] **Source count label** — messages with >2 citations show "N sources cited" above the stamps
- [x] **Citation keyboard activation** — Tab to a stamp, Enter or Space toggles the panel; visible focus ring
- [x] **Citation panel styling** — panel visually attached to its stamp (matching border color, no seam)

## Known gaps (Stage 13-14)

- Streaming endpoint (`/query/stream`) has simpler error handling than the non-streaming `/query`
  endpoint — doesn't yet distinguish Qdrant-down vs. OpenAI-down vs. generic errors
- Streaming endpoint doesn't yet log timing/cost data (only the non-streaming endpoint does)
- No "collapse all" affordance if a user expands many citation panels on one message

## Last run
Date: 2026-08-17
Result: All checks passed