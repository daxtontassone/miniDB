# Implements a heap file (all rows stored unordered in pages).
# Functions for insert(row), delete(rid), update(rid, new_row), scan().
# Uses the pager to actually store/retrieve data.
from __future__ import annotations
from typing import Dict, Iterator, List, Tuple
from ..schema import TableSchema

# Row ID (RID) = simple integer index in the rows list (MVP version).
RID = int

# Heap table: stores rows in insertion order in memory.
class HeapTable:
    def __init__(self, schema: TableSchema):
        self.schema = schema
        self._rows: List[Dict[str, object]] = []   # list of row dicts
        self._next_rid: RID = 0                   # auto-incremented row id
        self._pk_index: Dict[object, RID] = {}    # primary key -> row id

    def insert(self, row: Dict[str, object]) -> RID:
        """
        Insert a row into the table.
        - Validates row against schema
        - Enforces primary key uniqueness
        - Returns assigned row ID (RID)
        """
        self.schema.validate_row(row)

        # Enforce PK uniqueness
        if self.schema.primary_key:
            pk = row.get(self.schema.primary_key)
            if pk in self._pk_index:
                raise ValueError("PRIMARY KEY violation")

        rid = self._next_rid
        self._rows.append(row)

        if self.schema.primary_key:
            self._pk_index[row[self.schema.primary_key]] = rid

        self._next_rid += 1
        return rid

    def scan(self) -> Iterator[Tuple[RID, Dict[str, object]]]:
        """Iterate over all rows (RID, row dict)."""
        for rid, row in enumerate(self._rows):
            if row is not None:  # (room for delete later)
                yield rid, row

    def get_by_pk(self, key) -> Dict[str, object] | None:
        """
        Look up a row by its primary key value.
        Returns None if no PK or row not found.
        """
        if not self.schema.primary_key:
            return None
        rid = self._pk_index.get(key)
        if rid is None:
            return None
        return self._rows[rid]

    # MVP leaves update/delete for future iterations
