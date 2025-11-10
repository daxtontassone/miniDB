# Mini DB (MVP)
A minimal custom database engine written in Python. This project is a learning-focused implementation of a SQL-like database, showing how SQL parsing, catalog management, and heap-based storage interact inside a database system.

## Features (MVP)
- SQL parser for basic statements
- Execution engine for simple queries
- In-memory heap storage layer
- Catalog for tracking tables and schemas
- Interactive CLI with basic pretty-printing of query results

## Example

```bash
$ python -m mini_db.cli
Mini DB (MVP). End statements with ';'. Ctrl+C to exit.
mini-db> CREATE TABLE users (id INT, name TEXT);
OK
mini-db> INSERT INTO users VALUES (1, 'Alice');
OK
mini-db> INSERT INTO users VALUES (2, 'Bob');
OK
mini-db> SELECT * FROM users;
id | name
---+------
1  | Alice
2  | Bob
(2 rows)
mini-db> ^C
Bye.

Project Structure
mini_db/
  ├── api.py          # Main Database API for executing SQL
  ├── cli.py          # Interactive shell
  ├── schema.py         # Table schema & catalog
  ├── sql/            # SQL parser & executor
  └── storage/        # Heap storage layer
tests/                # Unit tests

Roadmap

 Add persistent storage (disk-backed tables)

 Implement indexes (e.g., B+ tree)

 Add query optimizer

 Support for transactions and concurrency

 Expand SQL support (JOINs, WHERE clauses, etc.)

Why This Project?

This project demonstrates systems-level programming in Python, focusing on the internal workings of a database. It’s to serve as a learning tool and portfolio project, to help me refine my coding skills and showcase all that I have learned.
