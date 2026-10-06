"""Generate 5 sample 'Python Programming Notes' chapter PDFs into ./sample_pdfs.

Usage:  python scripts/generate_sample_pdfs.py
(Requires: pip install reportlab)
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, Preformatted, SimpleDocTemplate, Spacer

OUT = Path(__file__).resolve().parent.parent / "sample_pdfs"
OUT.mkdir(exist_ok=True)

CHAPTERS = {
    "chapter_1_introduction_to_python": ("Chapter 1 - Introduction to Python", [
        ("h", "What is Python?"),
        ("p", "Python is a high-level, interpreted, general-purpose programming language created by Guido van Rossum "
              "and first released in 1991. It is famous for its clean and readable syntax, which makes it one of the "
              "best first languages for beginners. Python is used in web development, data science, artificial "
              "intelligence, automation, scripting and many other fields."),
        ("h", "Key Features of Python"),
        ("ul", ["Easy to read and write: code looks close to plain English.",
                "Interpreted: code runs line by line, so there is no separate compile step.",
                "Dynamically typed: you do not declare the type of a variable.",
                "Large standard library and a huge ecosystem of third-party packages (NumPy, pandas, FastAPI).",
                "Cross-platform: the same program runs on Windows, macOS and Linux."]),
        ("h", "Installing and Running Python"),
        ("p", "Download Python from python.org and check the installation from the terminal. You can type code "
              "directly in the interactive shell (REPL) or save it in a file ending in .py and run it."),
        ("code", "python --version        # check the installed version\npython                    # start the interactive shell\npython hello.py           # run a script file"),
        ("h", "Your First Program"),
        ("p", "The print() function displays output on the screen. A line starting with # is a comment: Python "
              "ignores it, and programmers use comments to explain their code."),
        ("code", "# My first Python program\nprint(\"Hello, World!\")\nname = input(\"What is your name? \")\nprint(\"Welcome to Python,\", name)"),
        ("h", "Indentation Matters"),
        ("p", "Unlike many languages that use curly braces, Python uses indentation (usually 4 spaces) to define "
              "blocks of code. Wrong indentation causes an IndentationError."),
        ("h", "How Python Runs Your Code"),
        ("p", "When you run a program, the Python interpreter first translates your source code into bytecode and "
              "then the Python Virtual Machine (PVM) executes that bytecode, one instruction at a time."),
    ]),
    "chapter_2_variables_and_data_types": ("Chapter 2 - Variables and Data Types", [
        ("h", "What are Python Variables?"),
        ("p", "A variable is a name that refers to a value stored in memory. You create a variable by assigning a "
              "value with the = operator. Python is dynamically typed, so the same name can later refer to a value "
              "of a different type. Variable names can contain letters, digits and underscores, cannot start with "
              "a digit, and are case-sensitive. The convention is snake_case, for example student_name."),
        ("code", "age = 20            # int\nprice = 99.5        # float\nname = \"Ayesha\"      # str\nis_student = True   # bool\nnothing = None      # NoneType\nprint(type(age))    # <class 'int'>"),
        ("h", "Basic Data Types"),
        ("ul", ["int: whole numbers such as 10 or -3.",
                "float: decimal numbers such as 3.14.",
                "str: text inside quotes, such as 'Python'.",
                "bool: True or False.",
                "NoneType: the special value None meaning 'no value'."]),
        ("p", "Type conversion (casting) changes a value from one type to another using int(), float(), str() "
              "and bool(). For example int('42') gives the number 42. F-strings make it easy to put variables "
              "inside text."),
        ("code", "score = int(\"85\")\nprint(f\"{name} scored {score} marks\")"),
        ("h", "Collection Data Types"),
        ("ul", ["list: an ordered, mutable collection written with square brackets [1, 2, 3].",
                "tuple: an ordered, immutable collection written with parentheses (1, 2, 3).",
                "dict: key-value pairs written with curly braces {'name': 'Ali'}.",
                "set: an unordered collection of unique items {1, 2, 3}."]),
        ("h", "Difference Between a List and a Tuple"),
        ("p", "The main difference is mutability. A list is mutable, which means you can add, remove or change its "
              "items after creation. A tuple is immutable, so once it is created it cannot be changed. Lists use "
              "square brackets and tuples use parentheses. Because tuples are fixed, they are slightly faster, use "
              "less memory and can be used as dictionary keys. Use a list for data that changes (a shopping cart) "
              "and a tuple for fixed data (coordinates or days of the week)."),
        ("code", "fruits = [\"apple\", \"banana\"]\nfruits.append(\"mango\")     # works: lists are mutable\nfruits[0] = \"kiwi\"          # works\n\npoint = (10, 20)\n# point[0] = 5               # TypeError: tuples are immutable"),
    ]),
    "chapter_3_conditional_statements": ("Chapter 3 - Conditional Statements", [
        ("h", "What are Conditional Statements?"),
        ("p", "Conditional statements let a program make decisions. The program checks a condition, which is an "
              "expression that evaluates to True or False, and runs different code depending on the result. "
              "Python provides the if, elif and else keywords for this purpose."),
        ("code", "marks = 72\nif marks >= 80:\n    print(\"Grade A\")\nelif marks >= 60:\n    print(\"Grade B\")\nelse:\n    print(\"Grade C\")"),
        ("h", "How if, elif and else Work"),
        ("ul", ["if: runs its block when the condition is True.",
                "elif (else if): checked only when the previous conditions were False.",
                "else: runs when none of the conditions were True; it is optional.",
                "Only the first block whose condition is True is executed."]),
        ("h", "Comparison and Logical Operators"),
        ("p", "Conditions are built with comparison operators: ==, !=, >, <, >= and <=. They can be combined with "
              "the logical operators and, or and not. Remember that = assigns a value while == compares two values."),
        ("code", "age = 19\nhas_id = True\nif age >= 18 and has_id:\n    print(\"You may enter\")\nif not has_id:\n    print(\"ID required\")"),
        ("h", "Nested Conditions and the Ternary Expression"),
        ("p", "An if statement can be placed inside another if statement. Python also offers a one-line "
              "conditional expression: value_if_true if condition else value_if_false."),
        ("code", "status = \"Pass\" if marks >= 40 else \"Fail\""),
        ("h", "Truthy and Falsy Values"),
        ("p", "Every Python value can be used as a condition. Falsy values are False, None, 0, 0.0, empty strings, "
              "empty lists, empty tuples and empty dictionaries. Everything else is truthy. For example "
              "if my_list: is True only when the list has items."),
        ("h", "The match Statement"),
        ("p", "Since Python 3.10 the match statement provides pattern matching, similar to switch in other languages."),
        ("code", "day = 3\nmatch day:\n    case 1:\n        print(\"Monday\")\n    case 2:\n        print(\"Tuesday\")\n    case _:\n        print(\"Another day\")"),
    ]),
    "chapter_4_loops": ("Chapter 4 - Loops", [
        ("h", "Why Do We Need Loops?"),
        ("p", "A loop repeats a block of code many times, so you do not have to write the same lines again and "
              "again. Python has two kinds of loops: the for loop and the while loop."),
        ("h", "What is a for Loop?"),
        ("p", "A for loop iterates over every item of a sequence such as a list, tuple, string, dictionary or the "
              "numbers produced by range(). On each repetition the loop variable takes the next item. Use a for loop "
              "when you know in advance what you want to loop over."),
        ("code", "for fruit in [\"apple\", \"banana\", \"mango\"]:\n    print(fruit)\n\nfor i in range(1, 6):      # 1, 2, 3, 4, 5\n    print(i)"),
        ("p", "range(start, stop, step) generates numbers from start up to but not including stop. Looping through "
              "a dictionary with .items() gives both the key and the value, and enumerate() gives the index and the "
              "item together."),
        ("code", "marks = {\"Ali\": 80, \"Sara\": 92}\nfor name, score in marks.items():\n    print(name, score)\n\nfor index, fruit in enumerate([\"apple\", \"banana\"]):\n    print(index, fruit)"),
        ("h", "What is a while Loop?"),
        ("p", "A while loop keeps running as long as its condition stays True. Use it when you do not know in advance "
              "how many repetitions are needed. Make sure something inside the loop eventually makes the condition "
              "False, otherwise you create an infinite loop."),
        ("code", "count = 1\nwhile count <= 5:\n    print(count)\n    count += 1"),
        ("h", "break, continue and else"),
        ("ul", ["break: stops the loop immediately.",
                "continue: skips the rest of the current repetition and goes to the next one.",
                "else: an optional block that runs when the loop finishes without hitting break."]),
        ("h", "Nested Loops and List Comprehensions"),
        ("p", "A loop inside another loop is called a nested loop; it is often used for tables and grids. A list "
              "comprehension is a short way to build a list with a loop in a single line."),
        ("code", "squares = [n * n for n in range(1, 6)]   # [1, 4, 9, 16, 25]\nevens = [n for n in range(10) if n % 2 == 0]"),
    ]),
    "chapter_5_functions": ("Chapter 5 - Functions", [
        ("h", "How Do Functions Work in Python?"),
        ("p", "A function is a named, reusable block of code that performs one task. You define it once with the def "
              "keyword and call it as many times as you want. When a function is called, Python jumps into the "
              "function body, runs it with the arguments you passed, and then returns to the place where it was "
              "called, handing back the value given by the return statement. A function without return gives back None."),
        ("code", "def greet(name):\n    \"\"\"Return a greeting message.\"\"\"\n    return f\"Hello, {name}!\"\n\nmessage = greet(\"Ayesha\")\nprint(message)   # Hello, Ayesha!"),
        ("h", "Parameters and Arguments"),
        ("p", "Parameters are the names listed in the function definition; arguments are the actual values passed "
              "when calling it. Python supports positional arguments, keyword arguments and default values."),
        ("code", "def power(base, exponent=2):\n    return base ** exponent\n\nprint(power(5))                 # 25 (default exponent)\nprint(power(2, 3))              # 8  (positional)\nprint(power(exponent=3, base=4)) # 64 (keyword)"),
        ("h", "*args and **kwargs"),
        ("p", "Use *args to accept any number of positional arguments (collected in a tuple) and **kwargs to accept "
              "any number of keyword arguments (collected in a dictionary)."),
        ("code", "def total(*numbers):\n    return sum(numbers)\n\nprint(total(1, 2, 3, 4))   # 10"),
        ("h", "Variable Scope"),
        ("p", "Variables created inside a function are local and exist only while the function runs. Variables "
              "created outside are global. Python looks up names in the order Local, Enclosing, Global, Built-in "
              "(the LEGB rule)."),
        ("h", "Lambda Functions and Recursion"),
        ("p", "A lambda is a small anonymous function written in one line, such as lambda x: x * 2. Recursion is when "
              "a function calls itself; it needs a base case to stop, for example when computing a factorial."),
        ("code", "square = lambda x: x * x\n\ndef factorial(n):\n    if n <= 1:          # base case\n        return 1\n    return n * factorial(n - 1)\n\nprint(factorial(5))   # 120"),
        ("h", "Why Use Functions?"),
        ("ul", ["Reusability: write once, use many times.",
                "Organisation: break a big problem into small, named pieces.",
                "Easier testing and debugging.",
                "Cleaner, shorter and more readable programs."]),
    ]),
}


def build(filename: str, title: str, items: list) -> None:
    styles = getSampleStyleSheet()
    h_title = ParagraphStyle("t", parent=styles["Title"], fontSize=22, textColor=colors.HexColor("#1e3a8a"), spaceAfter=14)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#3730a3"), spaceBefore=12, spaceAfter=4)
    body = ParagraphStyle("b", parent=styles["BodyText"], fontSize=10.5, leading=15)
    code = ParagraphStyle("c", parent=styles["Code"], fontSize=9, leading=12, backColor=colors.HexColor("#f1f5f9"),
                          borderPadding=6, leftIndent=6, spaceBefore=4, spaceAfter=8)

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(2 * cm, 1.2 * cm, f"Python Programming Notes  |  {title}")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
        canvas.restoreState()

    story = [Paragraph(title, h_title)]
    for kind, content in items:
        if kind == "h":
            story.append(Paragraph(content, h2))
        elif kind == "p":
            story.append(Paragraph(content, body))
            story.append(Spacer(1, 4))
        elif kind == "ul":
            story.append(ListFlowable([ListItem(Paragraph(t, body)) for t in content], bulletType="bullet", leftIndent=14))
        elif kind == "code":
            story.append(Preformatted(content, code))
    doc = SimpleDocTemplate(str(OUT / f"{filename}.pdf"), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm, title=title, author="AI Study Assistant")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    for fname, (title, items) in CHAPTERS.items():
        build(fname, title, items)
        print("created", OUT / f"{fname}.pdf")
