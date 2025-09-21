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

| ID | Name      | Type        | \#    | Description                    |
|----|-----------|-------------|-------|--------------------------------|
| 1  | **meta**  | Metadata    | 0..1  | Information about this package |
| 2  | **types** | Type unique | 1..\* | Types defined in this package  |

**********

Information about this package

**Type: Metadata (Map)**

| ID | Name             | Type            | \#    | Description                               |
|----|------------------|-----------------|-------|-------------------------------------------|
| 1  | **package**      | Namespace       | 1     | Unique name/version of this package       |
| 2  | **version**      | String{1..\*}   | 0..1  | Incrementing version within package       |
| 3  | **title**        | String{1..\*}   | 0..1  | Title                                     |
| 4  | **description**  | String{1..\*}   | 0..1  | Description                               |
| 5  | **comment**      | String{1..\*}   | 0..1  | Comment                                   |
| 6  | **copyright**    | String{1..\*}   | 0..1  | Copyright notice                          |
| 7  | **license**      | String{1..\*}   | 0..1  | SPDX licenseId of this package            |
| 8  | **namespaces**   | PrefixNs unique | 0..\* | Referenced packages                       |
| 9  | **roots**        | TypeName unique | 0..\* | Roots of the type tree(s) in this package |
| 10 | **config**       | Config          | 0..1  | Configuration variables                   |
| 11 | **jadn_version** | Namespace       | 0..1  | JADN Metaschema package                   |

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

**Type: Type (Array)**

| ID | Type                          | \#   | Description            |
|----|-------------------------------|------|------------------------|
| 1  | TypeName                      | 1    | **type_name** -        |
| 2  | Enumerated(enum[JADN-Type])   | 1    | **core_type** -        |
| 3  | TypeOptions(tagId[core_type]) | 0..1 | **type_options** -     |
| 4  | Description                   | 0..1 | **type_description** -  |
| 5  | JADN-Type(tagId[core_type])   | 0..1 | **fields** -           |

**********

**Type: JADN-Type (Choice)**

| ID | Name           | Type   | \# | Description |
|----|----------------|--------|----|-------------|
| 1  | **Binary**     | Empty  | 1  |             |
| 2  | **Boolean**    | Empty  | 1  |             |
| 3  | **Integer**    | Empty  | 1  |             |
| 4  | **Number**     | Empty  | 1  |             |
| 5  | **String**     | Empty  | 1  |             |
| 6  | **Enumerated** | Items  | 1  |             |
| 7  | **Choice**     | Fields | 1  |             |
| 8  | **Array**      | Fields | 1  |             |
| 9  | **ArrayOf**    | Empty  | 1  |             |
| 10 | **Map**        | Fields | 1  |             |
| 11 | **MapOf**      | Empty  | 1  |             |
| 12 | **Record**     | Fields | 1  |             |

**********

**Type: TypeOptions (Choice)**

| ID | Name           | Type           | \# | Description |
|----|----------------|----------------|----|-------------|
| 1  | **Binary**     | BinaryOpts     | 1  |             |
| 2  | **Boolean**    | BooleanOpts    | 1  |             |
| 3  | **Integer**    | IntegerOpts    | 1  |             |
| 4  | **Number**     | NumberOpts     | 1  |             |
| 5  | **String**     | StringOpts     | 1  |             |
| 6  | **Enumerated** | EnumeratedOpts | 1  |             |
| 7  | **Choice**     | ChoiceOpts     | 1  |             |
| 8  | **Array**      | ArrayOpts      | 1  |             |
| 9  | **ArrayOf**    | ArrayOfOpts    | 1  |             |
| 10 | **Map**        | MapOpts        | 1  |             |
| 11 | **MapOf**      | MapOfOpts      | 1  |             |
| 12 | **Record**     | RecordOpts     | 1  |             |

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
| 1  | FieldID     | 1    | **item_id** -          |
| 2  | String      | 0..1 | **item_value** -       |
| 3  | Description | 0..1 | **item_description** -  |

**********

**Type: Field (Array)**

