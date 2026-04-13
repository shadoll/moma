# Bump patch version in pyproject.toml and INSTALL.md
bump:
    #!/usr/bin/env python3
    import re
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    m = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
    if m:
        old = m.group(1) + '.' + m.group(2) + '.' + m.group(3)
        major, minor, patch = map(int, m.groups())
        new = f'{major}.{minor}.{patch + 1}'
        with open('pyproject.toml', 'w') as f:
            f.write(content.replace(m.group(0), f'version = "{new}"'))
        with open('INSTALL.md', 'r') as f:
            install = f.read()
        with open('INSTALL.md', 'w') as f:
            f.write(install.replace(old, new))
        print(f'Version bumped to {new}')
    else:
        print('Version not found')

# Bump version, sync dependencies, and build package
release: bump
    uv sync
    uv build
    @echo "Release process completed successfully!"

# Run tests
test:
    uv run pytest

# Tag the current version from pyproject.toml and push to origin
git-release:
    #!/usr/bin/env python3
    import re
    import subprocess
    import sys

    def read_version():
        with open('pyproject.toml', 'r') as f:
            content = f.read()
        m = re.search(r'version = "(\d+\.\d+\.\d+)"', content)
        return m.group(1) if m else None

    def tag_exists(tag):
        local = subprocess.run(['git', 'tag', '-l', tag], capture_output=True, text=True)
        if local.stdout.strip():
            return True
        remote = subprocess.run(['git', 'ls-remote', '--tags', 'origin', f'refs/tags/{tag}'], capture_output=True, text=True)
        return bool(remote.stdout.strip())

    def do_bump():
        with open('pyproject.toml', 'r') as f:
            content = f.read()
        m = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
        if not m:
            print('Version not found in pyproject.toml')
            sys.exit(1)
        old = m.group(0).split('"')[1]
        major, minor, patch = map(int, m.groups())
        new = f'{major}.{minor}.{patch + 1}'
        with open('pyproject.toml', 'w') as f:
            f.write(content.replace(m.group(0), f'version = "{new}"'))
        with open('INSTALL.md', 'r') as f:
            install = f.read()
        with open('INSTALL.md', 'w') as f:
            f.write(install.replace(old, new))
        print(f'Version bumped to {new}')
        return new

    version = read_version()
    if not version:
        print('Could not read version from pyproject.toml')
        sys.exit(1)

    tag = f'v{version}'

    if tag_exists(tag):
        print(f'Tag {tag} already exists.')
        print('  [c] Cancel')
        print('  [b] Bump version and continue')
        print('  [r] Replace tag (delete and re-create)')
        choice = input('Your choice (c/b/r): ').strip().lower()
        if choice == 'c' or choice == '':
            print('Cancelled.')
            sys.exit(0)
        elif choice == 'b':
            version = do_bump()
            tag = f'v{version}'
        elif choice == 'r':
            print(f'Deleting tag {tag} locally and on origin...')
            subprocess.run(['git', 'tag', '-d', tag])
            subprocess.run(['git', 'push', 'origin', f':refs/tags/{tag}'])
        else:
            print('Unknown choice, cancelling.')
            sys.exit(1)

    print(f'Creating tag {tag}...')
    subprocess.run(['git', 'tag', tag], check=True)
    print(f'Pushing tag {tag} to origin...')
    subprocess.run(['git', 'push', 'origin', tag], check=True)
    print(f'Done! Tag {tag} pushed.')

# Run the application
run *ARGS:
    uv run moma {{ARGS}}
