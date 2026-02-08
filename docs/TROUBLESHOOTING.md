# Troubleshooting

## Alembic migration desync (duplicate table/column errors)
If `alembic upgrade head` fails with duplicate table/column errors, the schema is ahead of Alembic.
Stamp the DB to the revision it already contains, then continue upgrading.

Example sequence used in local recovery:
```bash
cd backend
source venv/bin/activate
alembic stamp 94e50da19371
alembic stamp b6d5dd2ee2f6
alembic stamp e4c9a31df224
alembic stamp 9d7f6b3a2c11
alembic stamp 0f3b5d8a2c91
alembic upgrade head
```

Notes:
- Only stamp a revision if the DB already has that schema change.
- To verify, inspect tables with `\d+ <table>` and check `alembic_version`.

## Codex agent permissions
- When asking Codex to fix local issues, explicitly grant permission to run the required CLI commands.
- Codex should request permission once and then take over the execution steps end‑to‑end.