| ID | Type                           | \#   | Description             |
|----|--------------------------------|------|-------------------------|
| 1  | FieldID                        | 1    | **field_id** -          |
| 2  | FieldName                      | 1    | **field_name** -        |
| 3  | TypeRef                        | 1    | **field_type** -        |
| 4  | TypeOptions(tagId[field_type]) | 0..1 | **field_options** -     |
| 5  | Description                    | 0..1 | **field_description** -  |

**********

| Type Name   | Type Definition | Description |
|-------------|-----------------|-------------|
| **FieldID** | Integer=[0, *]  |             |

**********

**Type: FieldOptions (Map)**

| ID | Name          | Type             | \#   | Description |
|----|---------------|------------------|------|-------------|
| 91 | **minOccurs** | Integer=[0, \*]  | 0..1 |             |
| 93 | **maxOccurs** | Integer=[-2, \*] | 0..1 |             |
| 38 | **tagId**     | Integer          | 0..1 |             |
| 75 | **key**       | Boolean          | 0..1 |             |
| 76 | **link**      | Boolean          | 0..1 |             |
| 78 | **not**       | Boolean          | 0..1 |             |

**********

**Type: AllOpts (Map)**

| ID  | Name          | Type    | \#   | Description |
|-----|---------------|---------|------|-------------|
| 48  | **nillable**  | Boolean | 0..1 |             |
| 97  | **abstract**  | Boolean | 0..1 |             |
| 101 | **extends**   | TypeRef | 0..1 |             |
| 114 | **restricts** | TypeRef | 0..1 |             |
| 102 | **final**     | Boolean | 0..1 |             |

**********

**Type: BinaryOpts (Map)**

| ID  | Name          | Type                   | \#   | Description |
|-----|---------------|------------------------|------|-------------|
| 47  | **format**    | ArrayOf(Format) unique | 0..1 |             |
| 123 | **minLength** | Integer                | 0..1 |             |
| 125 | **maxLength** | Integer                | 0..1 |             |
| 117 | **default**   | Binary                 | 0..1 |             |
| 118 | **const**     | Binary                 | 0..1 |             |
| 48  | **nillable**  | Boolean                | 0..1 |             |
| 65  | **attr**      | Boolean                | 0..1 |             |

**********

**Type: BooleanOpts (Map)**

| ID  | Name         | Type    | \#   | Description |
|-----|--------------|---------|------|-------------|
| 117 | **default**  | Boolean | 0..1 |             |
| 118 | **const**    | Boolean | 0..1 |             |
| 48  | **nillable** | Boolean | 0..1 |             |
| 65  | **attr**     | Boolean | 0..1 |             |

**********

**Type: IntegerOpts (Map)**

| ID  | Name             | Type                   | \#   | Description |
|-----|------------------|------------------------|------|-------------|
| 47  | **format**       | ArrayOf(Format) unique | 0..1 |             |
| 69  | **scale**        | Integer                | 0..1 |             |
| 121 | **minInclusive** | Integer                | 0..1 |             |
| 122 | **maxInclusive** | Integer                | 0..1 |             |
| 119 | **minExclusive** | Integer                | 0..1 |             |
| 120 | **maxExclusive** | Integer                | 0..1 |             |
| 117 | **default**      | Integer                | 0..1 |             |
| 118 | **const**        | Integer                | 0..1 |             |
| 48  | **nillable**     | Boolean                | 0..1 |             |
| 65  | **attr**         | Boolean                | 0..1 |             |

**********

**Type: NumberOpts (Map)**

| ID  | Name             | Type                   | \#   | Description |
|-----|------------------|------------------------|------|-------------|
| 47  | **format**       | ArrayOf(Format) unique | 0..1 |             |
| 121 | **minInclusive** | Number                 | 0..1 |             |
| 122 | **maxInclusive** | Number                 | 0..1 |             |
| 119 | **minExclusive** | Number                 | 0..1 |             |
| 120 | **maxExclusive** | Number                 | 0..1 |             |
| 117 | **default**      | Number                 | 0..1 |             |
| 118 | **const**        | Number                 | 0..1 |             |
| 48  | **nillable**     | Boolean                | 0..1 |             |
| 65  | **attr**         | Boolean                | 0..1 |             |

**********

**Type: StringOpts (Map)**

