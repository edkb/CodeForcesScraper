"""
Usage:
    python solution.py < input.txt > solution_output.txt

Testing:
    pytest test_solution.py
"""


def get_input() -> str:
    """
    Loops throw the stdio to fetch input data
    It may change according to the input of the problem

    Returns:
        raw_input_data: The input of a problem
    """
    raw_input_data = ""
    raw_input_data += input() + "\n"
    return raw_input_data


def solve(raw_input_data):
    """
    Here you solve the problem, happy coding!!
    Args:
        raw_input_data: the output of the get_input() function

    Returns:
        answer: the solution of the problem
    """
    lines = raw_input_data.split("\n")
    
    return str(lines) + "\n"


if __name__ == "__main__":
    
    while True:
        try:
            input_data = get_input()
            answer = solve(input_data)
            print(answer, end="")
        except:
            break
