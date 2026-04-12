def main():
    import re
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    match = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
    if match:
        old_version = match.group(1) + '.' + match.group(2) + '.' + match.group(3)
        major, minor, patch = map(int, match.groups())
        patch += 1
        new_version = f'{major}.{minor}.{patch}'
        content = content.replace(match.group(0), f'version = "{new_version}"')
        with open('pyproject.toml', 'w') as f:
            f.write(content)
        # Update version references in INSTALL.md
        with open('INSTALL.md', 'r') as f:
            install = f.read()
        install = install.replace(old_version, new_version)
        with open('INSTALL.md', 'w') as f:
            f.write(install)
        print(f'Version bumped to {new_version}')
    else:
        print('Version not found')