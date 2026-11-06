"""SQLite reservations made before every attempt, including failed requests."""
from __future__ import annotations
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

class BudgetExceeded(RuntimeError): pass

class Ledger:
    def __init__(self, path: str|Path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS calls (id INTEGER PRIMARY KEY, scope TEXT NOT NULL, task_id TEXT NOT NULL, provider TEXT NOT NULL, purpose TEXT NOT NULL, status TEXT NOT NULL, created TEXT NOT NULL, detail TEXT, model TEXT, input_tokens INTEGER, output_tokens INTEGER)")
    def _connect(self):
        db=sqlite3.connect(self.path,timeout=30,isolation_level=None)
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA busy_timeout=30000")
        return db
    def reserve(self, *, scope:str, task_id:str, provider:str, purpose:str, cap:int, model:str="") -> int:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            count=db.execute("SELECT count(*) FROM calls WHERE scope=? AND task_id=?",(scope,task_id)).fetchone()[0]
            if count>=cap:
                db.execute("ROLLBACK"); raise BudgetExceeded(f"{scope} call budget exhausted ({count}/{cap})")
            cur=db.execute("INSERT INTO calls(scope,task_id,provider,purpose,status,created,model) VALUES(?,?,?,?,?,?,?)",(scope,task_id,provider,purpose,"reserved",datetime.now(timezone.utc).isoformat(),model))
            call_id=cur.lastrowid;db.execute("COMMIT");return call_id
    def finish(self,call_id:int,status:str,detail:str="",input_tokens:int|None=None,output_tokens:int|None=None) -> None:
        with self._connect() as db:
            db.execute("UPDATE calls SET status=?,detail=?,input_tokens=?,output_tokens=? WHERE id=?",(status,detail[:1000],input_tokens,output_tokens,call_id))
    def rows(self,task_id:str):
        with self._connect() as db:
            return db.execute("SELECT id,scope,provider,purpose,status,created,detail,model,input_tokens,output_tokens FROM calls WHERE task_id=? ORDER BY id",(task_id,)).fetchall()

    def summary(self,task_id=None):
        """Actual dispatch accounting only; never emit prompts, keys or error detail."""
        from collections import Counter
        with self._connect() as db:
            query='SELECT task_id,scope,provider,purpose,status,input_tokens,output_tokens FROM calls'
            rows=db.execute(query+(' WHERE task_id=?' if task_id is not None else ''),
                (task_id,) if task_id is not None else ()).fetchall()
        known=sum(r[5] is not None and r[6] is not None for r in rows)
        return {'task_filter':task_id,'total_calls':len(rows),
            'by_task':dict(Counter(r[0] for r in rows)),
            'by_scope':dict(Counter(r[1] for r in rows)),
            'by_provider':dict(Counter(r[2] for r in rows)),
            'by_role':dict(Counter(r[3].split(':',1)[0] for r in rows)),
            'by_status':dict(Counter(r[4] for r in rows)),
            'reported_input_tokens':sum(r[5] or 0 for r in rows),
            'reported_output_tokens':sum(r[6] or 0 for r in rows),
            'calls_with_reported_usage':known,'unknown_usage_calls':len(rows)-known,
            'usage_note':'Token sums cover reported usage only; unknown usage and hidden provider network attempts are not inferred.'}
