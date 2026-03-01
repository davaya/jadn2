```
         title: "JADN Metaschema"
       package: "http://oasis-open.org/openc2/jadn/v2.0/schema"
   description: "Syntax of a JSON Abstract Data Notation (JADN) package."
       license: "CC-BY-4.0"
         roots: ["Schema"]
        config: {"$FieldName": "^[$A-Za-z][_A-Za-z0-9]{0,63}$"}
```

Definition of a JADN package

**Type: Schema (Record)**

| ID | Name      | Type     | \#    | Description                    |
|----|-----------|----------|-------|--------------------------------|
| 1  | **meta**  | Metadata | 0..1  | Information about this package |
| 2  | **types** | Type     | 1..\* | Types defined in this package  |

**********

Information about this package

**Type: Metadata (Map)**

| ID | Name             | Type          | \#    | Description                               |
|----|------------------|---------------|-------|-------------------------------------------|
| 1  | **package**      | Namespace     | 1     | Unique name/version of this package       |
| 2  | **namespaces**   | PrefixNs      | 0..\* | Referenced packages                       |
| 3  | **roots**        | TypeName      | 0..\* | Roots of the type tree(s) in this package |
| 4  | **config**       | Config        | 0..1  | Configuration variables                   |
| 5  | **jadn_version** | Namespace     | 0..1  | JADN Metaschema package                   |
| 6  | **version**      | String{1..\*} | 0..1  | Incrementing version within package       |
| 7  | **title**        | String{1..\*} | 0..1  | Title                                     |
| 8  | **description**  | String{1..\*} | 0..1  | Description                               |
| 9  | **comment**      | String{1..\*} | 0..1  | Comment                                   |
| 10 | **copyright**    | String{1..\*} | 0..1  | Copyright notice                          |
| 11 | **license**      | String{1..\*} | 0..1  | SPDX licenseId of this package            |

**********

Prefix corresponding to a namespace IRI

**Type: PrefixNs (Array)**

| ID | Type      | \# | Description                          |
|----|-----------|----|--------------------------------------|
| 1  | NSID      | 1  | **prefix** - Namespace prefix string |
| 2  | Namespace | 1  | **namespace** - Namespace IRI        |

**********

Config vars override JADN defaults

**Type: Config (Map{1..\*})**

| ID | Name             | Type            | \#   | Description                                  |
|----|------------------|-----------------|------|----------------------------------------------|
| 1  | **$MaxBinary**   | Integer=[1, \*] | 0..1 | Package max octets, default = 255            |
| 2  | **$MaxString**   | Integer=[1, \*] | 0..1 | Package max characters, default = 255        |
| 3  | **$MaxElements** | Integer=[1, \*] | 0..1 | Package max items/properties, default = 255  |
| 4  | **$Sys**         | String{1..1}    | 0..1 | System character for TypeName, default = '.' |
| 5  | **$TypeName**    | String /regex   | 0..1 | Default = ^[A-Z][-.A-Za-z0-9]{0,63}$         |
| 6  | **$FieldName**   | String /regex   | 0..1 | Default = ^[a-z][_A-Za-z0-9]{0,63}$          |
| 7  | **$NSID**        | String /regex   | 0..1 | Default = ^([A-Za-z][A-Za-z0-9]{0,7})?$      |

**********

| Type Name     | Type Definition | Description              |
|---------------|-----------------|--------------------------|
| **Namespace** | String /uri     | Unique name of a package |

**********

| Type Name | Type Definition         | Description                     |
|-----------|-------------------------|---------------------------------|
| **NSID**  | String{pattern="$NSID"} | Namespace prefix matching $NSID |

**********

| Type Name    | Type Definition             | Description            |
|--------------|-----------------------------|------------------------|
| **TypeName** | String{pattern="$TypeName"} | Name of a logical type |

**********

| Type Name     | Type Definition              | Description                          |
|---------------|------------------------------|--------------------------------------|
| **FieldName** | String{pattern="$FieldName"} | Name of a field in a structured type |

**********

| Type Name   | Type Definition | Description                                          |
|-------------|-----------------|------------------------------------------------------|
| **TypeRef** | String          | Reference to a type, matching ($NSID ':')? $TypeName |

**********

Fixed structure for all type definitions

**Type: Type (Array)**

