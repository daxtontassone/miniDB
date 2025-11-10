# Table schemas + catalog:
#   TableSchema → describes one table (columns + primary key).
#   Catalog → stores all tables & indexes in the DB.

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
from .types import Column, DBType

# Defines table schema and validation logic.
@dataclass
class TableSchema:
    name: str
    columns: List[Column]            # Ordered list of column definitions
    primary_key: Optional[str] = None  # Primary key column (by name)

    def column_map(self) -> Dict[str, Column]:
        """Return dict mapping lowercase column names -> Column object."""
        return {c.name.lower(): c for c in self.columns}

    def validate_row(self, row: Dict[str, object]) -> None:
        """
        Ensure the row matches schema:
        - Required (non-nullable) columns are present
        - Types match declared column types
        - Length constraints for TEXT
        """
        cmap = self.column_map()

        # Check for NULL violations
        for c in self.columns:
            if not c.nullable and row.get(c.name) is None:
                raise ValueError(f"Column '{c.name}' cannot be NULL")

        # Type and existence checks
        for k, v in row.items():
            col = cmap.get(k.lower())
            if col is None:
                raise ValueError(f"Unknown column '{k}'")
            if v is None: 
                continue
            if col.dtype == DBType.INT and not isinstance(v, int):
                raise TypeError(f"{k} expects INT, got {type(v).__name__}")
            if col.dtype == DBType.FLOAT and not isinstance(v, (int, float)):
                raise TypeError(f"{k} expects FLOAT, got {type(v).__name__}")
            if col.dtype == DBType.BOOL and not isinstance(v, bool):
                raise TypeError(f"{k} expects BOOL, got {type(v).__name__}")
            if col.dtype == DBType.TEXT:
                if not isinstance(v, str):
                    raise TypeError(f"{k} expects TEXT, got {type(v).__name__}")
                if col.max_len and len(v) > col.max_len:
                    raise ValueError(f"{k} exceeds max_len {col.max_len}")

# Catalog = "database of schemas" (keeps metadata about tables).
class Catalog:
    """In-memory catalog for MVP."""

    def __init__(self):
        self.tables: Dict[str, TableSchema] = {}

    def create_table(self, schema: TableSchema):
        """Add a new table schema to the catalog, enforcing PK rules."""
        key = schema.name.lower()
        if key in self.tables:
            raise ValueError(f"Table '{schema.name}' already exists")

        # Ensure primary key consistency
        pks = [c.name for c in schema.columns if c.primary]
        if schema.primary_key and schema.primary_key not in pks:
            raise ValueError("primary_key must correspond to a column marked primary=True")
        if not schema.primary_key and pks:
            schema.primary_key = pks[0]

        self.tables[key] = schema

    def get(self, table: str) -> TableSchema:
        """Retrieve schema for a table by name (case-insensitive)."""
        t = self.tables.get(table.lower())
        if not t:
            raise ValueError(f"Unknown table '{table}'")
        return t
