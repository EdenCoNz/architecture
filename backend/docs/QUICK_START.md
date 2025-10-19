# Quick Start Guide

Get up and running with the backend development environment in minutes.

## Prerequisites

- Python 3.12+
- Poetry (installed at ~/.local/bin/poetry)
- PostgreSQL (for production; SQLite works for development)

## Setup (5 minutes)

```bash
# 1. Install dependencies
make install

# 2. Set up environment variables
cp .env.example .env
# Edit .env if needed (defaults work for development)

# 3. Run database migrations
make migrate

# 4. (Optional) Create superuser
make superuser
```

## Start Development

```bash
# Start development server with hot reload
make dev
```

The server will start at http://localhost:8000 with:
- Auto-reload enabled (changes trigger automatic restart)
- Debug mode enabled
- API documentation at http://localhost:8000/api/docs/

## Development Workflow

### Writing Code

```bash
# Start dev server (in one terminal)
make dev

# Run tests in watch mode (in another terminal)
make test-watch
```

The development server will automatically restart when you save Python files.

### Before Committing

```bash
# Format code
make format

# Check linting
make lint

# Run type checking
make type-check

# Run tests
make test
```

Or run all checks at once:
```bash
make format && make lint && make type-check && make test
```

## Common Commands

```bash
make help          # Show all available commands
make test          # Run tests with coverage
make lint          # Check code quality
make format        # Auto-format code
make type-check    # Check types
make shell         # Open Django shell
make clean         # Clean build artifacts
```

## IDE Setup

### VS Code (Recommended)

1. Install extensions:
   - Python (ms-python.python)
   - EditorConfig (editorconfig.editorconfig)
   - Ruff (charliermarsh.ruff)

2. Create .vscode/settings.json:
   ```json
   {
     "python.defaultInterpreterPath": ".venv/bin/python",
     "python.linting.enabled": true,
     "python.linting.ruffEnabled": true,
     "python.formatting.provider": "black",
     "editor.formatOnSave": true,
     "editor.rulers": [100],
     "[python]": {
       "editor.defaultFormatter": "ms-python.black-formatter",
       "editor.codeActionsOnSave": {
         "source.organizeImports": true
       }
     }
   }
   ```

3. Restart VS Code

### PyCharm

1. Settings > Project > Python Interpreter > Set to Poetry venv
2. Settings > Tools > Black > Install plugin
3. Settings > Tools > Actions on Save > Enable "Reformat code"
4. Settings > Editor > Code Style > Python > Set line length to 100

## Hot Reload

The development server automatically restarts when you:
- Modify Python files
- Add new Python files
- Change settings files

**No restart needed** when you:
- Modify templates
- Change static files
- Update documentation

To disable hot reload (not recommended):
```bash
python manage.py runserver --noreload
```

## Troubleshooting

### Server won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
python manage.py runserver 0.0.0.0:8080
```

### Tests failing

```bash
# Run tests with verbose output
pytest -v

# Run specific test
pytest tests/test_configuration.py::TestDjangoConfiguration::test_debug_setting_is_configured -v

# Clear cache and retry
make clean && make test
```

### Linting errors

```bash
# Auto-fix most issues
make format

# Check what's left
make lint
```

### Import errors

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=src

# Or use make commands which set it automatically
make test
make dev
```

## Next Steps

- Read [DEVELOPMENT.md](DEVELOPMENT.md) for detailed tool documentation
- Explore API docs at http://localhost:8000/api/docs/
- Check [backend/README.md](../README.md) for project structure
- Review Django settings in src/backend/settings/

## Support

- Check [DEVELOPMENT.md](DEVELOPMENT.md) for detailed documentation
- Review test files for usage examples
- See [README.md](../README.md) for project overview
