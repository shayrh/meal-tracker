# Agent Guidelines

## Scope
These guidelines apply to the entire repository. Create more specific `AGENTS.md` files in subdirectories if you need overrides.

## General workflow
- Prefer small, well-focused commits with descriptive messages.
- When you touch both backend (Python) and frontend (React) code, split changes logically when possible.
- Update or add tests alongside behavior changes.

## Backend (Flask / Python)
- Use f-strings for string interpolation when variables are involved.
- Keep imports grouped (standard library, third-party, then local) with a blank line between groups.
- Run relevant unit or integration checks via `pytest` when backend logic changes. If no automated tests cover your change, note the manual verification steps in the summary.

## Frontend (React)
- Favor functional components and React hooks. Avoid introducing new class components.
- Keep styling changes in CSS modules or existing stylesheet conventions; avoid inline styles unless necessary.
- Use `npm test` or targeted `npm run lint` if applicable after modifying frontend behavior.

## Documentation
- Ensure README-style files stay in sync with code changes that affect setup or usage instructions.

## Secrets
- Never commit real API keys or secrets. Use environment variables and `.env.example` patterns instead.
