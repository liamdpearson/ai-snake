def load_data():
    with open("data.txt", "r") as file:
        lines = file.readlines()

    return int(lines[0]), int(lines[1])

def replace_steps_taken(new):
    with open("data.txt", "r") as file:
        lines = file.readlines()

    lines[0] = str(new) + "\n"

    with open("data.txt", "w") as file:
        file.writelines(lines)

def replace_high_score(new):
    with open("data.txt", "r") as file:
        lines = file.readlines()

    lines[1] = str(new) + "\n"

    with open("data.txt", "w") as file:
        file.writelines(lines)