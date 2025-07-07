# JADN CLI applications

## Convert Schemas
**jadn-convert.py:** Convert JADN schemas between different forms. The following conversions are supported:
* **Convert:** Convert a JADN schema package in one data format to the same package in a different format.
All representations are equivalent, meaning that conversions between data formats are lossless.  
JADN schema and presentation formats are:
    * **jadn:** JSON data, the authoritative data format for JADN schemas
    * **jidl:** JADN Information Definition Language, a declarative text specification analogous to source code
    * **xasd:** XML Abstract Schema Definition language, an XML data format for JADN schemas
    * **md:** Markdown tables, a property table format for including JADN schemas in specification documents
    * **atree:** ASCII tree diagram showing dependency relationships between types
    * **erd:** Entity Relationship Diagram, text source for a graphical representation of a JADN schema.
    Two ERD formats are currently supported: Graphviz (.dot) and PlantUML (.puml)
* **Translate:** Translate a JADN schema into a different abstract or concrete schema language. Translations
are lossy to the extent that different languages have different capabilities and concrete schemas are less
flexible than information models, but mechanical translation provides a starting point for refinement.  
Schema languages are:
    * **jschema:** JSON Schema
    * **xsd:** XML Schema Definition
    * **cddl:** Concise Data Definition Language, the schema specification for IETF CBOR
    * **proto:** Google Protocol Buffers
    * **xeto:** Extensible Explicitly Typed Objects, a schema language developed for the smart buildings industry
* **Transform:** Convert a JADN schema into different JADN schema for various purposes such as:
    * simplifying shortcuts (syntactic sugar) into core definitions 
    * resolving external references between schema packages

**Usage:**
```
usage: jadn-convert.py [-h] [-f format] [-r] [--style STYLE]
                       schema [output_dir]

Convert JADN schemas to a specified format.

positional arguments:
  schema
  output_dir

options:
  -h, --help     show this help message and exit
  -f format      output format (default: jadn)
  -r             recursive directory search (default: False)
  --style STYLE  serialization style options (default: )
```
Examples:
* `jadn-convert.py -f erd --style "detail: information, attributes: True" jadn/data/jadn_v2.0_schema.jadn Out`
* `jadn-convert.py -f atree --style "detail:logical" jadn/data/jadn_v2.0_schema.jadn`

If output_dir is not specified, output goes to stdout.

Read a JADN `schema` package in the format indicated by its file extension (`.jadn`), convert it to the `erd`
(entity relationship diagram) format, overriding the default style options `detail` and `attributes`.

CLI style options are key:value pairs separated by commas and must be enclosed in double quotes.
Specifying invalid style options (e.g., `--style ?`) will print out all options applicable to the
`format` including default values from the format definition and the user's configuration file.

Example user-defined configuration file `jadn_config.json`:
```json
{
  "style": {
    "jidl": {
      "name": 20,
      "desc": 55
    },
    "erd": {
      "graph": "graphviz"
    }
  }
}
```
The top level of the configuration file is a section.
Under the style section are output formats and the option values specified for each format.
Only the style section is defined at this time, but additional sections may added later.

This example sets column widths for JIDL output and the graph format for ERDs. The data format class file
defines all possible options and their default values.  The configuration file overrides some of those
values, and the CLI `--style` argument supersedes both.

## Serialize and Validate Data
tbsl