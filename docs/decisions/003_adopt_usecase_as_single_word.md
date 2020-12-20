# 3 - Adopt Usecase as Single Word

## Status

Accepted

## Context

A usecase is typically spelled as 'use case'. This project places usecases
at the center of its requirements and consequently its code base. The
widespread usage of this two word term results in unwieldy references in
documentation, class paths, and attribute names. Some examples:

- Please see use case #4.
- `/usecases/base_use_case.py`
- `event.source_use_case_oid`

## Decision

Adopt usecase as a single word.

In this project, a usecase is a well-defined term. Collapsing this term into
a single word is 1) natural (doesn't confuse anyone), and 2) keeps its
usage in the project clean.

## Consequences

- Path, file, table, and attribute names are concise and clean.
- References to usecases in documentation may appear _wrong_ to new project
  contributors. 
