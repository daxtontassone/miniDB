# the command-line interface (REPL). Example:
# $ python -m mini_db
# mini-db> CREATE TABLE users (id INT PRIMARY KEY, name TEXT);

from __future__ import annotations
import sys
from .api import Database

PROMPT = "mini-db> "

def main():
    """
    Simple interactive CLI for the mini database.
    Reads SQL commands from stdin, executes them, and prints results.
    """
    db = Database()  # initialize fresh in-memory DB
    buf = ""         # buffer for multi-line input
    print("Mini DB (MVP). End statements with ';'. Ctrl+C to exit.")

    try:
        while True:
            # Read user input line-by-line
            line = input(PROMPT)
            buf += line + "\n"

            # When user enters a semicolon, treat buffer as a complete SQL stmt
            if ";" in line:
                try:
                    results = db.execute(buf)  # run SQL
                    for r in results:
                        if isinstance(r, list):
                            # Case: result set (from SELECT)
                            if not r:
                                print("(0 rows)")
                                continue
                            # Print header row
                            cols = list(r[0].keys())
                            print(" | ".join(cols))
                            print("-+-".join("-" * len(c) for c in cols))
                            # Print each row
                            for row in r:
                                print(" | ".join(str(row[c]) for c in cols))
                            print(f"({len(r)} rows)")
                        else:
                            # Case: non-SELECT response ("OK", "1 row inserted")
                            print(r)
                except Exception as e:
                    print(f"Error: {e}")
                # Reset buffer for next command
                buf = ""
    except (KeyboardInterrupt, EOFError):
        # Handle Ctrl+C / Ctrl+D cleanly
        print("\nBye.")

if __name__ == "__main__":
    main()
