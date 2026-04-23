# 2 - Perform Structured Logging

## Status

Accepted

## Context

Logging is a well-known / well-used discipline in software development.
There are great libraries available that make logging non-invasive (nobody
wants old debug print statements in the code base). We should adopt some
proven guidelines for logging to avoid cluttering-up our code.

More, Eugene's previous systems have enjoyed great / ongoing success by
logging business events in their databases. Users could quickly see what
happened, when it occurred, and who did it. More, business reports were
developed that create great value (some, years after the system went live).
We want that success too.

## Decision

(1) Record log entries in structured manner. Adhere to the *logging levels*
defined in the [Logging design document][1]. The specifics of these levels
will evolve over time and that's OK; most old log entries are culled
anyways.

(2) The `INFO` logging level will include (but are not limited to) business
events. Business events are those events understood, tracked, and measured
by business (non-tech) users.

(3) In addition to the logs, business events will be stored in the system's
database with key fields to support business reporting. 

## Consequences

- A [Logging design document][1] that requires ongoing attention is now part
  of the code repository.
- When business events occur, they must be logged both to the logs and to
  the database.
- Business events, their types, and their relationships must be considered
  in the database design.
- Developers must know the *logging levels* and record log entries
  accordingly.


[1]: ../logging.md
