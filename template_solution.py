"""
Usage:
    python solution.py < input.txt > solution_output.txt

Testing:
    pytest test_solution.py
"""


def get_input(inputs_number: int = 1) -> str:
    """
    Loops throw the stdio to fetch input data
    It may change according to the input of the problem
    Args:
        inputs_number: Number of lines of the input
                       Needs to be manually changed in case of
                       multiple lines input
    Returns:
        raw_input_data: The input of a problem
    """
    raw_input_data = ""
    raw_input_data += input()
    return raw_input_data


def process_input(raw_input_data: str):
    """
    Here the goal is to make the raw input
    equals to the input provided by the problem example
    (like the input strings on the test_solution.py)
    Args:
        raw_input_data:

    Returns:
        data: formatted string
    """
    data = raw_input_data.strip()
    return data


def solve(raw_input_data):
    """
    Here you solve the problem, happy coding!!
    Args:
        raw_input_data: the output of the get_input() function

    Returns:
        answer: the solution of the problem
    """
    answer = process_input(raw_input_data)
    return answer


if __name__ == "__main__":
    
    while True:
        try:
            # Change input lines number here
            input_data = get_input()
            answer = solve(input_data)
            print(answer)
        except:
            break
