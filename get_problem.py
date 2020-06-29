import requests, json, os, errno, sys
import re, fire, datetime
from random import choice
from bs4 import BeautifulSoup, Tag, ResultSet, NavigableString
from shutil import copyfile
from typing import List, Dict, Optional


def update():
    problems_endpoint = "https://codeforces.com/api/problemset.problems"
    try:
        res = requests.get(problems_endpoint)
    except Exception as e:
        print("Error with request to codeforce's api.")
        print(f"Message:", e.message)
        sys.exit()
    
    if int(res.status_code) != 200:
        print(f"Request to {problems_endpoint} failed")
        print(f"Status code: {res.status_code}")
        print(f"Reason: {res.reason}")
        sys.exit()
    
    jres = json.loads(res.text)
    problems = jres["result"]["problems"]
    
    problems_dict = {
        "date": datetime.datetime.today().strftime('%d-%m-%Y'),
        "problems": problems
    }
    with open("problems.json", "w") as file:
        file.write(json.dumps(problems_dict))
    
    return problems_dict


def fetch_problems() -> List:
    try:
        with open("problems.json", "r") as file:
            problems = json.load(file)
    except FileNotFoundError:
        problems = update()

    today = datetime.datetime.today()
    problems_date = datetime.datetime.strptime(problems["date"], "%d-%m-%Y")

    if today - problems_date > datetime.timedelta(days=7):
        problems = update()

    return problems["problems"]


