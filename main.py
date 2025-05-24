import os

OPEN_PARS = "(<"
CLOSE_PARS = ")>"

def indent(line: str):
    i = 0
    while line.startswith("    "):
        line = line.removeprefix("    ")
        i += 1
    return i

def get_word(line: str, i: int):
    try:
        return get_words(line)[i - 1]
    except:
        return ""

def add_explicit_protected(line: str):
    if (get_word(line, 1) not in ["public", "private", "protected"]):
        line = (" " * (len(line) - len(line.lstrip()))) + "protected " + line.lstrip()
    return line

def get_words(line: str):
    line = line.strip()
    is_inside_pars = False
    word: str = ""
    words: list[str] = []

    for char in line:
        if char in OPEN_PARS:
            is_inside_pars = True
        elif char in CLOSE_PARS:
            is_inside_pars = False

        word += char
        if (char == " " and not is_inside_pars):
            words.append(word.strip())
            word = ""

    # Add last word if there's anything left
    if word.strip():
        words.append(word.strip())

    return words

def auto_indent(string: str):
    indent = 0
    new_string = ""
    for line in string.split("\n"):
        line = line.strip()
        if line.endswith("}"):
            indent -= 1

        line = "\t"*indent + line

        if line.endswith("{"):
            indent += 1

        new_string += line + "\n"

    return new_string


class Class:
    def __init__(self, filename: str) -> None:
        with open(filename, "r") as f:
            self.java_code = f.readlines()
            self.java_code = map(str.rstrip, self.java_code)

            self.name = ""
            self.methods: list[Method] = []
            self.properties: list[Method] = []
            self.extends = ""

            self.package = ""

            self.get_methods()

    def get_methods(self):
        for line in self.java_code:
            if (line.startswith("package")):
                self.package = get_word(line, 2).rstrip(";")
            elif line.startswith("public class"):
                self.name = get_word(line, 3)
                self.extends = get_word(line, 5)
            elif (indent(line) == 1) and (not line.strip() == "}"):
                if "=" in line or line.endswith(";"):
                    if (len(line.strip()) < 3): continue # Get rid of various ); and }; and so on
                    line = add_explicit_protected(line)

                    # HANDLE PROPERTIES
                    prop = Method()
                    line = line.rstrip(";")
                    line = line.replace("final ", "")
                    line = line.replace("static ", "")

                    prop.signature = get_word(line, 3)
                    prop.set_visibility(get_word(line, 1))
                    prop.return_type = get_word(line, 2)

                    self.properties.append(prop)
                elif "{" in get_words(line):
                    line = add_explicit_protected(line)
                    line = line.replace("static ", "")
                    line = line.replace("synchronized ", "")

                    # HANDLE METHODS
                    method = Method()
                    method.return_type = get_word(line, 2)
                    if (method.return_type.startswith(self.name + "(")):
                        continue
                        # This is the constructor function which we don't care about
                    else:
                        method.set_visibility(get_word(line, 1))
                        method.return_type = get_word(line, 2)
                        method.signature = get_word(line, 3)
                        if (len(method.signature)) == 1:
                            # Generics edgecase
                            method.signature = get_word(line, 4)

                        self.methods.append(method)
    
    def get_stripped(self):
        return map(str.strip, self.java_code)

    def __repr__(self) -> str:
        string = f"class {self.name} {{\n"
        for prop in self.properties:
            string += f"{prop}\n"

        string += "\n"

        for method in self.methods:
            string += f"{method}\n"

        string += "}\n"

        return string

class Method:
    DEFAULT = "~"
    PUBLIC = "+"
    PRIVATE = "-"

    def __init__(self) -> None:
        self.visibility = Method.DEFAULT
        self.signature = ""
        self.return_type = ""

    def __repr__(self) -> str:
        return f"{self.visibility.strip()} {self.return_type.strip()} {self.signature.strip()}"

    def set_visibility(self, vis: str):
        match vis:
            case "public":
                self.visibility = Method.PUBLIC
            case "private":
                self.visibility = Method.PRIVATE
            case _:
                self.visibility = Method.DEFAULT

def main():
    classes: list[str] = []
    for filename in os.listdir("classes"):
        if (filename.endswith(".java")):
            classes.append(filename)

    class_objects: list[Class] = []
    for c in classes:
        class_objects.append(Class(f"classes/{c}"))

    string = "@startuml\n"
    for c in class_objects:
        string += f"{c}"

    for c in class_objects:
        if (c.extends != "" and c.extends + ".java" in classes):
            string += f"{c.extends} <|-- {c.name}\n"

    string += "\n@enduml"
    print(auto_indent(string))

if __name__ == "__main__":
    main()
