# 5 - Use Embedded Database (SQLite)

## Status

Proposed

## Context

The project must choose an ideal SQL database for data storage.

The target users of the shrikenet project are small organizations (see
project [README][1]). We want to give them the ability to run their own
online community software on modest hardware at low cost (i.e. old PC,
small VPS, RasberryPi).

By its nature, shrikenet manages several interrelated record types (i.e.
users, groups, posts, messages). Using a SQL database is generally accepted
as the best way to store and manage such data.

Two widely recognized types of SQL databases exist:

1. Embedded, exemplified by SQLite; and
2. Client-Server, represented by PostgreSQL, MySQL, among others.

Embedded SQL databases operate in a serverless manner, allowing applications
to interact directly with the database through function calls rather than
sending messages to a separate process.

Client-Server SQL databases function as servers, capable of handling
multiple concurrent connections and ensuring transactional integrity across
all connected clients.

## Decision

Use an embedded database since:

- shrikenet server is the only user
- it's **fast**
- reduces installation requirements
- reduces project complexity

Use [SQLite][2] since:

- considered the best embedded SQL database
- well known, well supported, and free

Moreover, shrikenet's intended use, serving small organizations, closely
aligns with the [Appropriate Uses of SQLite][3].

## Consequences

- External clients can not access shrikenet data directly (they must access
  the data via the shrikenet server).
- The shrikenet server must manage user connections.
- The MemoryAdapter and PostgreSQLAdapter classes must be replaced with
  a SQLiteAdapter.
- The StorageProvider tests must be simplified. Currently they use fixtures
  to test both adapter types using the same code. These fixtures should be
  removed so that the tests are easier to understand.


[1]: ../../README.md
[2]: https://www.sqlite.org/index.html
[3]: https://www.sqlite.org/whentouse.html
