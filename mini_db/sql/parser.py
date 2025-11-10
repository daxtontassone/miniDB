# Converts tokens into an AST (abstract syntax tree).
# Example:
# SELECT name FROM users WHERE id = 1;
# becomes
# Select(
#   table="users",
#   projections=["name"],
#   where=BinOp(ColRef("id"), "=", Const(1))
# )

from __future__ import annotations
from typing import List, Optional
from .tokenizer import tokenize
from .ast_nodes import CreateTable, Insert, Select

# Custom error type for SQL parsing issues
class ParserError(SyntaxError): ...

class Parser:
    """
    A simple recursive-descent parser for SQL.
    Converts tokens → AST nodes.
    """
    def __init__(self, sql: str):
        self.tokens = tokenize(sql)  # list[(kind,text)]
        self.i = 0                   # cursor position

    # === Helpers ===
    def cur(self):
        return self.tokens[self.i]

    def eat(self, kind: str):
        """Consume the current token if it matches `kind`, else raise error."""
        k, v = self.cur()
        if k != kind:
            raise ParserError(f"Expected {kind}, got {k} ('{v}')")
        self.i += 1
        return v

    def maybe(self, kind: str) -> bool:
        """Consume the token if it matches, else return False."""
        if self.cur()[0] == kind:
            self.i += 1
            return True
        return False

    # === Entry point ===
    def parse(self):
        stmts = []
        while self.cur()[0] != "EOF":
            stmts.append(self.statement())   # parse one statement
            self.maybe("SEMICOL")            # optional semicolon
        return stmts

    # === Statement dispatch ===
    def statement(self):
        k, _ = self.cur()
        if k == "CREATE": return self.create_table()
        if k == "INSERT": return self.insert()
        if k == "SELECT": return self.select()
        raise ParserError(f"Unexpected token {k}")

    # === CREATE TABLE parser ===
    def create_table(self) -> CreateTable:
        self.eat("CREATE"); self.eat("TABLE")
        name = self.eat("IDENT")   # table name
        self.eat("LP")
        cols = []
        while True:
            col_name = self.eat("IDENT")
            dtype = self.eat_type()
            nullable = True
            primary = False
            max_len = None
            # Handle optional decorations (PRIMARY KEY, NOT NULL)
            while self.cur()[0] in ("PRIMARY","NOT"):
                if self.maybe("PRIMARY"):
                    self.eat("KEY"); primary = True; nullable = False
                elif self.maybe("NOT"):
                    self.eat("NULL"); nullable = False
            cols.append((col_name, dtype, nullable, primary, max_len))
            if not self.maybe("COMMA"):
                break
        self.eat("RP")
        return CreateTable(name, cols)

    def eat_type(self) -> str:
        """Parse a column type (INT, FLOAT, BOOL, TEXT)."""
        k, v = self.cur()
        if k in ("INT","FLOAT","BOOL","TEXT"):
            self.i += 1
            return k
        raise ParserError("Expected type")

    # === INSERT parser ===
    def insert(self) -> Insert:
        self.eat("INSERT"); self.eat("INTO"); table = self.eat("IDENT")
        cols: Optional[List[str]] = None
        if self.maybe("LP"):
            # Explicit column list
            cols = []
            while True:
                cols.append(self.eat("IDENT"))
                if not self.maybe("COMMA"):
                    break
            self.eat("RP")
        self.eat("VALUES"); self.eat("LP")
        values: List[object] = []
        while True:
            k, v = self.cur()
            if k == "INT":
                values.append(int(self.eat("INT")))
            elif k == "STRING":
                values.append(self.eat("STRING"))
            elif k == "IDENT" and v.lower() in ("true","false"):
                # Boolean literal
                self.i += 1
                values.append(v.lower() == "true")
            else:
                raise ParserError(f"Unexpected value token {k} ('{v}')")
            if not self.maybe("COMMA"):
                break
        self.eat("RP")
        return Insert(table, cols, values)

    # === SELECT parser ===
    def select(self) -> Select:
        self.eat("SELECT")
        projections: Optional[List[str]]
        if self.maybe("STAR"):
            projections = None    # SELECT * 
        else:
            projections = []
            while True:
                projections.append(self.eat("IDENT"))
                if not self.maybe("COMMA"): break
        self.eat("FROM")
        table = self.eat("IDENT")
        limit = None
        if self.maybe("LIMIT"):
            limit = int(self.eat("INT"))
        return Select(table, projections, None, None, limit)
