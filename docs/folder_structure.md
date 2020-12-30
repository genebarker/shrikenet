# Folder Structure

Currently, the system uses [flask][1] to orchestrate web services. The
project folders are organized as that found in the flask documentation and
examples. We added three more folders to this structure:

Folder / Layer  | Description
--------------- | ----------------------------------------------------------
entities        | app data, functions, and interface definitions
usecases        | transactions: orchestrate flow of data to / from entities
adapters        | product, library, and storage adapters

These three folders contain the core code of the project and have no
dependencies on flask. See the [Hexagonal Architecture][2] document for
further detail on the content of these folders.


[1]: https://flask.palletsprojects.com
[2]: hexagonal_architecture.md