| ID | Type                          | \#   | Description                                               |
|----|-------------------------------|------|-----------------------------------------------------------|
| 1  | TypeName                      | 1    | **type_name** - Schema-defined type name                  |
| 2  | Enumerated(enum[JADN-Type])   | 1    | **core_type** - Core (JADN-defined) type name             |
| 3  | TypeOptions(tagId[core_type]) | 0..1 | **type_options** - Required/allowed options for core type |
| 4  | Description                   | 0..1 | **type_description** - Comments/Documentation             |
| 5  | JADN-Type(tagId[core_type])   | 0..1 | **fields** - Fields, Items, or nothing more for core type |

**********

Fields applicable for each core type

**Type: JADN-Type (Choice)**

| ID | Name           | Type   | \# | Description |
|----|----------------|--------|----|-------------|
| 1  | **Binary**     | Empty  | 1  |             |
| 2  | **Boolean**    | Empty  | 1  |             |
| 3  | **Integer**    | Empty  | 1  |             |
| 4  | **Number**     | Empty  | 1  |             |
| 5  | **String**     | Empty  | 1  |             |
| 6  | **Array**      | Fields | 1  |             |
| 7  | **ArrayOf**    | Empty  | 1  |             |
| 8  | **Map**        | Fields | 1  |             |
| 9  | **MapOf**      | Empty  | 1  |             |
| 10 | **Record**     | Fields | 1  |             |
| 11 | **Enumerated** | Items  | 1  |             |
| 12 | **Choice**     | Fields | 1  |             |

**********

Required/allowed options for each core type

**Type: TypeOptions (Choice)**

| ID | Name           | Type           | \# | Description |
|----|----------------|----------------|----|-------------|
| 1  | **Binary**     | BinaryOpts     | 1  |             |
| 2  | **Boolean**    | BooleanOpts    | 1  |             |
| 3  | **Integer**    | IntegerOpts    | 1  |             |
| 4  | **Number**     | NumberOpts     | 1  |             |
| 5  | **String**     | StringOpts     | 1  |             |
| 6  | **Array**      | ArrayOpts      | 1  |             |
| 7  | **ArrayOf**    | ArrayOfOpts    | 1  |             |
| 8  | **Map**        | MapOpts        | 1  |             |
| 9  | **MapOf**      | MapOfOpts      | 1  |             |
| 10 | **Record**     | RecordOpts     | 1  |             |
| 11 | **Enumerated** | EnumeratedOpts | 1  |             |
| 12 | **Choice**     | ChoiceOpts     | 1  |             |

**********

| Type Name | Type Definition | Description |
|-----------|-----------------|-------------|
| **Empty** | Array{0..0}     |             |

**********

| Type Name | Type Definition | Description |
|-----------|-----------------|-------------|
| **Items** | ArrayOf(Item)   |             |

**********

| Type Name  | Type Definition | Description |
|------------|-----------------|-------------|
| **Fields** | ArrayOf(Field)  |             |

**********

**Type: Item (Array)**

| ID | Type        | \#   | Description            |
|----|-------------|------|------------------------|
| 1  | Integer     | 1    | **item_id** -          |
| 2  | String      | 0..1 | **item_value** -       |
| 3  | Description | 0..1 | **item_description** -  |

**********

**Type: Field (Array)**

| ID | Type                            | \#   | Description             |
|----|---------------------------------|------|-------------------------|
| 1  | Integer=[1, \*]                 | 1    | **field_id** -          |
| 2  | FieldName                       | 1    | **field_name** -        |
| 3  | TypeRef                         | 1    | **field_type** -        |
| 4  | FieldOptions(tagId[field_type]) | 0..1 | **field_options** -     |
| 5  | Description                     | 0..1 | **field_description** -  |

**********

**Type: FieldOptions (Map extends(TypeOptions) ?{'tagString': 'JADNOpts'}?)**

| ID | Name          | Type            | \#   | Description                                                            |
|----|---------------|-----------------|------|------------------------------------------------------------------------|
| 91 | **minOccurs** | Integer=[0, \*] | 0..1 | [: min cardinality, default = 1, 0 = field is optional                 |
| 93 | **maxOccurs** | Integer=[0, \*] | 0..1 | ]: max cardinality, default = 1, <0 = inherited or none, not 1 = array |
| 38 | **tagId**     | Integer=[1, \*] | 0..1 | &: field that specifies the type of this field                         |
| 60 | **dir**       | Boolean         | 0..1 | <: pointer enumeration treats field as a collection                    |
| 75 | **key**       | Boolean         | 0..1 | K: field is the primary key for TypeName                               |
| 76 | **link**      | Boolean         | 0..1 | L: field is a link (foreign key) to an instance of FieldType           |

