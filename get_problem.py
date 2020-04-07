import requests, json, sys, html2markdown, markdown_strings as mds
from random import randint
from bs4 import BeautifulSoup

cc_url = "https://codeforces.com/api/problemset.problems"
res = requests.get(cc_url)
jres = json.loads(res.text)

if not jres["status"] == "OK":
    print("Request failed")
    sys.exit()

result = jres["result"]
problems = result["problems"]
desired = []
min_rating = 600
max_rating = 1000

for p in problems:
    if "rating" in p and min_rating <= p["rating"] <= max_rating:
        desired.append(p)

problem_index = randint(0, len(desired) - 1)
new_problem = desired[problem_index]
c_id = new_problem['contestId']
c_ind = new_problem['index']

problem_url = f"https://codeforces.com/problemset/problem/{c_id}/{c_ind}"

res = requests.get(problem_url)
soup = BeautifulSoup(res.content, 'html.parser')

problem_md = ""

problem_statement = soup.find("div", class_="problem-statement")

header = problem_statement.find("div", class_="header")

title_tag = header.find("div", class_="title")
title = title_tag.text

if title_tag.name in html2markdown._supportedTags:
    problem_md += mds.header("Main Title", 1)
else:
    problem_md += title_tag.text

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
description = ""
for p in description_div.find_all("p"):
    description += p.text + "\n"

input_text = "\n"
input_specification = soup.find("div", class_="input-specification").children
input_specification_title = input_specification.__next__().text

for child in input_specification:
    input_text += child.text

output_text = "\n"
output_specification = soup.find("div", class_="output-specification").children
output_specification_title = output_specification.__next__().text

for child in output_specification:
    output_text += child.text

sample_tests = soup.find("div", class_="sample-tests").next_element

sample_title = sample_tests.text
sample_tests_elements = sample_tests.next_sibling
sample_tests_text = ""

for child in sample_tests_elements.children:
    sample_tests_text += child.text.strip() + "\n"

note_elem = soup.find("div", class_="note")

note_title = note_elem.next_element.text

notes = "\n"

for n in note_elem.children:
    
    try:
        for c in c.children:
            notes += c.text.strip() + "\n"
    except:
        notes += n.text.strip() + "\n"

with open(title + ".md", "w") as file:
    file.write(mds.header(title, 1))
    file.write(" #")
    file.write(str(c_id))
    file.write(" - ")
    file.write(c_ind)
    file.write("\n")
    file.write(mds.esc_format(description))
    file.write("\n")
    file.write(mds.header(input_specification_title, 2))
    file.write("\n")
    file.write(mds.esc_format(input_text))
    file.write("\n")
    file.write(mds.header(output_specification_title, 2))
    file.write("\n")
    file.write(mds.esc_format(output_text))
    file.write("\n\n")
    file.write(mds.header(sample_title, 2))
    file.write("\n")
    file.write(mds.esc_format(sample_tests_text))
    file.write(mds.esc_format(notes))
