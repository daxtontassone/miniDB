# Executes the plan.
# Operators are iterators: SeqScan yields rows, Filter wraps it and filters, Project wraps and selects columns, etc.

from __future__ import annotations
from typing import Dict, Iterable, List
from ..schema import Catalog, TableSchema
from ..types import Column, DBType
from ..storage.heap import HeapTable
from .ast_nodes import CreateTable, Insert, Select

# Holds runtime state (catalog + heap storage)
class ExecutionContext:
    def __init__(self, catalog: Catalog, heaps: dict[str, HeapTable]):
        self.catalog = catalog       # schema definitions
        self.heaps = heaps           # table_name → HeapTable

# Entry point: dispatch by statement type
def exec_stmt(ctx: ExecutionContext, stmt):
    if isinstance(stmt, CreateTable):
        return _exec_create(ctx, stmt)
    if isinstance(stmt, Insert):
        return _exec_insert(ctx, stmt)
    if isinstance(stmt, Select):
        return _exec_select(ctx, stmt)
    raise ValueError(f"Unsupported statement: {type(stmt).__name__}")

# === CREATE TABLE ===
def _exec_create(ctx: ExecutionContext, s: CreateTable):
    cols: List[Column] = []
    pk = None
    # Convert AST column tuples → Column objects
    for name, dtype, nullable, primary, max_len in s.columns:
        t = {"INT": DBType.INT, "FLOAT": DBType.FLOAT, "BOOL": DBType.BOOL, "TEXT": DBType.TEXT}[dtype]
        col = Column(name=name, dtype=t, nullable=nullable, primary=primary, max_len=max_len)
        cols.append(col)
        if primary:
            pk = name
    schema = TableSchema(s.name, cols, pk)
    ctx.catalog.create_table(schema)
    ctx.heaps[s.name.lower()] = HeapTable(schema)  # allocate in-memory storage
    return "OK"

# === INSERT INTO ===
def _exec_insert(ctx: ExecutionContext, s: Insert):
    schema = ctx.catalog.get(s.table)
    col_order = [c.name for c in schema.columns]
    # Case 1: No column list → use table's full column order
    if s.columns is None:
        if len(s.values) != len(col_order):
            raise ValueError("VALUES count does not match table column count")
        row = {col_order[i]: s.values[i] for i in range(len(col_order))}
    else:
        # Case 2: Explicit column list
        if len(s.values) != len(s.columns):
            raise ValueError("VALUES count does not match column list")
        row = {c: v for c, v in zip(s.columns, s.values)}
        # Fill missing columns with NULLs
        for c in col_order:
            row.setdefault(c, None)
    heap = ctx.heaps[s.table.lower()]
    heap.insert(row)  # validation + storage
    return "1 row inserted"

# === SELECT ===
def _exec_select(ctx: ExecutionContext, s: Select):
    schema = ctx.catalog.get(s.table)
    heap = ctx.heaps[s.table.lower()]
    col_order = [c.name for c in schema.columns]
    cols = col_order if s.projections is None else s.projections
    out: List[Dict[str, object]] = []
    for _, row in heap.scan():
        proj = {c: row.get(c) for c in cols}   # projection (subset of columns)
        out.append(proj)
        if s.limit is not None and len(out) >= s.limit:
            break
    return out
