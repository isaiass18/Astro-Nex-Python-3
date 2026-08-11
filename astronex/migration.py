import os
import shutil
import sqlite3
from .extensions.path import path

def migrate_v2_data():
    home_v1 = path.joinpath(path.expanduser(path('~')), '.astronex')
    home_v2 = path.joinpath(path.expanduser(path('~')), '.astronex-v2')
    
    if not path.exists(home_v2):
        return
        
    if not path.exists(home_v1):
        try:
            os.rename(str(home_v2), str(home_v1))
        except Exception as e:
            print(f"Error renaming v2 to v1: {e}")
        return

    backup_dir = path.joinpath(path.expanduser(path('~')), '.astronex-backup-pre-2.0')
    if not path.exists(backup_dir):
        try:
            shutil.copytree(str(home_v1), str(backup_dir))
        except Exception as e:
            print(f"Error backing up v1 data: {e}")
            return

    try:
        _merge_databases(home_v1, home_v2)
        shutil.move(str(home_v2), str(home_v2) + "-migrated")
    except Exception as e:
        print(f"Migration error: {e}")

def _merge_databases(home_v1, home_v2):
    db1 = path.joinpath(home_v1, "charts.db")
    db2 = path.joinpath(home_v2, "charts.db")
    if path.exists(db2):
        conn1 = sqlite3.connect(str(db1))
        conn2 = sqlite3.connect(str(db2))
        _merge_charts(conn1, conn2)
        conn1.close()
        conn2.close()
        
    db1_custom = path.joinpath(home_v1, "customloc.db")
    db2_custom = path.joinpath(home_v2, "customloc.db")
    if path.exists(db2_custom):
        conn1 = sqlite3.connect(str(db1_custom))
        conn2 = sqlite3.connect(str(db2_custom))
        _merge_customloc(conn1, conn2)
        conn1.close()
        conn2.close()

def _merge_charts(conn1, conn2):
    c1 = conn1.cursor()
    c2 = conn2.cursor()
    
    c2.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c2.fetchall()]
    
    for tbl in tables:
        c2.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tbl,))
        schema_row = c2.fetchone()
        if not schema_row: continue
        schema = schema_row[0]
        
        try:
            c1.execute(schema)
        except sqlite3.OperationalError:
            pass
            
        c2.execute(f'PRAGMA table_info("{tbl}")')
        cols = [row[1] for row in c2.fetchall()]
        col_names = ", ".join([f'"{c}"' for c in cols])
        placeholders = ", ".join(["?"] * len(cols))
        
        c2.execute(f'SELECT * FROM "{tbl}"')
        rows = c2.fetchall()
        for row in rows:
            first = row[cols.index('first')]
            last = row[cols.index('last')]
            date = row[cols.index('date')]
            lat = row[cols.index('latitud')]
            lon = row[cols.index('longitud')]
            
            try:
                c1.execute(f'INSERT INTO "{tbl}" ({col_names}) VALUES ({placeholders})', row)
            except sqlite3.IntegrityError:
                c1.execute(f'SELECT date, latitud, longitud FROM "{tbl}" WHERE first=? AND last=?', (first, last))
                existing = c1.fetchone()
                if existing:
                    ex_date, ex_lat, ex_lon = existing
                    if ex_date == date and ex_lat == lat and ex_lon == lon:
                        continue
                    else:
                        new_last = last + " (v2)"
                        new_row = list(row)
                        new_row[cols.index('last')] = new_last
                        try:
                            c1.execute(f'INSERT INTO "{tbl}" ({col_names}) VALUES ({placeholders})', new_row)
                        except sqlite3.IntegrityError:
                            pass
    conn1.commit()

def _merge_customloc(conn1, conn2):
    c1 = conn1.cursor()
    c2 = conn2.cursor()
    c2.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c2.fetchall()]
    
    for tbl in tables:
        c2.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tbl,))
        schema_row = c2.fetchone()
        if not schema_row: continue
        try:
            c1.execute(schema_row[0])
        except sqlite3.OperationalError:
            pass
            
        c2.execute(f'PRAGMA table_info("{tbl}")')
        cols = [row[1] for row in c2.fetchall()]
        col_names = ", ".join([f'"{c}"' for c in cols])
        placeholders = ", ".join(["?"] * len(cols))
        
        c2.execute(f'SELECT * FROM "{tbl}"')
        for row in c2.fetchall():
            try:
                check_sql = f'SELECT 1 FROM "{tbl}" WHERE ' + " AND ".join([f'"{c}"=?' for c in cols])
                c1.execute(check_sql, row)
                if not c1.fetchone():
                    c1.execute(f'INSERT INTO "{tbl}" ({col_names}) VALUES ({placeholders})', row)
            except sqlite3.IntegrityError:
                pass
    conn1.commit()
