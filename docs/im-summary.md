# What Is Information Modeling

NIST describes Information Modeling [1] as:

> An information model is a representation of concepts, relationships, constraints, rules,
> and operations to specify data semantics for a chosen domain of discourse.
> The advantage of using an information model is that it can provide sharable, stable, and
> organized structure of information requirements for the domain context.
> An information modeling language is a formal syntax that allows users to capture data
> semantics and constraints.  ...  
> 
> In the objected-oriented approach, the fundamental construct is the object, which incorporates both
> data structures and functions. The building blocks in the O-O model are object classes, attributes,
> operations, and associations (relationships.)

Although information modeling is a diverse field, an information modeling language
must be defined precisely using unambiguous terminology.

1. **Class:** a blueprint or template for creating objects. It defines the characteristics
   (data or variables) and behaviors (functions or methods) that objects of that class will possess.
2. **Object:** an instance of a class.
3. **Data Type:** a classification that specifies the kind of value a variable can hold and how the
   computer interprets it. It dictates the operations that can be performed on the data and how much
   memory is allocated for it.
4. **Value:** an instance of a type.

Although the definitions of Class and Type are similar, objects are dynamic while values are static.
* In strongly-typed languages a string value cannot be added to an integer value, but a string object
  and an integer object have methods that determine whether the addition operation is allowed and if
  so how the result is calculated.
* An array value is a collection of values, but an array object's methods define how the collection
  of values is processed (e.g., how values are referenced, added and removed from the collection).


There is a critical distinction between the object-oriented **approach** and an object-oriented
**programming language**:
Every hardware CPU, virtual machine, and programming environment, simply by processing data,
has object classes, attributes, operations and associations:

* **Literals** are constant values (sequences of bytes or characters) suitable for storage and transmission.
* **Objects** hold variable values in a processing environment.
* Input translates literals into object values.
* Output translates object values to literals.
* An object has an information value with operations supported by a processing environment, but
loading, processing and saving information does not require an OOP language.

Example:
* The DEC PDP-11, a 1970's era minicomputer, has memory, registers, operations, and I/O.
Even its 8- and 16-bit values operated on by machine-level instructions are objects:

<img src="images/pdp11i.jpg" width=300>

The semantic meaning of an information value is independent of any literal values used
to represent it.

<img src="images/computers-comms.jpg" width="240">

## References

[1] "Information Modeling: From Design to Implementation", Y. Tina Lee, NIST, September 1999,
https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=821265

[2] "Mastering Classes and Objects", Dev Community,
https://dev.to/singhaayush/mastering-classes-and-objects-step-by-step-for-beginners-28i4