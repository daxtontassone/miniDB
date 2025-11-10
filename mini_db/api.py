# Python API so other programs can embed your DB:
# from mini_db.api import Database
# db = Database("./data")
# db.execute("INSERT INTO users VALUES (1, 'Alice')")
# rows = db.execute("SELECT * FROM users")

from __future__ import annotations
from typing import Any, List
from .schema import Catalog
from .storage.heap import HeapTable
from .sql.parser import Parser
from .sql.executor import ExecutionContext, exec_stmt

class Database:
    """
    Main entry point for interacting with the mini database.
    Manages the catalog (schema definitions) and table heaps (storage).
    """

    def __init__(self):
        # Global schema catalog
        self.catalog = Catalog()
        # Runtime table storage: table_name → HeapTable
        self.heaps: dict[str, HeapTable] = {}

    def execute(self, sql: str) -> List[Any]:
        """
        Execute one or more SQL statements.
        - sql: raw SQL string (can contain multiple ';'-separated statements)
        - returns: list of results (OK messages, row counts, or result sets)
        """
        parser = Parser(sql)  # tokenize + parse → AST
        stmts = parser.parse()
        ctx = ExecutionContext(self.catalog, self.heaps)  # runtime state
        results = []
        for s in stmts:
            res = exec_stmt(ctx, s)  # execute AST statement
            results.append(res)
        return results
