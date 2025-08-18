
#!/usr/bin/env python3
"""
Introspect a PostgreSQL/PostGIS database and output a Markdown documentation
of schemas, tables, columns, PK/FK, indexes, views, functions, and geometry columns.

Usage:
  python introspect_to_markdown.py \
    --host localhost --port 5433 \
    --db airport_air_quality --user airport_user --password airport_password \
    --schema public \
    --out db_introspection.md

If --out is omitted, the Markdown is printed to STDOUT.
"""

import argparse
import sys
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def mk_conn_url(host: str, port: int, db: str, user: str, password: str) -> str:
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def fetchall(engine: Engine, sql: str, params: Optional[dict] = None) -> List[Dict[str, Any]]:
    with engine.connect() as conn:
        res = conn.execute(text(sql), params or {})
        cols = res.keys()
        return [dict(zip(cols, row)) for row in res.fetchall()]


def md_h1(txt: str) -> str:
    return f"# {txt}\n\n"


def md_h2(txt: str) -> str:
    return f"## {txt}\n\n"


def md_h3(txt: str) -> str:
    return f"### {txt}\n\n"


def md_table(rows: List[Dict[str, Any]], headers: List[str]) -> str:
    # Convert to markdown table
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows:
        out.append("| " + " | ".join("" if r.get(h) is None else str(r.get(h)) for h in headers) + " |")
    return "\n".join(out) + "\n\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--user", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--schema", default=None, help="If provided, limit to this schema (e.g., public)")
    ap.add_argument("--out", default=None, help="Output Markdown file; if omitted, prints to STDOUT")
    args = ap.parse_args()

    url = mk_conn_url(args.host, args.port, args.db, args.user, args.password)
    engine = create_engine(url)

    parts: List[str] = []

    # Header
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    parts.append(md_h1(f"Database Introspection — {args.db}"))
    parts.append(f"_Generated on {now}_  \n")
    parts.append(f"**Host**: `{args.host}`  |  **Port**: `{args.port}`  |  **Schema filter**: `{args.schema or 'ALL (non-system)'}`\n\n")

    # Version & extensions
    version = fetchall(engine, "SELECT version() AS version;")
    parts.append(md_h2("Instance"))
    parts.append(md_table(version, ["version"]))

    ext = fetchall(engine, "SELECT extname, extversion, nspname AS schema FROM pg_extension e JOIN pg_namespace n ON n.oid = e.extnamespace ORDER BY extname;")
    parts.append(md_h3("Extensions"))
    if ext:
        parts.append(md_table(ext, ["extname", "extversion", "schema"]))
    else:
        parts.append("_No extensions found._\n\n")

    # Schemas
    sch_sql = """
    SELECT nspname AS schema
    FROM pg_namespace
    WHERE nspname NOT LIKE 'pg_%' AND nspname <> 'information_schema'
    ORDER BY 1;
    """
    schemas = [r["schema"] for r in fetchall(engine, sch_sql)]
    if args.schema:
        schemas = [s for s in schemas if s == args.schema]

    parts.append(md_h2("Schemas"))
    parts.append(md_table([{"schema": s} for s in schemas], ["schema"]))

    # Iterate schemas
    for schema in schemas:
        parts.append(md_h2(f"Schema `{schema}`"))

        # Tables
        tbl_sql = """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema = :schema
        ORDER BY 1,2;
        """
        tables = fetchall(engine, tbl_sql, {"schema": schema})

        # Views
        view_sql = """
        SELECT table_schema, table_name
        FROM information_schema.views
        WHERE table_schema = :schema
        ORDER BY 1,2;
        """
        views = fetchall(engine, view_sql, {"schema": schema})

        parts.append(md_h3("Tables"))
        parts.append(md_table(tables, ["table_schema", "table_name"]) if tables else "_No tables._\n\n")

        parts.append(md_h3("Views"))
        parts.append(md_table(views, ["table_schema", "table_name"]) if views else "_No views._\n\n")

        # For each table: columns, PK, FK, indexes
        for t in tables:
            tname = t["table_name"]
            parts.append(md_h3(f"Table `{schema}.{tname}`"))

            col_sql = """
            SELECT ordinal_position, column_name, data_type, udt_name, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = :schema AND table_name = :table
            ORDER BY ordinal_position;
            """
            cols = fetchall(engine, col_sql, {"schema": schema, "table": tname})
            parts.append("**Columns**\n\n")
            parts.append(md_table(cols, ["ordinal_position", "column_name", "data_type", "udt_name", "is_nullable", "column_default"]))

            pk_sql = """
            SELECT kcu.column_name, tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = :schema
              AND tc.table_name = :table
            ORDER BY kcu.ordinal_position;
            """
            pks = fetchall(engine, pk_sql, {"schema": schema, "table": tname})
            parts.append("**Primary Key**\n\n")
            parts.append(md_table(pks, ["column_name", "constraint_name"]) if pks else "_(none)_\n\n")

            fk_sql = """
            SELECT kcu.column_name,
                   ccu.table_schema AS foreign_table_schema,
                   ccu.table_name   AS foreign_table_name,
                   ccu.column_name  AS foreign_column_name,
                   tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
             AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = :schema
              AND tc.table_name = :table
            ORDER BY 1;
            """
            fks = fetchall(engine, fk_sql, {"schema": schema, "table": tname})
            parts.append("**Foreign Keys**\n\n")
            parts.append(md_table(fks, ["column_name", "foreign_table_schema", "foreign_table_name", "foreign_column_name", "constraint_name"]) if fks else "_(none)_\n\n")

            idx_sql = """
            SELECT schemaname AS table_schema, tablename AS table_name, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = :schema AND tablename = :table
            ORDER BY indexname;
            """
            idxs = fetchall(engine, idx_sql, {"schema": schema, "table": tname})
            parts.append("**Indexes**\n\n")
            parts.append(md_table(idxs, ["indexname", "indexdef"]) if idxs else "_(none)_\n\n")

        # Geometry columns (PostGIS)
        geom_sql = """
        SELECT f_table_schema AS table_schema, f_table_name AS table_name, f_geometry_column AS column_name,
               srid, type
        FROM public.geometry_columns
        WHERE f_table_schema = :schema
        ORDER BY 1,2,3;
        """
        try:
            geoms = fetchall(engine, geom_sql, {"schema": schema})
            parts.append(md_h3("Geometry Columns (PostGIS)"))
            parts.append(md_table(geoms, ["table_schema", "table_name", "column_name", "srid", "type"]) if geoms else "_No geometry columns._\n\n")
        except Exception as e:
            parts.append(md_h3("Geometry Columns (PostGIS)"))
            parts.append(f"_Not available (geometry_columns view missing?). Error: {e}_\n\n")

        # Functions (user-defined) in this schema
        fn_sql = """
        SELECT p.proname AS function_name, pg_get_function_identity_arguments(p.oid) AS args
        FROM pg_proc p
        JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname = :schema
        ORDER BY 1;
        """
        fns = fetchall(engine, fn_sql, {"schema": schema})
        parts.append(md_h3("Functions"))
        parts.append(md_table(fns, ["function_name", "args"]) if fns else "_No functions._\n\n")

    md = "".join(parts)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Wrote Markdown to {args.out}")
    else:
        print(md)


if __name__ == "__main__":
    main()
