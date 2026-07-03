---
name: db-consistency-check
description: MUST be used when checking consistency of the database models for this coursework across src/docs, report, and implementation code. Verifies that documented ER, PostgreSQL JSONB, PostgreSQL normalized, MongoDB nested, and MongoDB referenced models are internally logical, mutually consistent, reflected in the report, and not contradicted by application/loadgen/database code. Produces a verdict with exact locations, confidence, suspicions, and can prepare fixes after confirmation.
metadata:
  short-description: Check DB model consistency across docs, report, and code
---

# DB Consistency Check

Use this skill when the user asks to verify database/model consistency, compare `src/docs/` with the report, or find mismatches between model documentation and code.

Primary source of truth: `src/docs/`. If the report or code conflicts with `src/docs/`, report the conflict and be ready to fix the non-source-of-truth side unless `src/docs/` is itself incomplete or illogical.

## Scope

Check these model documents first:

- `src/docs/er.md`
- `src/docs/rel_jsonb.md`
- `src/docs/rel_norm.md`
- `src/docs/doc_nested.md`
- `src/docs/doc_norm.md`

If `doc_nested.md` or `doc_norm.md` is missing, also inspect likely legacy/report counterparts such as `report/Content/033_mdb_nested.tex` and `report/Content/034_mdb_ref.tex`, but still flag the missing `src/docs/` files as an inconsistency with the project instructions.

Then inspect:

- `report/content.tex` and relevant `report/Content/*.tex`
- `src/apps/server/`
- `src/apps/loadgen/`
- database setup/migration/compose files if present
- `src/docs/architecture.md`, `src/docs/database.md`, and `src/docs/scenario.md` when they describe storage behavior

## Required Workflow

1. Run the helper scan from the repository root:

   ```bash
   python3 .agents/skills/db-consistency-check/scripts/scan_db_consistency.py
   ```

   Treat the scan as an index and suspicion generator, not as final proof.

2. Build a compact source-of-truth map from `src/docs/`:

   - ER entities, attributes, identifiers, and cardinalities.
   - PostgreSQL JSONB tables, columns, JSONB columns, keys, foreign keys, and bridge tables.
   - PostgreSQL normalized tables, columns, decomposed tables, keys, and foreign keys.
   - MongoDB nested collections, embedded documents/arrays, references if any.
   - MongoDB normalized/reference collections and `$ref` links.

3. Check internal logic of each model:

   - Every FK/reference points to an existing table/collection/entity.
   - Every many-to-many relationship has a bridge table/collection or an explicitly embedded representation.
   - Every 1:0..1 relationship has a unique constraint or equivalent explanation.
   - Surrogate keys and alternate/business keys are consistently named.
   - JSONB fields are only used in JSONB/document models; fully normalized model decomposes them.
   - Telemetry/log naming is consistent. If ER says `CameraTelemetry` but implementation models use `camera_log`, flag this unless the text explicitly explains the mapping.
   - Event payload/object/alert relationships remain equivalent across model variants.

4. Compare models to each other:

   - `rel_jsonb.md` and `rel_norm.md` should preserve the same conceptual entities and relationships from `er.md`.
   - Normalized PostgreSQL should decompose JSONB/composite fields from JSONB PostgreSQL without losing meaning.
   - MongoDB nested and normalized/reference models should represent the same information as the PostgreSQL models, with intentional differences explained.
   - The report should not introduce fields, tables, collections, or relationship cardinalities absent from `src/docs/` unless it explicitly says they are implementation details.

5. Compare report text:

   - Use `rg -n` for table/collection/entity names and key field names.
   - Check sections under model design and implementation, especially `report/Content/021_entites.tex`, `022_relations.tex`, `023_er.tex`, `032_pg_jsonb.tex`, `032_pg_norm.tex`, `033_mdb_nested.tex`, `034_mdb_ref.tex`, and `042_dbs.tex`.
   - Verify names and semantics, not only string equality. LaTeX escaping (`event\_payload`) is equivalent to Markdown/code (`event_payload`).

6. Compare code:

   - Search for SQL DDL/DML, Mongo collection usage, struct field names, API payload names, scenario/load generation payloads, and env/config names.
   - If code only contains connection plumbing and no schema operations, say that the code currently gives no strong evidence of schema conformance instead of inventing a mismatch.
   - If migrations or seed scripts exist, compare them table-by-table and collection-by-collection against `src/docs/`.

## Verdict Format

Lead with one of:

- `Вердикт: соответствует`
- `Вердикт: не соответствует`
- `Вердикт: есть подозрения на расхождение`

Then list findings sorted by severity:

- `Критично` - contradiction that makes the model/report/code wrong.
- `Средне` - likely mismatch, missing source file, naming drift, or unverified implementation detail.
- `Низко` - unclear wording, style drift, or weak suspicion.

Each finding must include:

- exact file and line reference;
- what `src/docs/` says;
- what the report/code says;
- why this is a mismatch or suspicion;
- suggested fix direction.

If no mismatch is found, still include residual risk: which files were checked and what could not be verified.

## Fixing

When the user asks to fix:

- Fix the smallest non-source-of-truth artifact first: usually report text or code comments.
- Update `src/docs/` only if the model document is missing, internally contradictory, or clearly stale compared with a deliberate implementation.
- After edits, rerun the helper scan and manually re-check the affected files.
- If adding or renaming `src/docs/` files, update any repository file-structure descriptions that mention model files.

