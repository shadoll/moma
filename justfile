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

# Run the application
run *ARGS:
    uv run moma {{ARGS}}
