with open("test_tasks.py", "r") as f:
    lines = f.readlines()

start = 0
for i, line in enumerate(lines):
    if "test_regression_check_flag_sets_rc_metadata" in line:
        start = i
        break

for i in range(start, start + 50):
    if 'move", task_file, "PROGRESSING"' in lines[i]:
        lines[i] = lines[i].replace("PROGRESSING", "READY,PROGRESSING")
    elif 'move", task_file, "TESTING"' in lines[i]:
        # This one is tricky because it needs to be from PROGRESSING.
        # But maybe just READY,PROGRESSING,TESTING?
        # Let's try READY,PROGRESSING,TESTING.
        lines[i] = lines[i].replace("TESTING", "READY,PROGRESSING,TESTING")
    elif 'move", task_file, "REVIEW"' in lines[i]:
        # Same thing.
        lines[i] = lines[i].replace("REVIEW", "READY,PROGRESSING,TESTING,REVIEW")

with open("test_tasks.py", "w") as f:
    f.writelines(lines)
