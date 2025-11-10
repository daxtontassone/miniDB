# Turns AST into a logical plan (sequence of operators like Scan, Filter, Project).
# Chooses between SeqScan vs IndexScan based on schema & indexes.