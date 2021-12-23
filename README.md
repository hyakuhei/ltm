# ltm
ltm provides a DSL, parser and diagram generator for scene based architectural diagrams. These diagrams are useful for operational readiness reviews, architecture reviews and threat modeling.

In this authors experience (at HP, IBM, Oracle, AWS) architectural models are normally presented with one or two very high level "plumbing" diagrams, lots of boxes with lines that show that _maybe_ these things communicate - but no context as to what they communicate or when. If those details exist in the document, they're usually as verbiage somewhere in the detail section. Occasionally you might find a sequence diagram to eplain a particularly complex thing.

There's a few problems with this. First, the diagrams are unmaintainable, typically drawn in the developers tool of choice and the source for the diagram almost immediately lost. Future presenters of "architecture 2.0" will waste hours re-creating the diagrams or worse, present the old ones with some small note that tells the reviewer "this isn't quite accurate". Second, the big architecture diagram that some developer slaved over, isn't actually that useful. It serves only to set context; you can't tell much at all about the system or how it works from the high level diagram. That's like me showing you a street map of Austin to describe the route the Number 32A bus takes... 

ltm provides a mechanism for creating scene-based "diagrams as code". Being scene based means that the developer focuses on describing specific exchanges of information or transactions that they think are important in the system. ltm will diagram these and will also create a high level context diagram automatically, constructing it from the parts described in each scene. In my experimentation using this it has saved developers significant amounts of time and effort. The automatically generated diagrams also end up being more accurate than if the developer had drawn them deliberately. The reason for this is that when a developer reviews a diagram that "something else" drew, they do so critically, they identify gaps that they would have missed if they drew it themselves and add a scene to fill in the gap.

ltm has a simple DSL for describing architectures, this allows diagrams to be stored as code, and maintained in version control. Teams using ltm will never have to re-invent a diagram, or open an image editor to "add a new box" to the top of an already cramped image because "Lyndsay used to do the diagrams, they left and we don't know what tool they used"...


# Language
Newlines separate statements, one statement per line, no line length limits

Keywords: scene, boundary - these mean something and you can't use them outside of "defined strings"
Special characters: ":" - assigns thing on the right to thing on the left
scene: <name of a scene>
boundary <name of boundary>: <actor in boundary> <another actor in boundary>

Dataflows: describe how one actor talks to another, the format is:
<pitcher> <catcher>: "data" e.g:
```alice bob: "Oh hai"```
Each actor is a single word and case sensitive. ```Bob``` is a different actor to ```bob```

Dataflows can also contain protocol information, described as 'protocol("data")' e.g:
```alice bob: TELNET("Oh Hai")```

Protocols can also be nested e.g:
```server client: IP(TLS(HTTP(HTML("index"))))```

Boundaries can be declared before, or after scenes.

## The LTM process
![Process](https://github.com/hyakuhei/ltm/raw/main/static/User%20generates%20json%20representation.png)

```
scene: "User renders diagrams"
user shell: "cat out.json | python3 jtg.py"
shell python: "load jtg.py"
python python: "Parse json and generate .dot and .png"
python filesystem: "Write .dot files"
python dot: "Call dot to generate .png files"
dot filesystem: "Write .png"
```

## Another example
An online book review site. Unauthenticated users can list books and read reviews. Authenticated users can write reviews.

``` 
scene: "See reviewed books"
User Nginx: TLS(HTTP("GET /"))
Nginx DB: SQL(User,Pass,Query("Get All Books"))
DB Nginx: SQL("All Books")
DB Nginx: TLS(HTTP(HTML("All Books")))

boundary "Internet": User
boundary "Front End": Nginx
boundary "Backend": DB

scene: "User authenticates"
User Nginx: TLS(HTTP("POST /login"))
Nginx DB: SQL(Query("Compare credential hash with stored hash"))
DB Nginx: SQL(True)
Nginx User: TLS(HTTP(Cookie))
```


