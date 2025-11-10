# Defines AST classes (Select, Insert, Update, Delete, Expr, ColRef, etc.).
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

# === AST Node Definitions ===
# These are lightweight data structures that represent parsed SQL statements.

# DDL (Data Definition Language)
@dataclass
class CreateTable:
    # Represents: CREATE TABLE ...
    name: str
    columns: List[tuple]  # (name, type, nullable, primary, max_len)

# DML (Data Manipulation Language)
@dataclass
class Insert:
    # Represents: INSERT INTO ...
    table: str
    columns: Optional[List[str]]  # If None → values provided for all columns
    values: List[object]          # Raw values (int, str, bool, etc.)

@dataclass
class Select:
    # Represents: SELECT ...
    table: str
    projections: Optional[List[str]]  # If None → SELECT *
    where: None = None                # Reserved for later (MVP ignores WHERE)
    order_by: None = None             # Reserved for later
    limit: Optional[int] = None       # LIMIT N support
