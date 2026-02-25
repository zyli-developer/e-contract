# Data Importer

Import `.synnovator/*.md` files into SQLite database via SQLAlchemy models.

## Usage

```bash
cd scripts/

# Import all data
python cli.py import \
  --source ../../../.synnovator \
  --db ../../../data/synnovator.db \
  --models ../../../backend/models

# Import specific types
python cli.py import \
  --source ../../../.synnovator \
  --db ../../../data/synnovator.db \
  --models ../../../backend/models \
  --types user,post,event
```

## Features

- Parse YAML frontmatter + Markdown body
- Automatic type conversion (datetime, JSON, boolean, etc.)
- Dependency-aware import order
- Skip existing records (incremental mode)
- Detailed error reporting
- Batch import for performance

## Testing

```bash
cd scripts/
python test_importer.py
```

## Structure

```
data-importer/
├── SKILL.md              # Skill description
├── README.md             # This file
├── scripts/
│   ├── importer.py       # Core import logic
│   ├── cli.py            # Command-line interface
│   └── test_importer.py  # Test suite
└── references/
    ├── mapping.md        # Field mapping reference
    └── import-order.md   # Dependency graph
```

## Requirements

- Python 3.8+
- SQLAlchemy
- PyYAML