**********

**Type: BinaryOpts (Map ?{'tagString': 'JADNOpts'}?)**

| ID  | Name          | Type    | \#   | Description |
|-----|---------------|---------|------|-------------|
| 47  | **format**    | Format  | 0..1 |             |
| 123 | **minLength** | Integer | 0..1 |             |
| 125 | **maxLength** | Integer | 0..1 |             |
| 117 | **default**   | Binary  | 0..1 |             |
| 118 | **const**     | Binary  | 0..1 |             |
| 48  | **nillable**  | Boolean | 0..1 |             |
| 65  | **attr**      | Boolean | 0..1 |             |

**********

**Type: BooleanOpts (Map ?{'tagString': 'JADNOpts'}?)**

| ID  | Name         | Type    | \#   | Description |
|-----|--------------|---------|------|-------------|
| 47  | **format**   | Format  | 0..1 |             |
| 117 | **default**  | Boolean | 0..1 |             |
| 118 | **const**    | Boolean | 0..1 |             |
| 48  | **nillable** | Boolean | 0..1 |             |
| 65  | **attr**     | Boolean | 0..1 |             |

**********

**Type: IntegerOpts (Map ?{'tagString': 'JADNOpts'}?)**

| ID  | Name             | Type    | \#   | Description |
|-----|------------------|---------|------|-------------|
| 47  | **format**       | Format  | 0..1 |             |
| 69  | **scale**        | Integer | 0..1 |             |
| 121 | **minInclusive** | Integer | 0..1 |             |
| 122 | **maxInclusive** | Integer | 0..1 |             |
| 119 | **minExclusive** | Integer | 0..1 |             |
| 120 | **maxExclusive** | Integer | 0..1 |             |
| 117 | **default**      | Integer | 0..1 |             |
| 118 | **const**        | Integer | 0..1 |             |
| 48  | **nillable**     | Boolean | 0..1 |             |
| 65  | **attr**         | Boolean | 0..1 |             |

**********

**Type: NumberOpts (Map ?{'tagString': 'JADNOpts'}?)**

| ID  | Name             | Type    | \#   | Description |
|-----|------------------|---------|------|-------------|
| 47  | **format**       | Format  | 0..1 |             |
| 121 | **minInclusive** | Number  | 0..1 |             |
| 122 | **maxInclusive** | Number  | 0..1 |             |
| 119 | **minExclusive** | Number  | 0..1 |             |
| 120 | **maxExclusive** | Number  | 0..1 |             |
| 117 | **default**      | Number  | 0..1 |             |
| 118 | **const**        | Number  | 0..1 |             |
| 48  | **nillable**     | Boolean | 0..1 |             |
| 65  | **attr**         | Boolean | 0..1 |             |

**********

**Type: StringOpts (Map ?{'tagString': 'JADNOpts'}?)**

| ID  | Name             | Type            | \#   | Description |
|-----|------------------|-----------------|------|-------------|
| 47  | **format**       | Format          | 0..1 |             |
| 121 | **minInclusive** | String          | 0..1 |             |
| 122 | **maxInclusive** | String          | 0..1 |             |
| 119 | **minExclusive** | String          | 0..1 |             |
| 120 | **maxExclusive** | String          | 0..1 |             |
| 37  | **pattern**      | String /regex   | 0..1 |             |
| 123 | **minLength**    | Integer=[0, \*] | 0..1 |             |
| 125 | **maxLength**    | Integer=[0, \*] | 0..1 |             |
| 117 | **default**      | String          | 0..1 |             |
| 118 | **const**        | String          | 0..1 |             |
| 48  | **nillable**     | Boolean         | 0..1 |             |
| 65  | **attr**         | Boolean         | 0..1 |             |

**********

**Type: AllOpts (Map ?{'tagString': 'JADNOpts'}?)**

