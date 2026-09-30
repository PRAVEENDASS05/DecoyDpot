import os

def create_decoy(directory="./honeypot"):
    os.makedirs(directory, exist_ok=True)
    decoys = {
        "passwords.txt": "admin:P@ssw0rd123\nroot:SuperSecret!",
        "financial_report.csv": "Account,Balance\nCEO Fund,5000000",
        "employee_salaries.xlsx": ""  # Empty bait file
    }
    for name, content in decoys.items():
        path = os.path.join(directory, name)
        with open(path, "w") as f:
            f.write(content)
    print(f"Decoys placed in {directory}")
