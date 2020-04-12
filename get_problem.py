import requests, json, os, errno
import re, fire, datetime, update_problems
from random import choice
from bs4 import BeautifulSoup
from shutil import copyfile
from typing import List, Dict, Optional


def fetch_problems() -> List:
    try:
        with open("problems.json", "r") as file:
            problems = json.load(file)
    except FileNotFoundError:
        problems = update_problems.update()

    today = datetime.datetime.today()
    problems_date = datetime.datetime.strptime(problems["date"], "%d-%m-%Y")

    if today - problems_date > datetime.timedelta(days=7):
        problems = update_problems.update()

    return problems["problems"]


def filter_problems(
    problems: List, min_rating: Optional[int] = None, max_rating: Optional[int] = None
) -> List[Dict]:
    """
    Returns a list of problems between the specified rating
    Args:
        problems: Complete list of problems
        min_rating: The minimum difficulty rate
        max_rating: The maximum difficulty rate

    Returns:
        desired: List with the filtered problems
    """
    desired = []
    for p in problems:
        # IS IT RATED???
        if "rating" in p:
            if min_rating:
                if max_rating:
                    if min_rating <= p["rating"] <= max_rating:
                        # Add problem if is between specified range
                        desired.append(p)
                else:
                    # Add problem if only min is specified
                    if min_rating <= p["rating"]:
                        desired.append(p)
            else:
                if max_rating:
                    # Add problem if only min is specified
                    if p["rating"] <= max_rating:
                        desired.append(p)
        else:
            # Add problem it's not rated and there is no rating limit
            if not (min_rating or max_rating):
                desired.append(p)
    return desired


def is_fetched_problem(title_underline: str, filename: str) -> bool:
    """
    Check if the problem already exists
    Args:
        title_underline:
        filename:

    Returns:
        True if it's fetched,
        False otherwise
    """
    if not os.path.exists(f"./{title_underline}"):
        try:
            os.makedirs(os.path.dirname(filename))
            return True
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    return False


def choose_new_problem(desired: List) -> Dict:
    """
    Selects a random problem from the desired list
    Args:
        desired: List of the desired problems

    Returns:
        new_problem: The chosen problem
    """
    while True:
        # Randomly chooses a problem util
        # ir finds a new one
        new_problem = choice(desired)
        title = new_problem["name"]
        title_underline = title.replace(" ", "_")
        filename = f"./{title_underline}/{title_underline}.md"

        if is_fetched_problem(title_underline, filename):
            continue
        else:
            break
    return new_problem


def main(min_rating: int = 700, max_rating: int = 900) -> None:

    problems = fetch_problems()
    desired = filter_problems(problems, min_rating, max_rating)

    new_problem = choose_new_problem(desired)

    c_id = new_problem["contestId"]
    c_ind = new_problem["index"]
    rating = new_problem["rating"]
    title = new_problem["name"]

    title_underline = title.replace(" ", "_")
    filename = f"./{title_underline}/{title_underline}.md"

    problem_url = f"https://codeforces.com/problemset/problem/{c_id}/{c_ind}"

    res = requests.get(problem_url)
    soup = BeautifulSoup(res.content, "html.parser")

    problem_statement = soup.find("div", class_="problem-statement")
    header = problem_statement.find("div", class_="header")

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
        re.sub(
            r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", input_specification_html
        )
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
        re.sub(
            r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", output_specification_html
        )
        + "\n"
    )
    output_specification = re.sub(r" (\\le|\\leq) ", r" <= ", output_specification)
    output_specification = re.sub(r" (\\ge|\\geq) ", r" >= ", output_specification)

    sample_tests_div = soup.find("div", class_="sample-tests")
    sample_tests_title = sample_tests_div.next_element.extract().text
    sample_tests_html = sample_tests_div.prettify()
    sample_tests = f"\n## {sample_tests_title}\n\n"
    sample_tests += (
        re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", sample_tests_html)
        + "\n"
    )

    sample_tests_elements = sample_tests_div.next_element
    file_tests_input = ""
    file_tests_output = ""

    number_of_examples = 0
    number_of_inputs = 0

    with open(f"./{title_underline}/test_solution.py", "w") as file:
        file.write("from .solution import solve\n")

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
                        input_value += re.sub(r"\n", r"\\n", v.strip() + "\n")

            elif child.attrs["class"][0] == "output":
                value = child.find("pre")
                output_value = ""
                for v in value.children:
                    if v.name == "br":
                        continue
                    else:
                        file_tests_output += v.strip() + "\n"
                        output_value += re.sub(r"\n", r"\\n", v.strip() + "\n")
                file.write(
                    f'\n\n@pytest.mark.timeout({time_limit_value})\ndef test_solve_{number_of_examples}():\n\tassert solve("{input_value}") == "{output_value}"\n'
                )

    note_elem_div = soup.find("div", class_="note")

    if note_elem_div:
        note_elem_text = "\n"
        note_elem_title = note_elem_div.next_element.extract().text
        note_elem_html = note_elem_div.prettify()
        note_elem = f"\n### {note_elem_title}\n\n "
        note_elem += (
            re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", note_elem_html)
            + "\n"
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


if __name__ == "__main__":
    fire.Fire(main)
