"""Local filoMacchine app server with SQLite persistence (Python standard library only)."""
from __future__ import annotations

import json
import os
import sqlite3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "filomacchine.sqlite3"
PORT = int(os.environ.get("FILOMACCHINE_PORT", "8765"))

SEED = {
    "machines": [
        {"id": 1, "name": "John Deere 6120M", "type": "Trattore", "year": 2021, "serial": "1L06120MCLL123456", "hours": 1284, "next": 1300, "icon": "🚜", "service": "Cambio olio e filtri", "manual": "Manuale operatore · John Deere 6120M", "last": "2025-08-14", "cost": 480},
        {"id": 2, "name": "New Holland CX 5.80", "type": "Mietitrebbia", "year": 2019, "serial": "HACX580A0KX987654", "hours": 846, "next": 900, "icon": "🌾", "service": "Controllo pre-campagna", "manual": "Manuale operatore · CX 5.80", "last": "2025-06-22", "cost": 720},
        {"id": 3, "name": "Massey Ferguson 5711", "type": "Trattore", "year": 2022, "serial": "V5711CFD03214567", "hours": 632, "next": 750, "icon": "🚜", "service": "Tagliando ordinario", "manual": "Manuale operatore · MF 5711", "last": "2025-09-03", "cost": 350},
    ],
    "works": [
        {"date": "2026-11-24", "machine": 1, "activity": "Aratura", "field": "Campo Nord", "operator": "Marco Rossi", "hours": 6, "cost": 0},
        {"date": "2026-11-23", "machine": 3, "activity": "Semina grano", "field": "Lotto 4", "operator": "Luca Bianchi", "hours": 4.5, "cost": 0},
        {"date": "2026-11-21", "machine": 1, "activity": "Trasporto raccolto", "field": "Podere Ovest", "operator": "Marco Rossi", "hours": 3, "cost": 0},
        {"date": "2026-11-19", "machine": 2, "activity": "Raccolta mais", "field": "Campo Sud", "operator": "Paolo Verdi", "hours": 7, "cost": 0},
        {"date": "2026-11-18", "machine": 3, "activity": "Trattamento", "field": "Vigneto", "operator": "Luca Bianchi", "hours": 2.5, "cost": 0},
    ],
    "services": [
        {"date": "2025-08-14", "machine": 1, "activity": "Cambio olio e filtri", "cost": 480},
        {"date": "2025-06-22", "machine": 2, "activity": "Manutenzione annuale", "cost": 720},
        {"date": "2025-09-03", "machine": 3, "activity": "Tagliando ordinario", "cost": 350},
    ],
}


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def initialize_database() -> None:
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS machines (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL, type TEXT NOT NULL DEFAULT '',
                year INTEGER NOT NULL DEFAULT 0, serial TEXT NOT NULL DEFAULT '',
                hours REAL NOT NULL DEFAULT 0, next REAL NOT NULL DEFAULT 0,
                icon TEXT NOT NULL DEFAULT '🚜', service TEXT NOT NULL DEFAULT '',
                manual TEXT NOT NULL DEFAULT '', last TEXT NOT NULL DEFAULT '', cost REAL NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS works (
                id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL,
                machine INTEGER NOT NULL REFERENCES machines(id) ON DELETE CASCADE,
                activity TEXT NOT NULL, field TEXT NOT NULL DEFAULT '',
                operator TEXT NOT NULL DEFAULT '', hours REAL NOT NULL DEFAULT 0, cost REAL NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL,
                machine INTEGER NOT NULL REFERENCES machines(id) ON DELETE CASCADE,
                activity TEXT NOT NULL, cost REAL NOT NULL DEFAULT 0
            );
        """)
        if db.execute("SELECT COUNT(*) FROM machines").fetchone()[0] == 0:
            save_state(db, SEED)


def get_state(db: sqlite3.Connection) -> dict:
    machines = [dict(row) for row in db.execute("SELECT * FROM machines ORDER BY id")]
    works = [dict(row) for row in db.execute("SELECT date,machine,activity,field,operator,hours,cost FROM works ORDER BY id")]
    services = [dict(row) for row in db.execute("SELECT date,machine,activity,cost FROM services ORDER BY id")]
    return {"machines": machines, "works": works, "services": services}


def save_state(db: sqlite3.Connection, state: dict) -> None:
    machines = state.get("machines", [])
    works = state.get("works", [])
    services = state.get("services", [])
    if not all(isinstance(x, list) for x in (machines, works, services)):
        raise ValueError("Formato dati non valido")
    if len(machines) > 1000 or len(works) > 100000 or len(services) > 100000:
        raise ValueError("Numero di righe superiore al limite")
    machine_ids = {int(m["id"]) for m in machines}
    if any(int(w["machine"]) not in machine_ids for w in works + services):
        raise ValueError("Un’attività fa riferimento a una macchina inesistente")
    with db:
        db.execute("DELETE FROM works")
        db.execute("DELETE FROM services")
        db.execute("DELETE FROM machines")
        db.executemany("""INSERT INTO machines(id,name,type,year,serial,hours,next,icon,service,manual,last,cost)
            VALUES(:id,:name,:type,:year,:serial,:hours,:next,:icon,:service,:manual,:last,:cost)""", machines)
        db.executemany("""INSERT INTO works(date,machine,activity,field,operator,hours,cost)
            VALUES(:date,:machine,:activity,:field,:operator,:hours,:cost)""", works)
        db.executemany("INSERT INTO services(date,machine,activity,cost) VALUES(:date,:machine,:activity,:cost)", services)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store" if self.path.startswith("/api/") else "no-cache")
        super().end_headers()

    def do_GET(self) -> None:
        if urlparse(self.path).path == "/api/state":
            with connect() as db:
                body = json.dumps(get_state(db), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if urlparse(self.path).path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/state":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 2_000_000:
                raise ValueError("Richiesta vuota o troppo grande")
            state = json.loads(self.rfile.read(length))
            if not isinstance(state, dict):
                raise ValueError("Formato dati non valido")
            with connect() as db:
                save_state(db, state)
            body = b'{"saved":true}'
            self.send_response(200)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError, sqlite3.IntegrityError) as exc:
            body = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
            self.send_response(400)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")


if __name__ == "__main__":
    initialize_database()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"filoMacchine attivo su http://127.0.0.1:{PORT}")
    print(f"Database SQLite: {DB_PATH}")
    print("Per fermare il server premi CTRL+C in questa finestra.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Arresto filoMacchine...")
    finally:
        server.server_close()
