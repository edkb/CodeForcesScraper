import requests, sys, json, datetime


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


if __name__ == "__main__":
    update()
