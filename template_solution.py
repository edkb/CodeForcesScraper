"""
Usage:
    python solution.py < input.txt > solution_output.txt

Testing:
    pytest test_solution.py
"""


def get_input(inputs_number: int = 1) -> str:
    """
    Loops throw the stdio to fetch input data
    Args:
        inputs_number: Number of lines of the input
                       Needs to be manually changed in case of
                       multiple lines input
    Returns:
        raw_input_data: The input of a problem
    """
    raw_input_data = ""
    for _ in range(inputs_number):
        raw_input_data += input()
    return raw_input_data


def process_input(raw_input_data: str):
    data = raw_input_data.strip()
    return data


def solve(raw_input_data):
    n = process_input(raw_input_data)
    return n


if __name__ == "__main__":
    
    while True:
        try:
            # Change input lines number here
            input_data = get_input()
            answer = solve(input_data)
            print(answer)
        except:
            break
