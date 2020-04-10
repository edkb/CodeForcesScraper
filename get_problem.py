import requests, json, sys, os, errno, re
import markdown_strings as mds
from random import randint
from bs4 import BeautifulSoup
from shutil import copyfile

cc_url = "https://codeforces.com/api/problemset.problems"
try:
    res = requests.get(cc_url)
except Exception as e:
    print("Error with request to codeforce's api.")
    print(f"Message:", e.message)
    sys.exit()

jres = json.loads(res.text)

if not jres["status"] == "OK":
    print("Request failed")
    sys.exit()

result = jres["result"]
problems = result["problems"]
desired = []
min_rating = 700
max_rating = 800

for p in problems:
    # IS IT RATED???
    if "rating" in p:
        # Checks if rating is withing specified rating range
        if min_rating <= p["rating"] <= max_rating:
            desired.append(p)

problem_index = randint(0, len(desired) - 1)
new_problem = desired[problem_index]
c_id = new_problem["contestId"]
c_ind = new_problem["index"]
rating = new_problem["rating"]

problem_url = f"https://codeforces.com/problemset/problem/{c_id}/{c_ind}"

res = requests.get(problem_url)
soup = BeautifulSoup(res.content, "html.parser")

problem_md = ""

problem_statement = soup.find("div", class_="problem-statement")

header = problem_statement.find("div", class_="header")

# Find title html tag
title_tag = header.find("div", class_="title")

# Removes index from title
raw_title = title_tag.text[3:]
title_underline = raw_title.replace(" ", "_")

# Convert to md title
title = mds.header(raw_title, 1)


filename = f"./{title_underline}/{title_underline}.md"

if not os.path.exists(f"./{title_underline}"):
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise
else:
    print("Problem already fetched, exiting...")
    sys.exit()


time_limit = header.find("div", class_="time-limit").next_element
time_limit_title = time_limit.next_element
time_limit_value = time_limit_title.next_element

memory_limit = header.find("div", class_="memory-limit").next
memory_limit_title = memory_limit.next_element
memory_limit_value = memory_limit_title.next_element

input_file = header.find("div", class_="input-file").next
input_file_title = input_file.next_element
input_file_value = input_file_title.next_element

output_file = header.find("div", class_="output-file").next
output_file_title = time_limit.next_element
output_file_value = time_limit_title.next_element

description_div = header.next_sibling
description_html = description_div.prettify()
description = (
    re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", description_html) + "\n"
)
description = re.sub(r" (\\le|\\leq) ", r" <= ", description)
description = re.sub(r" (\\ge|\\geq) ", r" >= ", description)

input_text = "\n"
input_specification_div = soup.find("div", class_="input-specification")
input_title = input_specification_div.next_element.extract().text
input_specification_html = input_specification_div.prettify()
input_specification = f"\n## {input_title}\n\n"
input_specification += (
    re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", input_specification_html)
    + "\n"
)
input_specification = re.sub(r" (\\le|\\leq) ", r" <= ", input_specification)
input_specification = re.sub(r" (\\ge|\\geq) ", r" >= ", input_specification)

output_text = "\n"
output_specification_div = soup.find("div", class_="output-specification")
output_title = output_specification_div.next_element.extract().text
output_specification_html = output_specification_div.prettify()
output_specification = f"\n## {output_title}\n\n"
output_specification += (
    re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", output_specification_html)
    + "\n"
)
output_specification = re.sub(r" (\\le|\\leq) ", r" <= ", output_specification)
output_specification = re.sub(r" (\\ge|\\geq) ", r" >= ", output_specification)

sample_tests_div = soup.find("div", class_="sample-tests")
sample_tests_title = sample_tests_div.next_element.extract().text
sample_tests_html = sample_tests_div.prettify()
sample_tests = f"\n## {sample_tests_title}\n\n"
sample_tests += (
    re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", sample_tests_html) + "\n"
)

sample_tests_elements = sample_tests_div.next_element
file_tests_input = ""
file_tests_output = ""

number_of_examples = 0
number_of_inputs = 0


with open(f"./{title_underline}/test_solution.py", "w") as file:
    file.write("from solution import solve\n")
    
    complete_test_html = sample_tests_elements.prettify()

    for child in sample_tests_elements.children:
    
        if child.attrs["class"][0] == "input":
            number_of_examples += 1
            value = child.find("pre")
            input_value = ""
            for v in value.children:
                if v.name == "br":
                    continue
                else:
                    number_of_inputs += 1
                    file_tests_input += v.strip() + "\n"
                    input_value += re.sub(r"\n", r"\\n",  v.strip() + "\n")
    
        elif child.attrs["class"][0] == "output":
            value = child.find("pre")
            output_value = ""
            for v in value.children:
                if v.name == "br":
                    continue
                else:
                    file_tests_output += v.strip() + "\n"
                    output_value += re.sub(r"\n", r"\\n",  v.strip() + "\n")
            file.write(
                f'\n\ndef test_solve_{number_of_examples}():\n\tassert solve("{input_value}") == "{output_value}"\n'
            )

note_elem_div = soup.find("div", class_="note")

if note_elem_div:
    note_elem_text = "\n"
    note_elem_title = note_elem_div.next_element.extract().text
    note_elem_html = note_elem_div.prettify()
    note_elem = f"\n### {note_elem_title}\n\n "
    note_elem += (
        re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", note_elem_html) + "\n"
    )
    note_elem = re.sub(r" (\\le|\\leq) ", r" <= ", note_elem)
    note_elem = re.sub(r" (\\ge|\\geq) ", r" >= ", note_elem)


with open(filename, "w") as file:

    file.write(title)
    file.write(" #")
    file.write(str(c_id))
    file.write(" - ")
    file.write(c_ind)
    file.write("\n")
    file.write(f"## Rating: {rating}")
    file.write("\n")
    file.write(description)
    file.write("\n")
    file.write(input_specification)
    file.write(output_specification)
    file.write(sample_tests)
    if note_elem_div:
        file.write(note_elem)


with open(f"./{title_underline}/input.txt", "w") as file:
    file.write(file_tests_input)

with open(f"./{title_underline}/expected_output.txt", "w") as file:
    file.write(file_tests_output)

with open(f"./{title_underline}/output_solution.txt", "w") as file:
    # Creates an empty solution file
    # (this helps when configuring pycharm to redirect output)
    file.write("")

copyfile("./template_solution.py", f"./{title_underline}/solution.py")
    
print(f"New problem on ./{title_underline}")