| ID  | Name          | Type    | \#   | Description |
|-----|---------------|---------|------|-------------|
| 48  | **nillable**  | Boolean | 0..1 |             |
| 97  | **abstract**  | Boolean | 0..1 |             |
| 101 | **extends**   | TypeRef | 0..1 |             |
| 114 | **restricts** | TypeRef | 0..1 |             |
| 102 | **final**     | Boolean | 0..1 |             |

**********

**Type: ArrayOpts (Map extends(AllOpts) ?{'tagString': 'JADNOpts'}?)**

| ID  | Name          | Type            | \#   | Description |
|-----|---------------|-----------------|------|-------------|
| 47  | **format**    | Format          | 0..1 |             |
| 123 | **minLength** | Integer=[0, \*] | 0..1 |             |
| 125 | **maxLength** | Integer=[0, \*] | 0..1 |             |

**********

**Type: ArrayOfOpts (Map extends(AllOpts) ?{'tagString': 'JADNOpts'}?)**

| ID  | Name          | Type            | \#   | Description |
|-----|---------------|-----------------|------|-------------|
| 42  | **valueType** | TypeRef         | 1    |             |
| 123 | **minLength** | Integer=[0, \*] | 0..1 |             |
| 125 | **maxLength** | Integer=[0, \*] | 0..1 |             |
| 113 | **unique**    | Boolean         | 0..1 |             |
| 115 | **set**       | Boolean         | 0..1 |             |
| 98  | **unordered** | Boolean         | 0..1 |             |

**********

**Type: MapOpts (Map extends(AllOpts) ?{'tagString': 'JADNOpts'}?)**

| ID  | Name          | Type            | \#   | Description |
|-----|---------------|-----------------|------|-------------|
| 61  | **id**        | Boolean         | 0..1 |             |
| 123 | **minLength** | Integer=[0, \*] | 0..1 |             |
| 125 | **maxLength** | Integer=[0, \*] | 0..1 |             |
| 111 | **sequence**  | Boolean         | 0..1 |             |
| 116 | **tagString** | String          | 0..1 |             |

**********

**Type: MapOfOpts (Map extends(AllOpts) ?{'tagString': 'JADNOpts'}?)**

| ID  | Name          | Type            | \#   | Description |
|-----|---------------|-----------------|------|-------------|
| 43  | **keyType**   | TypeRef         | 1    |             |
| 42  | **valueType** | TypeRef         | 1    |             |
| 123 | **minLength** | Integer=[0, \*] | 0..1 |             |
| 125 | **maxLength** | Integer=[0, \*] | 0..1 |             |
| 111 | **sequence**  | Boolean         | 0..1 |             |

**********

**Type: RecordOpts (Map extends(AllOpts) ?{'tagString': 'JADNOpts'}?)**

| ID  | Name          | Type            | \#   | Description |
|-----|---------------|-----------------|------|-------------|
| 123 | **minLength** | Integer=[0, \*] | 0..1 |             |
| 125 | **maxLength** | Integer=[0, \*] | 0..1 |             |
| 111 | **sequence**  | Boolean         | 0..1 |             |

**********

**Type: EnumeratedOpts (Map extends(AllOpts) ?{'tagString': 'JADNOpts'}?)**

| ID | Name        | Type    | \#   | Description |
|----|-------------|---------|------|-------------|
| 61 | **id**      | Boolean | 0..1 |             |
| 35 | **enum**    | TypeRef | 0..1 |             |
| 62 | **pointer** | TypeRef | 0..1 |             |
| 65 | **attr**    | Boolean | 0..1 |             |

**********

**Type: ChoiceOpts (Map extends(AllOpts) ?{'tagString': 'JADNOpts'}?)**

| ID | Name        | Type    | \#   | Description |
|----|-------------|---------|------|-------------|
| 61 | **id**      | Boolean | 0..1 |             |
| 67 | **combine** | Combine | 0..1 |             |

**********

JADN type and field option IDs/Names for tag-string serialization

**Type: JADNOpts (Enumerated)**

