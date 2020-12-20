# Hexagonal Architecture

To [Isolate Products from the Business Logic][1], the system has a
hexagonal (ports & adapters) architecture. It aligns closely to the rules
described in Uncle Bob's post [The Clean Architecture][2]. The core of
this architecture is the *Dependency Rule* where source code dependencies
can only point inwards.

Products                | Adapters         | Business Logic
----------------------- | ---------------- | ----------------------
flask, PostgreSQL, etc  | <-- adapters --> | usecases --> entities

Product dependencies are isolated from the business logic via adapters.
The interfaces for the adapters are defined in the entities layer. The
business logic uses these interfaces to access the adapters provided to
it via dependency injection. For example, a usecase may require a storage
provider (PostgreSQL).


[1]: decisions/004_isolate_products_from_business_logic.md
[2]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
