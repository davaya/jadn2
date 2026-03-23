# JSON Abstract Data Notation: JADN

## Status of This Memo

This document specifies an Internet standards track protocol for the
Internet community, and requests discussion and suggestions for
improvements.  Please refer to the current edition of the "Internet
Official Protocol Standards" (STD 1) for the standardization state
and status of this protocol.  Distribution of this memo is unlimited.

## Abstract

This document defines JSON Abstract Data Notation (JADN), an information
modeling language designed to improve the rigor of Internet technical
specifications. Existing standards like ABNF, XSD, and JSON Schema
define formal syntax for text and structured data values.
But while RFC 3444 and RFC 8477 establish goals for information modeling,
adoption remains limited.
JADN addresses this by introducing a regular structure for information types
that balances simplicity with extensibility and expressive power.
The key feature of any IM is equivalence across data formats, and unlike
traditional schema languages, a JADN schema is itself an information value.
This ensures equivalence across schema formats, allowing authors to select
or design a representation suitable for the application and target audience.

## Introduction

RFC3444 begins: "There has been ongoing confusion about the differences
between Information Models and Data Models for defining managed objects in
network management." The confusion can be partially attributed to the absence of a
definition of information itself, so this specification begins with two definitions::

* **Information (Information Technology)**: structured, processed data that has
been given context, meaning, and semantics within a specific domain.
It turns raw facts into usable knowledge by organizing data objects, their
attributes, and their relationships, typically at a high level of abstraction,
independent of physical storage protocols.

* **Information (Information Theory)**: the reduction of uncertainty, measured
as the statistical rarity of a message rather than its semantic meaning.
It quantifies how much a data point reduces doubt, measured in bits.

Given a literal value (the fixed sequence of bytes in a document or message,
the "data object" or "data point" in these definitions), the information
in that literal can be viewed as the questions it answers. An information
model (IM) defines equivalence between literals, and a concise literal
such as an RFC 791 IP packet contains the identical information (both semantics
and entropy) as an equivalent verbose literal in a format such as XML.

<!--
NIST describes [[Information Modeling](#information-modeling)] as:

> An information model is a representation of concepts, relationships, constraints, rules,
> and operations to specify data semantics for a chosen domain of discourse.
> The advantage of using an information model is that it can provide sharable, stable, and
> organized structure of information requirements for the domain context.
>
> An information modeling language is a formal syntax that allows users to capture data
> semantics and constraints.

This hints at the primary reasons for using information models:

1. **High Level** - for an IM to be broadly sharable and stable, it should be a high level
specification that separates information sharing requirements from implementation details.
This makes an IM desirable for initial conceptual design where details are unknown or undecided,
for exposition and publication where they are distracting, as well as for implementation
where unambiguous specification of details using a formal syntax is essential
for robustness and interoperability.
2. **Language Independent** - an information modeling language defines information in a way that
is representation-independent both within a process and when stored or communicated among processes.
Because an IM is requirements-focused, a single specification applies to many processing environments
and data formats, ensuring that they can deliver equivalent results.

This document is the reference specification for the JADN information modeling language.
See [[JADN-CN](#jadn-cn)] for additional detail on the information modeling
process and how to construct and use JADN information models.
While the term information modeling is used broadly and covers a range of applications, a JADN
information model defines the essential content of discrete data items used in computing
independently of how that content is represented for processing, communication or storage.
* **Essential content** (meaning) is expressed using model definitions and quantified by
information theory, where the amount of information conveyed in a message is not directly related
to the size or format of the message.
* **Data items** (literals: documents, messages, protocol data units, data structures, etc.)
are mapped to information values using explicit and unambiguous encoding rules.

[[Unified Modeling Language (UML)](#uml)] provides a standardized visual way to model and document
software systems, encompassing both their structure and behavior:

> *The objective of UML is to provide system architects, software engineers, and software developers
with tools for analysis, design, and implementation of software-based systems as well as for modeling
business and similar processes.*

JADN can be described as a UML profile for data items, formally defining the content of data used
in software-based systems.
UML's organizing principle is classification, and among its classifiers are class and datatype:
* **Class**: Instances of a class are objects that model operations and behavior, including the
behavior of variables within a process. This does not imply use of an object-oriented
programming language; objects implement any variable in any language.
* **Datatype**: Datatype differs from class in that instances of a datatype are identified only by
their value. All instances of a datatype with the same value are considered to be equal instances.
A datatype instance is a constant because by definition a different value is a different instance.
A value may be classified as an instance of multiple datatypes, but value comparison is meaningful
only among instances of the same type.

A class is a programming language's mechanism for implementing variables, while a type defines the
set of values an object of that type may have, as defined in 
**XML Schema Definition Language** [[XSD](#xsd)]:

> A datatype has three properties:
>  * A **value space**, which is a set of values.
>  * A **lexical space**, which is a set of **literals** used to denote the **values**.
>  * A **lexical mapping**, which is a mapping from the **lexical space** into the **value space**,
>    and a small collection of functions, relations, and procedures associated with the datatype,
>    including equality and (for some datatypes) order relations on the value space.

An information model is constructed from datatypes, not classes, because its purpose is to compare
literals for equivalence based on their information values, and only datatypes provide the necessary
linkage between typed variables and messages that can be compared and validated for content and integrity.

-->