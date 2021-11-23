# ltm
ltm provides a DSL, parser and diagram generator for scene based architectural diagrams. These diagrams are useful for operational readiness reviews, architecture reviews and threat modeling.

In this authors experience (at HP, IBM, Oracle, AWS) architectural models are normally presented with one or two very high level "plumbing" diagrams, lots of boxes with lines that show that _maybe_ these things communicate - but no context as to what they communicate or when. If those details exist in the document, they're usually as verbiage somewhere in the detail section. Occasionally you might find a sequence diagram to eplain a particularly complex thing.

There's a few problems with this. First, the diagrams are unmaintainable, typically drawn in the developers tool of choice and the source for the diagram almost immediately lost. Future presenters of "architecture 2.0" will waste hours re-creating the diagrams or worse, present the old ones with some small note that tells the reviewer "this isn't quite accurate". Second, the big architecture diagram that some developer slaved over, isn't actually that useful. It serves only to set context; you can't tell much at all about the system or how it works from the high level diagram. That's like me showing you a street map of Austin to describe the route the Number 32A bus takes... 

ltm provides a mechanism for creating scene-based "diagrams as code". Being scene based means that the developer focuses on describing specific exchanges of information or transactions that they think are important in the system. ltm will diagram these and will also create a high level context diagram automatically, constructing it from the parts described in each scene. In my experimentation using this it has saved developers significant amounts of time and effort. The automatically generated diagrams also end up being more accurate than if the developer had drawn them deliberately. The reason for this is that when a developer reviews a diagram that "something else" drew, they do so critically, they identify gaps that they would have missed if they drew it themselves and add a scene to fill in the gap.

ltm has a simple DSL for describing architectures, this allows diagrams to be stored as code, and maintained in version control. Teams using ltm will never have to re-invent a diagram, or open an image editor to "add a new box" to the top of an already cramped image because "Lyndsay used to do the diagrams, they left and we don't know what tool they used"...


# Language
Newlines separate statements, one statement per line, no line length limits

Actors, data, transports, boundaries, are all created and manipulated using Keywords - Keywords in ltm are always capitalized.
Any keyword created variable exists within a global context.

## Reference example
An online book review site. Unauthenticated users can list books and read reviews. Authenticated users can write reviews.

## Version 0.1
| Keyword | Parameter | Meaning | 
| ------- | --------| --- |
| //      | Everything after | a comment, everything after // is ignored |
| ACTOR   | Single Word | An entity in the diagram |
| TRANSPORT | Single Word | A mechanism for moving data from one actor to another. |
| DATA    | Single Word | A piece of data - which can be owned by an actor and sent via a transport |
| BOUNDARY | Single Word | A logical trust boundary - this could be physical like a wall, or virtual like a vlan it depends on the architecture |
| SEND | Acts on Actor to Left and Right of SEND | An instruction to send some data, from an actor, to an actor, possibly using a specific transport |
| IN | Single Word | Tells an entity that it is within a Boundary. |
| EXEC | Everything after | Tells an entity to perform an instruction, often used for notes about important computation |
| USE | Single Word | <Optional> can be used with SEND to describe which transport to use |

ltm reads like a recipie book from the 1920's statements are instructions of what to do.

### Example
In version 0.1 the goal is to build a very simple language, with no shortcuts or convienence features.

``` 
ACTOR User // Create an actor called User
ACTOR Nginx // Create an actor called Nginx
DATA Credentials // Credentials exists as an entity that can be moved around
TRANSPORT TLS // Create a transport called TLS (later this will be a built-in)

```

## Version 0.2
Introduces 
IS - to set properties

