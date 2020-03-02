import json

with open("demo/input.json", "r") as input:
    obj = json.load(input)
    print("Hello," + obj["Name"])
    with open("demo/output.txt", "w") as output:
        output.write(obj["Name"] + "'s Hobbies:\n")
        for hobby in obj["Hobbies"]:
            output.write(hobby + "\n")
