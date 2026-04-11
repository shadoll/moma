def main():
    import re
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    match = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
    if match:
        major, minor, patch = map(int, match.groups())
        patch += 1
        new_version = f'{major}.{minor}.{patch}'
        content = content.replace(match.group(0), f'version = "{new_version}"')
        with open('pyproject.toml', 'w') as f:
            f.write(content)
        print(f'Version bumped to {new_version}')
    else:
        print('Version not found')