| ID  | Item             | Description                                                                            |
|-----|------------------|----------------------------------------------------------------------------------------|
| 61  | **id**           | '=', Boolean: Enumerated type and Choice/Map/Record keys are ID not Name               |
| 42  | **valueType**    | '*', TypeRef: Value type for ArrayOf and MapOf                                         |
| 43  | **keyType**      | '+', TypeRef: Key type for MapOf                                                       |
| 35  | **enum**         | '#', TypeRef: enumeration derived from Array/Choice/Map/Record type                    |
| 62  | **pointer**      | '>', TypeRef: enumeration of pointers derived from Array/Choice/Map/Record type        |
| 37  | **pattern**      | '%', String: regular expression that a string must match                               |
| 117 | **default**      | 'u', *: Default value                                                                  |
| 118 | **const**        | 'v', *: Constant value                                                                 |
| 119 | **minExclusive** | 'w', *: minimum numeric/string value, excluding bound                                  |
| 120 | **maxExclusive** | 'x', *: maximum numeric/string value, excluding bound                                  |
| 121 | **minInclusive** | 'y', *: minimum numeric/string value                                                   |
| 122 | **maxInclusive** | 'z', *: maximum numeric/string value                                                   |
| 123 | **minLength**    | '{', Integer: minimum byte or text string length, collection item count                |
| 125 | **maxLength**    | '}', Integer: maximum byte or text string length, collection item count                |
| 113 | **unique**       | 'q', Boolean: ArrayOf instance must not contain duplicates (ordered set)               |
| 115 | **set**          | 's', Boolean: ArrayOf instance is unordered and unique (set)                           |
| 98  | **unordered**    | 'b', Boolean: ArrayOf instance is unordered and not unique (bag)                       |
| 111 | **sequence**     | 'o', Boolean: Map, MapOf or Record instance is ordered and unique (ordered keys)       |
| 48  | **nillable**     | '0', Boolean: Instance may have no value, represented by nil, null, None, etc.         |
| 67  | **combine**      | 'C', Combine: Choice is a logical combination (1: allOf, 2: anyOf, 3: oneOf, 4: diff)  |
| 47  | **format**       | '/', Format: semantic validation keyword, may affect serialization                     |
| 69  | **scale**        | 'E', Integer: fixed point scale factor n, serialized int = value * 10^n                |
| 116 | **tagString**    | 't', TypeRef: use referenced type for tag-string serialization                         |
| 97  | **abstract**     | 'a', Boolean: Inheritance: non-instantiatable                                          |
| 114 | **restricts**    | 'r', TypeRef: Inheritance: subset of referenced type                                   |
| 101 | **extends**      | 'e', TypeRef: Inheritance: superset of referenced type                                 |
| 102 | **final**        | f', Boolean: Inheritance: cannot have subtype                                          |
| 65  | **attr**         | 'A', Boolean: Value may be serialized as an XML attribute                              |
| 84  | **typeOpts**     | 'T', --Sentinel--: preceding items are Type Options, following items are Field Options |
| 91  | **minOccurs**    | '[', Integer: min cardinality, default = 1, 0 = field is optional                      |
| 93  | **maxOccurs**    | ']', Integer: max cardinality, default = 1, <0 = inherited or none, not 1 = array      |
| 38  | **tagId**        | '&', Integer: field that specifies the type of this field                              |
| 60  | **dir**          | '<', Boolean: pointer enumeration treats field as a collection                         |
| 75  | **key**          | 'K', Boolean: field is the primary key for TypeName                                    |
| 76  | **link**         | 'L', Boolean: field is a link (foreign key) to an instance of FieldType                |

**********

| Type Name  | Type Definition                        | Description |
|------------|----------------------------------------|-------------|
| **Format** | String{pattern="^[a-zA-Z0-9]{1,16}+$"} |             |

**********

**Type: Description (Choice(3))**

| ID | Name | Type       | \# | Description                     |
|----|------|------------|----|---------------------------------|
| 1  | **** | String     | 1  | **str** - Text String           |
| 2  | **** | Annotation | 1  | **anno** - Type-labeled strings |

**********

**Type: Annotation (Map)**

| ID | Name    | Type   | \# | Description    |
|----|---------|--------|----|----------------|
| 1  | **md**  | String | 1  | MarkDown text  |
| 2  | **xml** | String | 1  | XML annotation |

**********

Untagged Union combining function

**Type: Combine (Enumerated)**

| ID | Item      | Description |
|----|-----------|-------------|
| 1  | **allOf** |             |
| 2  | **anyOf** |             |
| 3  | **oneOf** |             |
| 4  | **diff**  |             |

**********