| ID  | Name             | Type                   | \#   | Description |
|-----|------------------|------------------------|------|-------------|
| 47  | **format**       | ArrayOf(Format) unique | 0..1 |             |
| 121 | **minInclusive** | String                 | 0..1 |             |
| 122 | **maxInclusive** | String                 | 0..1 |             |
| 119 | **minExclusive** | String                 | 0..1 |             |
| 120 | **maxExclusive** | String                 | 0..1 |             |
| 37  | **pattern**      | String /regex          | 0..1 |             |
| 123 | **minLength**    | Integer=[0, \*]        | 0..1 |             |
| 125 | **maxLength**    | Integer=[0, \*]        | 0..1 |             |
| 117 | **default**      | String                 | 0..1 |             |
| 118 | **const**        | String                 | 0..1 |             |
| 48  | **nillable**     | Boolean                | 0..1 |             |
| 65  | **attr**         | Boolean                | 0..1 |             |

**********

**Type: EnumeratedOpts (Map extends(AllOpts))**

| ID | Name        | Type    | \#   | Description |
|----|-------------|---------|------|-------------|
| 61 | **id**      | Boolean | 0..1 |             |
| 35 | **enum**    | TypeRef | 0..1 |             |
| 62 | **pointer** | TypeRef | 0..1 |             |
| 65 | **attr**    | Boolean | 0..1 |             |

**********

**Type: ChoiceOpts (Map extends(AllOpts))**

| ID | Name        | Type         | \#   | Description |
|----|-------------|--------------|------|-------------|
| 61 | **id**      | Boolean      | 0..1 |             |
| 67 | **combine** | String{1..1} | 0..1 |             |

**********

**Type: ArrayOpts (Map extends(AllOpts))**

| ID  | Name          | Type                   | \#   | Description |
|-----|---------------|------------------------|------|-------------|
| 47  | **format**    | ArrayOf(Format) unique | 0..1 |             |
| 123 | **minLength** | Integer=[0, \*]        | 0..1 |             |
| 125 | **maxLength** | Integer=[0, \*]        | 0..1 |             |

**********

**Type: ArrayOfOpts (Map extends(AllOpts))**

| ID  | Name          | Type            | \#   | Description |
|-----|---------------|-----------------|------|-------------|
| 42  | **valueType** | TypeRef         | 1    |             |
| 123 | **minLength** | Integer=[0, \*] | 0..1 |             |
| 125 | **maxLength** | Integer=[0, \*] | 0..1 |             |
| 113 | **unique**    | Boolean         | 0..1 |             |
| 115 | **set**       | Boolean         | 0..1 |             |
| 98  | **unordered** | Boolean         | 0..1 |             |

**********

**Type: MapOpts (Map extends(AllOpts))**

| ID  | Name          | Type            | \#   | Description |
|-----|---------------|-----------------|------|-------------|
| 61  | **id**        | Boolean         | 0..1 |             |
| 123 | **minLength** | Integer=[0, \*] | 0..1 |             |
| 125 | **maxLength** | Integer=[0, \*] | 0..1 |             |
| 111 | **sequence**  | Boolean         | 0..1 |             |

**********

**Type: MapOfOpts (Map extends(AllOpts))**

| ID  | Name          | Type            | \#   | Description |
|-----|---------------|-----------------|------|-------------|
| 43  | **keyType**   | TypeRef         | 1    |             |
| 42  | **valueType** | TypeRef         | 1    |             |
| 123 | **minLength** | Integer=[0, \*] | 0..1 |             |
| 125 | **maxLength** | Integer=[0, \*] | 0..1 |             |
| 111 | **sequence**  | Boolean         | 0..1 |             |

**********

**Type: RecordOpts (Map extends(AllOpts))**

| ID  | Name          | Type            | \#   | Description |
|-----|---------------|-----------------|------|-------------|
| 123 | **minLength** | Integer=[0, \*] | 0..1 |             |
| 125 | **maxLength** | Integer=[0, \*] | 0..1 |             |
| 111 | **sequence**  | Boolean         | 0..1 |             |

**********

| Type Name  | Type Definition                         | Description |
|------------|-----------------------------------------|-------------|
| **Format** | String{pattern="^/[a-zA-Z0-9]{1,16}+$"} |             |

**********

| Type Name       | Type Definition | Description |
|-----------------|-----------------|-------------|
| **Description** | String          |             |

**********
