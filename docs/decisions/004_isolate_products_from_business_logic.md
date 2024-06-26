# 4 - Isolate Products from Business Logic

## Status

Accepted

## Context

We want to leverage great existing products to provide as much function as
possible. We don't want to reinvent the wheel. We want to focus our energy
on the unique business function this system provides. As such, *we are
dependent* on existing products. Unmanaged, this dependence creates a number
of issues, for example:

- code breaks when a product changes
- product peculiarities are woven throughout the business logic
- tests can be SLOW (like persistent storage)
- code becomes *locked* to product choices

We don't want these issues.

## Decision

Isolate products from the business logic; do not reference them in the code.

Keep the business logic laser-focused on providing *business* function to
minimize the impact of product changes on the code base.

## Consequences

- System must use a hexagonal (ports & adapters) style architecture.
- More code must be written to incorporate product function  
  (build an interface, no direct calls).
- Business logic is clean; void of product references.
- Tests are easier to write.
- Product changes are easier.
