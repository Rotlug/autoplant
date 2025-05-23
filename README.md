# autoplant

autoplant is a very primitive tool that converts a bunch of .java files into a PlantUML diagram

### Limitations

- Doesn't support grouping variables together
  for example:

```java
float x, y = 0;
```

- Only works on public classes

### How to use

1. close this repo
2. make a "classes" folder
3. put all your .java files in the classes folder
4. run this command:

```bash
python main.py > uml.puml
```

5. then export your diagram like this:

```bash
plantuml -tsvg uml.puml
```

(You need to have plantuml installed)
