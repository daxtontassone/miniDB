# Write-ahead log: append-only file that records every modification before it’s written to the heap file.
# On crash, replay WAL to recover consistency.