with open("test_robustness.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "READY,PROGRESSING" in line:
        # Check if the previous line is 'self.run_cmd(["move", file, "TESTING"])'
        if i > 0 and "TESTING" in lines[i - 1]:
            lines[i] = lines[i].replace("READY,PROGRESSING", "PROGRESSING")

with open("test_robustness.py", "w") as f:
    f.writelines(lines)
