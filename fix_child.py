import os

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    if '.child.' in content:
        content = content.replace('.child.', '.get_child().')
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed {filepath}")

for root, _, files in os.walk('astronex'):
    for file in files:
        if file.endswith('.py'):
            fix_file(os.path.join(root, file))