def filter_problems(
    problems: List,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None
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


def create_problem_directory_and_files(title_underline: str) -> None:
    try:
        md_filename = f"./{title_underline}/{title_underline}.md"
        os.makedirs(os.path.dirname(md_filename))
        open(f"{title_underline}/__init__.py", 'a').close()
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise


def choose_new_problem(desired: List) -> Dict:
    """
    Selects a random problem from the desired list
    Args:
        desired: List of the desired problems

    Returns:
        new_problem: The chosen problem
    """
    while True:
        # Randomly chooses a new problem
        new_problem = choice(desired)
        title = new_problem["name"]
        title_underline = title.replace(" ", "_")
        
        # Create the problem directory and returns the problem
        # if its a new problem (directory with the problem's name doesn't exist)
        if not os.path.exists(f"./{title_underline}"):
            create_problem_directory_and_files(title_underline)
            return new_problem


def main(min_rating: int = 700, max_rating: int = 900, problem_url: Optional[str] = None) -> None:

    if not problem_url:
        problems = fetch_problems()
        desired = filter_problems(problems, min_rating, max_rating)
    
        new_problem = choose_new_problem(desired)
    
        c_id = new_problem["contestId"]
        c_ind = new_problem["index"]
        rating = new_problem["rating"]
        title = new_problem["name"]
    
        title_underline = title.replace(" ", "_")
        md_filename = f"./{title_underline}/{title_underline}.md"
    
        problem_url = f"https://codeforces.com/problemset/problem/{c_id}/{c_ind}"
        
    else:
        divided_url = problem_url.split("/")
        
        c_id = divided_url[-2]
        c_ind = divided_url[-1]
        rating = "unknown"
        title = ""

    res = requests.get(problem_url)
    soup = BeautifulSoup(res.content, "html.parser")

    problem_statement: Tag = soup.find("div", class_="problem-statement")
    header: Tag = problem_statement.find("div", class_="header")
    
    if not title:
        # Find title html tag
        title_tag = header.find("div", class_="title")
    
        # Removes index from title
        raw_title = title_tag.text[3:]
        title_underline = raw_title.replace(" ", "_")
        md_filename = f"./{title_underline}/{title_underline}.md"
        
        create_problem_directory_and_files(title_underline)

    time_limit = header.find("div", class_="time-limit").next_element
    time_limit_title = time_limit.next_element
    time_limit_text: str = time_limit_title.next_element.split(" ")
    time_limit_value = int(time_limit_text[0])

    memory_limit = header.find("div", class_="memory-limit")
    memory_limit_title = memory_limit.contents[1].text
    memory_limit_value = memory_limit.contents[2].string

    input_file = header.find("div", class_="input-file")
    input_file_title = input_file.contents[1].text
    input_file_value = input_file.contents[2].string

    output_file = header.find("div", class_="output-file")
    output_file_title = output_file.contents[1].text
    output_file_value = output_file.contents[2].string

    description_div: Tag = header.next_sibling
    while isinstance(description_div, NavigableString):
        description_div = description_div.next_sibling
        
    description_html: str = description_div.prettify()
    description = (
        re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", description_html) + "\n"
    )
    description = re.sub(r" (\\le|\\leq) ", r" <= ", description)
    description = re.sub(r" (\\ge|\\geq) ", r" >= ", description)

    input_specification_div: Tag = soup.find("div", class_="input-specification")
    input_title_div: Tag = input_specification_div.find("div", class_="section-title")
    input_title: str = input_title_div.text
    input_title_div.decompose()
    input_specification_html = input_specification_div.prettify()
    input_specification = f"\n### {input_title}\n\n"
    input_specification += (
        re.sub(
            r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", input_specification_html
        )
        + "\n"
    )
    input_specification = re.sub(r" (\\le|\\leq) ", r" <= ", input_specification)
    input_specification = re.sub(r" (\\ge|\\geq) ", r" >= ", input_specification)

    output_specification_div = soup.find("div", class_="output-specification")
    output_title_div = output_specification_div.find("div", class_="section-title")
    output_title: str = output_title_div.text
    output_title_div.decompose()
    output_specification_html = output_specification_div.prettify()
    output_specification = f"\n### {output_title}\n\n"
    output_specification += (
        re.sub(
            r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", output_specification_html
        )
        + "\n"
    )
    output_specification = re.sub(r" (\\le|\\leq) ", r" <= ", output_specification)
    output_specification = re.sub(r" (\\ge|\\geq) ", r" >= ", output_specification)

    sample_tests_div: Tag = soup.find("div", class_="sample-tests")
    sample_tests_title_div = sample_tests_div.find(class_="section-title")
    sample_tests_title = sample_tests_title_div.text
    sample_tests_title_div.decompose()
    
    sample_tests_html = sample_tests_div.prettify()
    sample_tests = f"\n## {sample_tests_title}\n\n"
    sample_tests += (
        re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", sample_tests_html)
        + "\n"
    )

    sample_tests_elements: Tag = sample_tests_div.find(class_="sample-test")
    
    input_elements: ResultSet = sample_tests_elements.find(class_="input").find_all("pre")
    output_elements: ResultSet = sample_tests_elements.find(class_="output").find_all("pre")
    
    file_tests_input = ""
    file_tests_output = ""

    number_of_examples = 0

    copyfile("./test_template_solution.py", f"./{title_underline}/test_solution.py")

    with open(f"./{title_underline}/test_solution.py", "a+") as file:

        for input_child, output_child in zip(input_elements, output_elements):

            input_value = ""
            for v in input_child.children:
                if v.name == "br":
                    continue
                else:
                    file_tests_input += v.strip() + "\n"
                    input_value += re.sub(r"\n", r"\\n", v.strip() + "\n")

                output_value = ""
            for v in output_child.children:
                if v.name == "br":
                    continue
                else:
                    file_tests_output += v.strip() + "\n"
                    output_value += re.sub(r"\n", r"\\n", v.strip() + "\n")
            file.write(
                f'\n\n@pytest.mark.timeout({time_limit_value})\ndef test_solve_{number_of_examples}():\n\tassert solve("{input_value}") == "{output_value}"\n'
            )

    note_elem_div: Tag = soup.find("div", class_="note")

    if note_elem_div:
        note_elem_title_div: Tag = note_elem_div.find("div", class_="section-title")
        note_elem_title = note_elem_title_div.text
        note_elem_title_div.decompose()
        note_elem_html = note_elem_div.prettify()
        note_elem = f"\n### {note_elem_title}\n\n "
        note_elem += (
            re.sub(r"\$\$\$([^\$]+)\$\$\$", r"<strong>\1</strong>", note_elem_html)
            + "\n"
        )
        note_elem = re.sub(r" (\\le|\\leq) ", r" <= ", note_elem)
        note_elem = re.sub(r" (\\ge|\\geq) ", r" >= ", note_elem)

    with open(md_filename, "w") as file:
        file.write(f"# [{title} #{c_id} - {c_ind}]({problem_url})\n")
        file.write(f"### Rating: {rating}\n")
        file.write(f"\n{memory_limit_title}: {memory_limit_value}\n")
        file.write(f"\n{input_file_title}: {input_file_value}\n")
        file.write(f"\n{output_file_title}: {output_file_value}\n")
        file.write(f"##Description {description} \n")
        file.write(input_specification)
        file.write(output_specification)
        file.write(sample_tests)
        if note_elem_div:
            file.write(note_elem)

    with open(f"./{title_underline}/input.txt", "w") as file:
        file.write(file_tests_input)

    with open(f"./{title_underline}/expected_output.txt", "w") as file:
        file.write(file_tests_output)

    with open(f"./{title_underline}/solution_output.txt", "w") as file:
        # Creates an empty solution file
        # (this helps when configuring pycharm to redirect output)
        file.write("")

    copyfile("./template_solution.py", f"./{title_underline}/solution.py")

    print(f"New problem on ./{title_underline}")


if __name__ == "__main__":
    fire.Fire(main)
