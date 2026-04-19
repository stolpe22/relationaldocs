FETCH_TABLES_QUERY = """
    SELECT table_name
    FROM all_tables
    WHERE owner = :schema
    ORDER BY table_name
"""

FETCH_SCHEMAS_QUERY = """
    SELECT DISTINCT owner
    FROM all_tables
    ORDER BY owner
"""

FETCH_METADATA_QUERY = """
    SELECT
        c.table_name,
        c.column_id        AS col_order,
        c.column_name,
        c.data_type,
        c.char_length      AS data_length,
        c.data_precision,
        c.data_scale,
        c.nullable,
        c.data_default,
        cc.comments        AS col_comment,
        tc.comments        AS tbl_comment
    FROM all_tab_columns c
    LEFT JOIN all_col_comments cc
           ON cc.owner = c.owner
          AND cc.table_name = c.table_name
          AND cc.column_name = c.column_name
    LEFT JOIN all_tab_comments tc
           ON tc.owner = c.owner
          AND tc.table_name = c.table_name
    WHERE c.owner = :schema
      AND c.table_name IN ({placeholders})
    ORDER BY c.table_name, c.column_id
"""

FETCH_CONSTRAINTS_QUERY = """
    SELECT
        con.table_name,
        con.constraint_name,
        con.constraint_type,
        col.column_name,
        col.position,
        rcon.table_name   AS ref_table,
        rcol.column_name  AS ref_column,
        rcol.position     AS ref_position,
        con.search_condition
    FROM all_constraints con
    JOIN all_cons_columns col
      ON col.owner = con.owner
     AND col.constraint_name = con.constraint_name
    LEFT JOIN all_constraints rcon
           ON con.constraint_type = 'R'
          AND rcon.owner = con.r_owner
          AND rcon.constraint_name = con.r_constraint_name
    LEFT JOIN all_cons_columns rcol
           ON rcol.owner = rcon.owner
          AND rcol.constraint_name = rcon.constraint_name
          AND rcol.position = col.position
    WHERE con.owner = :schema
      AND con.table_name IN ({placeholders})
      AND con.constraint_type IN ('P', 'R', 'U', 'C')
      AND NOT (con.constraint_type = 'C' AND con.constraint_name LIKE 'SYS_C%')
    ORDER BY con.table_name, con.constraint_type, con.constraint_name, col.position
"""

FETCH_TRIGGERS_QUERY = """
    SELECT table_name, trigger_name, trigger_type, triggering_event, status
    FROM all_triggers
    WHERE owner = :schema
      AND table_name IN ({placeholders})
    ORDER BY table_name, trigger_name
"""

FETCH_IMPLICIT_RELATIONS_QUERY = """
    SELECT
        t1.column_name,
        t1.table_name AS table_1,
        t2.table_name AS table_2,
        t1.data_type
    FROM all_tab_columns t1
    JOIN all_tab_columns t2
      ON  t1.column_name = t2.column_name
     AND  t1.table_name  < t2.table_name
     AND  t1.data_type   = t2.data_type
    WHERE t1.owner = :schema
      AND t2.owner = :schema
      AND t1.table_name IN ({placeholders})
      AND t2.table_name IN ({placeholders})
      AND t1.column_name LIKE 'COD%'
    ORDER BY t1.column_name, t1.table_name, t2.table_name
"""
