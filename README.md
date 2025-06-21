# JADN CLI applications

## jadn-convert
Convert JADN schemas between different forms. The following conversions are supported:
* **Convert:** Convert a JADN schema package in one data format to the same schema in a different format.
All representations are equivalent, meaning that conversions between data formats are lossless.
Data formats are:
    * **jadn:** JSON data, the authoritative data format for JADN schemas
    * **jidl:** JADN Information Definition Language, a declarative text specification analogous to source code
    * **xasd:** XML Abstract Schema Definition language, an XML data format for JADN schemas
    * **md:** Markdown tables, a property table format for including JADN schemas in specification documents
    * **erd:** Entity Relationship Diagram, text source for a graphical representation of a JADN schema
    in two formats: Graphviz and PlantUML
* **Translate:** Translate a JADN schema into a different abstract or concrete schema language. Translations
are lossy to the extent that different languages have different capabilities and concrete schemas define
a lower level of abstraction, but machine translation provides a starting point for human refinement.
Schema languages are:
    * **jschema:** JSON Schema
    * **xsd:** XML Schema Definition
    * **cddl:** Concise Data Definition Language, the schema specification for IETF CBOR
    * **proto:** Google Protocol Buffers
    * **xeto:** Extensible Explicitly Typed Objects, a schema language developed for the smart buildings industry
* **Transform:** Convert a JADN schema into different JADN schema for various purposes, such as:
    * simplifying shortcuts (syntactic sugar) into core definitions 
    * resolving external references between schema packages

### Usage

```
Usage: jadn-convert.py [-h] [-f format] [-r] [--style STYLE] schema [output]

Positional arguments:
  schema
  output

Options:
  -h, --help     show this help message and exit
  -f format      output format (default: jadn)
  -r             recursive directory search (default: False)
  --style STYLE  serialization style options (default: )
```
Example:
* `jadn-convert.py -f erd --style "detail: logical, attributes: True" jadn/data/jadn_v2.0_schema.jadn`

Read a JADN `schema` package in the format indicated by its file extension `.jadn`, convert it to the `erd`
(entity relationship diagram) format, overriding the default style options `detail` and `attributes`.
CLI style options are key:value pairs separated by commas and must be enclosed in double quotes. Supplying
empty style options `--style ""` will print out all of the options applicable to the `format` with
default values from the class definition user configuration file.

Example user-supplied configuration file `jadn_config.json`:
```json
{
  "style": {
    "erd": {
      "graph": "graphviz"
    }
  }
}
```
Only `style` options are defined at this time. Additional top-level sections may be added to the configuration
file as additional schema operations are created.

This example specifies no output folder so the output goes to stdout.
