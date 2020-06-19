"""
Usage:
    python solution.py < input.txt > solution_output.txt

Testing:
    pytest test_solution.py

Submit:
    Just copy and paste all the code or upload the whole file
"""


def get_input_list() -> str:
    """
    Loops throw the stdio to fetch input data
    Generally used on problems with 'n' inputs

    Returns:
        raw_input_data: The input of a problem
    """
    n = int(input())
    raw_input_data = str(n) + "\n"
    
    for _ in range(n):
        raw_input_data += input() + "\n"
        
    return raw_input_data
    

def get_input() -> str:
    """
    Fetch input data from stdio
    Generally used on problems with discrete inputs
    Returns:
        raw_input_data: The input of a problem
    """
    raw_input_data = ""
    raw_input_data += input()
    return raw_input_data


def solve(raw_input_data: str):
    """
    Here you solve the problem, happy coding!!
    Args:
        raw_input_data: the data you test the solution

    Returns:
        answer: the solution of the problem
    """
    lines = raw_input_data.split()
    return str(lines)


if __name__ == "__main__":
    
    while True:
        try:
            # Use this with simple inputs
            # input_data = get_input()
            
            # Use this with the problem have many inputs
            input_data = get_input_list()
            
            answer = solve(input_data)
            print(answer, end="\n")
        except:
            break
