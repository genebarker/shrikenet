# Logging

The system records log entries using Python's standard logging library and
its predefined logging levels.

The guidelines for these logging levels are defined below.

Of special note, business log entries are also stored in the database. See
[Perform Structured Logging][a]. This strategy provides easy access to
business object history.

## Logging Levels

The following guidelines are used to determine the appropriate logging level
for log entries:

Level       | Guideline
----------- | --------------------------------------------------------------
`CRITICAL`  | Application entry that requires immediate attention.
`ERROR`     | Application entry that's an obvious problem / needs review.
`WARNING`   | Application entry that's a potential problem / needs review.
`INFO`      | Business entry that is understood, tracked, and / or measured.
`DEBUG`     | Application entry that's significant[^1].

## Logging Tips

- [10 Tips for Proper Application Logging][b] post on Java Code Geeks
- [Best practices for logging user actions][c] answer on StackExchange


[^1]: Log entry that mark significant points in processing - a trail of
breadcrumbs that assists in debugging. Some examples: environment settings,
database calls, user actions, processing times, etc..  

[a]: decisions/002_perform_structured_logging.md
[b]: https://www.javacodegeeks.com/2011/01/10-tips-proper-application-logging.html
[c]: http://softwareengineering.stackexchange.com/questions/168059/best-practices-for-logging-user-actions-in-production/168075#168075
