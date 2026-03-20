# JADN Software

JSON Abstract Data Notation (JADN) information model development.

*organization:*

* [apps](apps): Information Modeling applications, currently including a command line (CLI) schema translation tool.
* [docs](docs): Documentation for developing and using JADN information models.
* [jadn](jadn): Source for the JADN software package distributed on PyPI. This will eventually be moved
to its own repository.
* [schemas](schemas): JADN information models used to illustrate information modeling and test
the JADN software package.
* [test](test): Unit test suite for the JADN software package.

Both the CLI application and the unit tests illustrate use of the JADN processing software.

## Quickstart

The [Coordinate schema](schemas/jadn/coordinate.jadn) is a simple "hello world" example information model,
consisting of a single type definition containing two fields.

*purpose of information modeling: exact equivalence between all representation formats* 

Translate it from JADN format (authoritative JSON data) to text format using an example (non-autoritative)
domain specific language called JADN Information Definition Language (JIDL).
From a Windows cmd tool in the top-level `jadn2` directory and a Python virtual environment in `.venv`, type:

```
.venv\scripts\activate
set PYTHONPATH=c:\full\path\to\jadn2
python apps/jadn-convert.py schemas/jadn/coordinate.jadn -f jidl
```

*Note that jadn, jidl and xasd representations serve different purposes but represent the identical information
(python variable)*