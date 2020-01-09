# Logging

The system logs events to log files using Python's standard logging library
and its predefined logging levels.

The guidelines for these logging levels are defined below.

Of special note, business events are also stored in the database.[^1] This
strategy provides easy access to business object history.

## Logging Levels

The following guidelines are used to determine the appropriate logging level
for events:

Level       Guideline
----------- ---------------------------------------------------------------
`CRITICAL`  Application event that requires immediate attention.
`ERROR`     Application event that's an obvious problem / needs review.
`WARNING`   Application event that's a potential problem / needs review.
`INFO`      Business event that is understood, tracked, and / or measured
            by business users.
`DEBUG`     Application event that's significant[^2].

*Note:* If an `INFO` level event is also a higher level event
(i.e. `WARNING`), then two separate log entries must be performed to ensure
it's handled properly.

## Logging Tips

- [10 Tips for Proper Application Logging][a] post on Java Code Geeks
- [Best practices for logging user actions][b] answer on StackExchange


[^1]: See `decisions/002_perform_structured_logging.md`
[^2]: Events that mark significant points in processing - a trail of
breadcrumbs that assists in debugging. Some examples: environment settings,
database calls, user actions, processing times, etc..  

[a]:https://www.javacodegeeks.com/2011/01/10-tips-proper-application-logging.html
[b]:http://softwareengineering.stackexchange.com/questions/168059/best-practices-for-logging-user-actions-in-production/168075#168075
