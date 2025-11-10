# Defines data types (e.g., INTEGER, STRING, BOOLEAN).

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass

# Enumeration of supported SQL-like types.
class DBType(Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    BOOL = "BOOL"
    TEXT = "TEXT"

# Column metadata definition.
# frozen=True makes the object immutable after creation.
@dataclass(frozen=True)
class Column:
    name: str                # Column name (case preserved)
    dtype: DBType            # Data type (from the enum above)
    nullable: bool = True    # Whether column accepts NULL values
    max_len: int | None = None  # For TEXT columns (default below)
    primary: bool = False    # Whether this column is part of the primary key

    def __post_init__(self):
        # If column type is TEXT but no max_len was given, default to 255.
        if self.dtype == DBType.TEXT and self.max_len is None:
            object.__setattr__(self, "max_len", 255)
