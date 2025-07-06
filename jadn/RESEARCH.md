# Ideas to Explore

* Translate JADN to JSON Schema anonymous style - generate unnamed nested type definitions
* Integrate npm graph viewers

* https://marketplace.visualstudio.com/items?itemName=imgildev.vscode-json-flow
Transform your JSON files into interactive node-based graphs directly in Visual Studio Code.
JSON Flow makes working with structured data effortless and visually intuitive,
turning raw data into dynamic, interactive visualizations.

* https://jsonformatter.org/yaml-to-flow
Generates type definitions, for purpose currently unknown.
```
export type Welcome3Properties = {
    provenance: Provenance;
    source:     Source;
    use:        Use;
};

export type Provenance = {
    description: string;
    properties:  ProvenanceProperties;
    required:    string[];
    type:        string;
};

export type ProvenanceProperties = {
    date:                DateClass;
    format:              Format;
    "generation-method": GenerationMethod;
    "generation-period": GenerationPeriod;
    origin:              Origin;
    "origin-geography":  OriginGeography;
    "previous-date":     DateClass;
    source:              DateClass;
    "sub-provenance":    SubProvenance;
};
```