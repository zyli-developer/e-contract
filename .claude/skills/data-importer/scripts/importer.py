#!/usr/bin/env python3
"""
Synnovator Data Importer

Import .synnovator/*.md files into SQLite database via SQLAlchemy models.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    from sqlalchemy import create_engine, inspect
    from sqlalchemy.orm import sessionmaker
except ImportError:
    print("ERROR: SQLAlchemy is required. Install with: pip install sqlalchemy", file=sys.stderr)
    sys.exit(1)


class DataImporter:
    """Import .synnovator data into database"""

    # Import order following dependency graph
    IMPORT_ORDER = [
        # Phase 1: Independent content types
        "user",
        "event",
        "rule",
        # Phase 2: Dependent content types
        "group",
        "post",
        "resource",
        # Phase 3: Interactions
        "interaction",
        # Phase 4: Relations
        "event_rule",
        "event_post",
        "event_group",
        "post_post",
        "post_resource",
        "group_user",
        "target_interaction",
    ]

    CONTENT_TYPES = ["user", "event", "rule", "group", "post", "resource", "interaction"]
    RELATION_TYPES = [
        "event_rule",
        "event_post",
        "event_group",
        "post_post",
        "post_resource",
        "group_user",
        "target_interaction",
    ]

    def __init__(self, db_path: str, source_dir: str, models_module: Any):
        """
        Initialize importer.

        Args:
            db_path: Path to SQLite database
            source_dir: Path to .synnovator directory
            models_module: SQLAlchemy models module
        """
        self.db_path = db_path
        self.source_dir = Path(source_dir)
        self.models = models_module

        # Create database engine
        self.engine = create_engine(f"sqlite:///{db_path}")
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Statistics
        self.stats = {
            "imported": 0,
            "skipped": 0,
            "failed": 0,
            "errors": [],
        }

    def parse_md_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse .md file with YAML frontmatter.

        Returns:
            Dict with 'data' (frontmatter) and 'body' (markdown content)
        """
        try:
            content = file_path.read_text(encoding="utf-8")

            # Split frontmatter and body
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip() if len(parts) > 2 else ""
                    return {"data": frontmatter, "body": body}

            # No frontmatter, treat entire content as frontmatter
            return {"data": yaml.safe_load(content), "body": ""}

        except Exception as e:
            print(f"  ❌ Failed to parse {file_path}: {e}", file=sys.stderr)
            return None

    def get_model_class(self, type_name: str) -> Optional[Any]:
        """Get SQLAlchemy model class by type name."""
        # Convert type name to class name (e.g., "user" -> "User", "event_rule" -> "EventRule")
        class_name = "".join(word.capitalize() for word in type_name.split("_"))

        return getattr(self.models, class_name, None)

    def convert_value(self, value: Any, column_type: str) -> Any:
        """Convert value to appropriate type for database."""
        if value is None:
            return None

        # Handle datetime
        if "datetime" in column_type.lower():
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value.replace("Z", "+00:00"))
                except:
                    return None
            return value

        # Handle JSON (lists, dicts)
        if "json" in column_type.lower() or column_type.lower() in ["array", "object"]:
            if isinstance(value, (list, dict)):
                return json.dumps(value)
            return value

        # Handle boolean
        if "boolean" in column_type.lower():
            if isinstance(value, str):
                return value.lower() in ["true", "1", "yes"]
            return bool(value)

        # Handle integer
        if "integer" in column_type.lower():
            try:
                return int(value)
            except:
                return value

        # Handle float
        if "float" in column_type.lower() or "numeric" in column_type.lower():
            try:
                return float(value)
            except:
                return value

        return value

    def import_content_type(self, type_name: str, files: List[Path]) -> None:
        """Import all files of a content type."""
        print(f"\n📦 Importing {type_name} ({len(files)} files)...")

        model_class = self.get_model_class(type_name)
        if not model_class:
            print(f"  ❌ Model class not found for {type_name}", file=sys.stderr)
            self.stats["failed"] += len(files)
            return

        for file_path in files:
            self.import_single_record(type_name, file_path, model_class)

    def import_single_record(self, type_name: str, file_path: Path, model_class: Any) -> None:
        """Import a single record."""
        try:
            # Parse file
            parsed = self.parse_md_file(file_path)
            if not parsed:
                self.stats["failed"] += 1
                return

            data = parsed["data"]
            body = parsed["body"]

            # Check if record already exists
            record_id = data.get("id")
            if record_id:
                existing = self.session.query(model_class).filter_by(id=record_id).first()
                if existing:
                    print(f"  ⏭  Skipped {record_id} (already exists)")
                    self.stats["skipped"] += 1
                    return

            # Add body field if present
            if body and hasattr(model_class, "body"):
                data["body"] = body

            # Convert datetime strings
            inspector = inspect(model_class)
            for col in inspector.columns:
                if col.name in data:
                    data[col.name] = self.convert_value(data[col.name], str(col.type))

            # Create record
            record = model_class(**data)
            self.session.add(record)
            self.session.commit()

            print(f"  ✅ Imported {record_id or file_path.stem}")
            self.stats["imported"] += 1

        except Exception as e:
            self.session.rollback()
            error_msg = f"{type_name}/{file_path.name}: {str(e)}"
            print(f"  ❌ {error_msg}", file=sys.stderr)
            self.stats["failed"] += 1
            self.stats["errors"].append(error_msg)

    def import_all(self, types_filter: Optional[List[str]] = None) -> None:
        """
        Import all data in dependency order.

        Args:
            types_filter: If provided, only import these types
        """
        print(f"🚀 Starting import from {self.source_dir}")

        for type_name in self.IMPORT_ORDER:
            # Skip if filtered
            if types_filter and type_name not in types_filter:
                continue

            # Determine directory
            if type_name in self.CONTENT_TYPES:
                type_dir = self.source_dir / type_name
            else:
                type_dir = self.source_dir / "relations" / type_name

            # Skip if directory doesn't exist
            if not type_dir.exists():
                print(f"\n⏭  Skipping {type_name} (directory not found)")
                continue

            # Get all .md files
            files = sorted(type_dir.glob("*.md"))
            if not files:
                print(f"\n⏭  Skipping {type_name} (no .md files)")
                continue

            # Import
            self.import_content_type(type_name, files)

    def print_summary(self) -> None:
        """Print import summary."""
        print("\n" + "=" * 60)
        print("Import Summary")
        print("=" * 60)
        print(f"✅ Imported: {self.stats['imported']}")
        print(f"⏭  Skipped:  {self.stats['skipped']}")
        print(f"❌ Failed:   {self.stats['failed']}")

        if self.stats["errors"]:
            print(f"\nErrors ({len(self.stats['errors'])}):")
            for error in self.stats["errors"][:10]:  # Show first 10
                print(f"  - {error}")
            if len(self.stats["errors"]) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more")

    def close(self) -> None:
        """Close database session."""
        self.session.close()


def load_models_module(models_path: str) -> Any:
    """Dynamically load SQLAlchemy models module."""
    import importlib.util
    from pathlib import Path

    # Handle both directory and file paths
    models_path_obj = Path(models_path)
    if models_path_obj.is_dir():
        init_file = models_path_obj / "__init__.py"
        if init_file.exists():
            spec = importlib.util.spec_from_file_location("models", init_file)
        else:
            raise FileNotFoundError(f"No __init__.py found in {models_path}")
    else:
        spec = importlib.util.spec_from_file_location("models", models_path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load models from {models_path}")

    models_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_module)

    return models_module
