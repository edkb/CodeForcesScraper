import requests, json, sys, os, errno, re
import markdown_strings as mds
from random import randint
from bs4 import BeautifulSoup

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
min_rating = 500
max_rating = 600

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

# Convert to md title
title = mds.header(raw_title, 1)

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
description = re.sub(r" \\le ", r" <= ", description)
description = re.sub(r" \\ge ", r" >= ", description)

input_text = "\n"
input_specification_div = soup.find("div", class_="input-specification")
input_title = input_specification_div.next_element.extract().text
input_specification_html = input_specification_div.prettify()
input_specification = f"\n## {input_title}\n\n"
input_specification += (
    re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", input_specification_html)
    + "\n"
)
input_specification = re.sub(r" \\le ", r" <= ", input_specification)
input_specification = re.sub(r" \\ge ", r" >= ", input_specification)

output_text = "\n"
output_specification_div = soup.find("div", class_="output-specification")
output_title = output_specification_div.next_element.extract().text
output_specification_html = output_specification_div.prettify()
output_specification = f"\n## {output_title}\n\n"
output_specification += (
    re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", output_specification_html)
    + "\n"
)
output_specification = re.sub(r" \\le ", r" <= ", output_specification)
output_specification = re.sub(r" \\ge ", r" >= ", output_specification)

sample_tests_div = soup.find("div", class_="sample-tests")
sample_tests_title = sample_tests_div.next_element.extract().text
sample_tests_html = sample_tests_div.prettify()
sample_tests = f"\n## {sample_tests_title}\n\n"
sample_tests += (
    re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", sample_tests_html) + "\n"
)

sample_tests_elements = sample_tests_div.next_element
sample_tests_input = ""
sample_tests_output = ""

number_of_examples = 0

for child in sample_tests_elements.children:

    if child.attrs["class"][0] == "input":
        number_of_examples += 1
        value = child.find("pre")

        for v in value.children:
            if v.name == "br":
                continue
            else:
                sample_tests_input += v.strip() + "\n"

    elif child.attrs["class"][0] == "output":
        value = child.find("pre").text
        sample_tests_output += value.strip() + "\n"

sample_tests_input = str(number_of_examples) + "\n" + sample_tests_input

note_elem_div = soup.find("div", class_="note")

if note_elem_div:
    note_elem_text = "\n"
    note_elem_title = note_elem_div.next_element.extract().text
    note_elem_html = note_elem_div.prettify()
    note_elem = f"\n### {note_elem_title}\n\n "
    note_elem += (
        re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", note_elem_html) + "\n"
    )
    note_elem = re.sub(r" \\le ", r" <= ", note_elem)
    note_elem = re.sub(r" \\ge ", r" >= ", note_elem)

title_underline = raw_title.replace(" ", "_")

filename = f"./{title_underline}/{title_underline}.md"

if not os.path.exists(os.path.dirname(filename)):
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

with open(filename, "w") as file:

    file.write(title)
    file.write(" #")
    file.write(str(c_id))
    file.write(" - ")
    file.write(c_ind)
    file.write("\n")
    file.write(description)
    file.write("\n")
    file.write(input_specification)
    file.write(output_specification)
    file.write(sample_tests)
    if note_elem_div:
        file.write(note_elem)


with open(f"./{title_underline}/input.txt", "w") as file:
    file.write(sample_tests_input)

with open(f"./{title_underline}/expected_output.txt", "w") as file:
    file.write(sample_tests_output)


code = """
def solve(test, data):
    pass


if __name__ == "__main__":
    with open("input.txt", "r") as file:
        n_tests = int(file.readline())
        data = file.readlines()

    for test in range(1, n_tests + 1):
        solve(test, data)
"""
with open(f"./{title_underline}/solution.py", "w") as file:
    file.write(code)
