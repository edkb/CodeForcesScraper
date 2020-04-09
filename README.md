# CodeForcesScrapper

## TL;DR
Fetches a random problem from https://codeforces.com, creates a markdown description, input and output files, a python solution template and saves on a new directory.

## FAQ
**Why do I need this?** - To easily get new problems to solve without leaving the IDE and switchig to the browser. All the information necessary is saved on the same place.

**How does it works?**
The script uses the official [api](https://codeforces.com/apiHelp) to to select a new problem within a [rank range](../master/get_problem.py#L25) and then scraps the page of the problem, make some tweeks to make more it readable on markdown and create the new files.

## Benefits
- Problem description integrated to the code (no more copying and pasting in the comments)
- Automatic input and expected output files (no more copying and pasting data from the examples)
- Automatic solution template code (no more recriating the same template solution for every new problem)

## Download
`git clone https://github.com/edkb/CodeForcesScrapper`

## Execution
`pip install requirements.txt`

`python get_problem.py`

## Output
New directory with the folowing template:
```
├── Name_of_the_problem
│   ├── expected_output.txt
│   ├── Name_of_the_problem.md
│   ├── input.txt
│   └── solution.py
```

### Example

![alt text](./example.png "Example")
