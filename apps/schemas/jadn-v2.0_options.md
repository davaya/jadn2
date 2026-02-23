```
         title: "JADN Type and Field Options"
       package: "http://oasis-open.org/openc2/jadn/v2.0/schema/options"
```

**Type: AllTypeOptions (Choice)**

| ID  | Name             | Type    | \# | Description                                                           |
|-----|------------------|---------|----|-----------------------------------------------------------------------|
| 61  | **id**           | Boolean | 1  | = - Enumerated type and Choice/Map/Record keys are ID not Name        |
| 42  | **valueType**    | String  | 1  | * - Value type for ArrayOf and MapOf                                  |
| 43  | **keyType**      | String  | 1  | + - Key type for MapOf                                                |
| 35  | **enum**         | String  | 1  | # - enumeration derived from Array/Choice/Map/Record type             |
| 62  | **pointer**      | String  | 1  | > - enumeration of pointers derived from Array/Choice/Map/Record type |
| 37  | **pattern**      | String  | 1  | % - regular expression that a string must match                       |
| 119 | **minExclusive** | Any     | 1  | w - minimum numeric/string value, excluding bound                     |
| 120 | **maxExclusive** | Any     | 1  | x - maximum numeric/string value, excluding bound                     |
| 121 | **minInclusive** | Any     | 1  | y - minimum numeric/string value                                      |
| 122 | **maxInclusive** | Any     | 1  | z - maximum numeric/string value                                      |
| 117 | **default**      | Any     | 1  | u - Default value                                                     |
| 118 | **const**        | Any     | 1  | v - Constant value                                                    |
| 123 | **minLength**    | Integer | 1  | { - minimum byte or text string length, collection item count         |
| 125 | **maxLength**    | Integer | 1  | } - maximum byte or text string length, collection item count         |
| 113 | **unique**       | Boolean | 1  | q - ArrayOf instance must not contain duplicates                      |
| 115 | **set**          | Boolean | 1  | s - ArrayOf instance is unordered and unique (set)                    |
| 98  | **unordered**    | Boolean | 1  | b - ArrayOf instance is unordered and not unique (bag)                |
| 111 | **sequence**     | Boolean | 1  | o - Map, MapOr or Record instance is ordered and unique (ordered set) |
| 48  | **nillable**     | Boolean | 1  | 0 - Instance may have no value, represented by nil, null, None, etc   |
| 67  | **combine**      | String  | 1  | C - Choice instance is a logical combination (anyOf, allOf, oneOf)    |
| 69  | **scale**        | Integer | 1  | E - fixed point scale factor n, serialized int = value * 10^n         |
| 97  | **abstract**     | Boolean | 1  | a - Inheritance: abstract, non-instantiatable                         |
| 114 | **restricts**    | String  | 1  | r - Inheritance: restriction - subset of referenced type              |
| 101 | **extends**      | String  | 1  | e - Inheritance: extension - superset of referenced type              |
| 102 | **final**        | Boolean | 1  |  - Inheritance: final - cannot have subtype                           |
| 65  | **attr**         | Boolean | 1  | A - Value may be serialized as an XML attribute                       |

**********

**Type: AllFieldOptions (Choice)**

| ID | Name          | Type    | \# | Description                                                             |
|----|---------------|---------|----|-------------------------------------------------------------------------|
| 91 | **minOccurs** | Integer | 1  | [ - min cardinality, default = 1, 0 = field is optional                 |
| 93 | **maxOccurs** | Integer | 1  | ] - max cardinality, default = 1, <0 = inherited or none, not 1 = array |
| 38 | **tagId**     | Integer | 1  | & - field that specifies the type of this field                         |
| 60 | **dir**       | String  | 1  | < - pointer enumeration treats field as a collection                    |
| 75 | **key**       | Boolean | 1  | K - field is the primary key for TypeName                               |
| 76 | **link**      | Boolean | 1  | L - field is a link (foreign key) to an instance of FieldType           |

**********

Any primitive type

**Type: Any (Choice(oneOf))**

| ID | Name | Type    | \# | Description   |
|----|------|---------|----|---------------|
| 1  | **** | Binary  | 1  | **binary** -  |
| 2  | **** | Boolean | 1  | **boolean** -  |
| 3  | **** | Integer | 1  | **integer** -  |
| 4  | **** | Number  | 1  | **number** -  |
| 5  | **** | String  | 1  | **string** -  |

**********
