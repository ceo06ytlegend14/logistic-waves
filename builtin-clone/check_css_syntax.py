with open('builtin-clone/static/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Check balance of { and }
open_count = 0
close_count = 0
for i, char in enumerate(css):
    if char == '{':
        open_count += 1
    elif char == '}':
        close_count += 1

print(f"Total open braces: {open_count}, Total close braces: {close_count}")
if open_count != close_count:
    print(f"SYNTAX ERROR: Braces mismatch! Diff: {open_count - close_count}")
else:
    print("Braces are balanced overall.")
