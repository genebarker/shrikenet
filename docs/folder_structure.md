# Folder Structure

The core of the project is the server. The system uses [flask][1] to
orchestrate these services. The project folders are organized as that found
in the flask documentation. We added the usecases and entities folders to
isolate the business logic from product dependencies. We added the adapters
folder to store the product specific implementations of the adapters used by
the business logic.

Folder    | Layer       | Description
--------- | ----------- | --------------------------------------------------
static    | product     | static web assets
templates | product     | jinja web templates
web       | interfaces  | web interface
api       | interfaces  | json api interface
client    | interfaces  | command line client
adapters  | interfaces  | product, library, and storage adapters
usecases  | usecases    | transactions; orchestrate flow of data to entities
entities  | entities    | app data, functions, and adapter definitions

See the [Hexagonal Architecture][2] document for further detail on the
content of these folders and how they are layered.


[1]: https://flask.palletsprojects.com
[2]: hexagonal_architecture.md
