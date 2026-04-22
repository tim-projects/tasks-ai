with open("test_robustness.py", "r") as f:
    lines = f.readlines()

# The concurrent test is the one that has "Sequential Move Test" in it.
# Let's find it.
start = 0
for i, line in enumerate(lines):
    if "Sequential Move Test" in line:
        start = i
        break

for i in range(start, len(lines)):
    if 'res = self.run_cmd(["move", file, "READY,PROGRESSING"])' in lines[i]:
        lines[i] = lines[i].replace("READY,PROGRESSING", "PROGRESSING")
        break

with open("test_robustness.py", "w") as f:
    f.writelines(lines)
