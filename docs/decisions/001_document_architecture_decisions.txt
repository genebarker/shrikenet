# 1 - Document Architecture Decisions

## Status

Accepted

## Context

As this project grows, significant architecture decisions will
be made. It's important to know what decisions were made and why. This
knowledge prevents rework and promotes reflective improvement.

## Decision

Use a proven decision template to document architecture decisions. We'll
use the template from Michael Nygard:

- Title: short noun phrase
- Context: describe the forces at play, probably in tension
- Decision: describe our response to these forces
- Status: proposed, accepted, deprecated or superseded
- Consequences: describe the resulting context, after applying the decision

Each decision will be saved as its own file in: `docs/decisions`

Decision filenames will use same format as usecases. See `docs/usecases`
and this decision's filename.

## Consequences

Decision documents requiring ongoing attention are now part of the code
repository.
