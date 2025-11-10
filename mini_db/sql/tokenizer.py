# Splits SQL text into tokens (SELECT, FROM, WHERE, identifiers, literals).

import re

# === Token Definitions ===
# Each SQL keyword/symbol is mapped to a regex pattern.
TOKEN_SPEC = [
    ("SKIP",   r"[ \t\r\n]+"),               # Whitespace
    ("COMMA",  r","),                        # ,
    ("LP",     r"\("),                       # (
    ("RP",     r"\)"),                       # )
    ("SEMICOL",r";"),                        # ;
    ("STAR",   r"\*"),                       # *
    ("INT",    r"\d+"),                      # integer literal
    ("STRING", r'"[^"]*"|\'[^\']*\''),       # quoted string
    ("IDENT",  r"[A-Za-z_][A-Za-z0-9_]*"),   # identifier (table/col names)
]

# SQL keywords recognized (case-insensitive, converted to uppercase tokens)
KEYWORDS = {
    "create","table","primary","key","not","null",
    "insert","into","values",
    "select","from","limit",
    "int","float","bool","text"
}

Tok = tuple[str, str]

def tokenize(sql: str) -> list[Tok]:
    """
    Convert an input SQL string into a list of tokens.
    Example:
      'SELECT * FROM users;' →
      [('SELECT','select'), ('STAR','*'), ('FROM','from'), ('IDENT','users'), ('SEMICOL',';'), ('EOF','')]
    """
    tok_regex = "|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC)
    get_token = re.compile(tok_regex).match
    pos = 0
    tokens: list[Tok] = []
    m = get_token(sql, pos)
    while m:
        kind = m.lastgroup
        text = m.group()
        if kind == "SKIP":
            # Ignore whitespace
            pass
        elif kind in ("STRING",):
            # Strip surrounding quotes for strings
            if text[0] == text[-1] and text[0] in "\"'":
                text = text[1:-1]
            tokens.append((kind, text))
        else:
            # Check if IDENT is actually a keyword
            if kind == "IDENT":
                low = text.lower()
                if low in KEYWORDS:
                    tokens.append((low.upper(), low))
                else:
                    tokens.append(("IDENT", text))
            else:
                tokens.append((kind, text))
        pos = m.end()
        m = get_token(sql, pos)

    tokens.append(("EOF", ""))  # End marker
    return tokens
