# Hati mobile expense page redesign

## Intent
Make Hati feel polished and dependable for college roommates splitting PHP expenses on phones, while retaining every current page feature.

## Goals
- Make the current balance and settlement list easy to scan.
- Make adding an expense feel simple on a narrow screen.
- Preserve the existing `POST /expenses` and `GET /settlements` behavior.

## Non-goals
- No API, data-model, or persistence changes.
- No new frontend dependencies or design framework.

## Constraints
- The page remains the inline HTML template in `main.py`.
- Interactive controls remain usable by touch and keyboard.

## Approaches
1. Update the single inline template: selected because it is the smallest change and retains the existing FastAPI surface.
2. Use static CSS and JavaScript files: cleaner separation but disproportionate for this three-file application.
3. Add a component framework: rejected because it adds complexity without improving the current user flow.

## Design decisions
- **Style:** calm and trustworthy, selected from the visual companion.
- **Colours:** navy text, accessible blue actions, pale blue background surfaces, and white cards. These create financial clarity without the severity of a banking dashboard.
- **Fonts:** system sans-serif stack for fast loading and native familiarity on student phones.
- **Layout:** a compact brand header, a clear balance panel, a card-based expense form, and settlement rows with clear payer/payee hierarchy.
