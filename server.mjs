import { createServer } from 'node:http';
import { DatabaseSync } from 'node:sqlite';
import { createReadStream, mkdirSync, statSync } from 'node:fs';
import { extname, join, normalize, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('.', import.meta.url));
const DATA = join(ROOT, 'data');
const DB_FILE = join(DATA, 'filomacchine.sqlite3');
const PORT = Number(process.env.FILOMACCHINE_PORT || 8765);
mkdirSync(DATA, { recursive: true });
const db = new DatabaseSync(DB_FILE);
db.exec(`PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS machines(id INTEGER PRIMARY KEY,name TEXT NOT NULL,type TEXT NOT NULL DEFAULT '',year INTEGER NOT NULL DEFAULT 0,serial TEXT NOT NULL DEFAULT '',hours REAL NOT NULL DEFAULT 0,next REAL NOT NULL DEFAULT 0,icon TEXT NOT NULL DEFAULT '🚜',service TEXT NOT NULL DEFAULT '',manual TEXT NOT NULL DEFAULT '',last TEXT NOT NULL DEFAULT '',cost REAL NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS works(id INTEGER PRIMARY KEY AUTOINCREMENT,date TEXT NOT NULL,machine INTEGER NOT NULL REFERENCES machines(id) ON DELETE CASCADE,activity TEXT NOT NULL,field TEXT NOT NULL DEFAULT '',operator TEXT NOT NULL DEFAULT '',hours REAL NOT NULL DEFAULT 0,cost REAL NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS services(id INTEGER PRIMARY KEY AUTOINCREMENT,date TEXT NOT NULL,machine INTEGER NOT NULL REFERENCES machines(id) ON DELETE CASCADE,activity TEXT NOT NULL,cost REAL NOT NULL DEFAULT 0);`);

const seed = {
  machines: [
    {id:1,name:'John Deere 6120M',type:'Trattore',year:2021,serial:'1L06120MCLL123456',hours:1284,next:1300,icon:'🚜',service:'Cambio olio e filtri',manual:'Manuale operatore · John Deere 6120M',last:'2025-08-14',cost:480},
    {id:2,name:'New Holland CX 5.80',type:'Mietitrebbia',year:2019,serial:'HACX580A0KX987654',hours:846,next:900,icon:'🌾',service:'Controllo pre-campagna',manual:'Manuale operatore · CX 5.80',last:'2025-06-22',cost:720},
    {id:3,name:'Massey Ferguson 5711',type:'Trattore',year:2022,serial:'V5711CFD03214567',hours:632,next:750,icon:'🚜',service:'Tagliando ordinario',manual:'Manuale operatore · MF 5711',last:'2025-09-03',cost:350}
  ],
  works: [
    {date:'2026-11-24',machine:1,activity:'Aratura',field:'Campo Nord',operator:'Marco Rossi',hours:6,cost:0},
    {date:'2026-11-23',machine:3,activity:'Semina grano',field:'Lotto 4',operator:'Luca Bianchi',hours:4.5,cost:0},
    {date:'2026-11-21',machine:1,activity:'Trasporto raccolto',field:'Podere Ovest',operator:'Marco Rossi',hours:3,cost:0},
    {date:'2026-11-19',machine:2,activity:'Raccolta mais',field:'Campo Sud',operator:'Paolo Verdi',hours:7,cost:0},
    {date:'2026-11-18',machine:3,activity:'Trattamento',field:'Vigneto',operator:'Luca Bianchi',hours:2.5,cost:0}
  ],
  services: [
    {date:'2025-08-14',machine:1,activity:'Cambio olio e filtri',cost:480},
    {date:'2025-06-22',machine:2,activity:'Manutenzione annuale',cost:720},
    {date:'2025-09-03',machine:3,activity:'Tagliando ordinario',cost:350}
  ]
};

function saveState(state) {
  const {machines=[],works=[],services=[]}=state||{};
  if (![machines,works,services].every(Array.isArray) || machines.length>1000 || works.length>100000 || services.length>100000) throw Error('Formato o numero di righe non valido');
  const ids=new Set(machines.map(x=>Number(x.id)));
  if ([...works,...services].some(x=>!ids.has(Number(x.machine)))) throw Error('Attività collegata a una macchina inesistente');
  db.exec('BEGIN IMMEDIATE');
  try {
    db.exec('DELETE FROM works; DELETE FROM services; DELETE FROM machines;');
    const machine=db.prepare('INSERT INTO machines(id,name,type,year,serial,hours,next,icon,service,manual,last,cost) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)');
    for(const x of machines) machine.run(Number(x.id),x.name,x.type||'',Number(x.year)||0,x.serial||'',Number(x.hours)||0,Number(x.next)||0,x.icon||'🚜',x.service||'',x.manual||'',x.last||'',Number(x.cost)||0);
    const work=db.prepare('INSERT INTO works(date,machine,activity,field,operator,hours,cost) VALUES(?,?,?,?,?,?,?)');
    for(const x of works) work.run(x.date,Number(x.machine),x.activity,x.field||'',x.operator||'',Number(x.hours)||0,Number(x.cost)||0);
    const service=db.prepare('INSERT INTO services(date,machine,activity,cost) VALUES(?,?,?,?)');
    for(const x of services) service.run(x.date,Number(x.machine),x.activity,Number(x.cost)||0);
    db.exec('COMMIT');
  } catch(error) { db.exec('ROLLBACK'); throw error; }
}
function getState() {
  return {
    machines: db.prepare('SELECT * FROM machines ORDER BY id').all(),
    works: db.prepare('SELECT date,machine,activity,field,operator,hours,cost FROM works ORDER BY id').all(),
    services: db.prepare('SELECT date,machine,activity,cost FROM services ORDER BY id').all()
  };
}
if (db.prepare('SELECT COUNT(*) AS count FROM machines').get().count===0) saveState(seed);

const mime={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.webmanifest':'application/manifest+json; charset=utf-8','.svg':'image/svg+xml','.jpg':'image/jpeg','.png':'image/png'};
const send=(res,status,body,type='application/json; charset=utf-8')=>{const data=Buffer.isBuffer(body)?body:Buffer.from(body);res.writeHead(status,{'Content-Type':type,'Content-Length':data.length,'X-Content-Type-Options':'nosniff','Cache-Control':'no-store'});res.end(data);};
const server=createServer((req,res)=>{
  const pathname=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);
  if(pathname==='/api/state'&&req.method==='GET') return send(res,200,JSON.stringify(getState()));
  if(pathname==='/api/state'&&req.method==='POST'){
    let raw='';req.on('data',chunk=>{raw+=chunk;if(raw.length>2_000_000){req.destroy();}});
    req.on('end',()=>{try{saveState(JSON.parse(raw));send(res,200,'{"saved":true}');}catch(error){send(res,400,JSON.stringify({error:error.message}));}});return;
  }
  if(req.method!=='GET') return send(res,405,JSON.stringify({error:'Metodo non supportato'}));
  const relative=pathname==='/'?'index.html':normalize(pathname.replace(/^[/\\]+/,''));
  const path=resolve(ROOT,relative);
  if(path!==ROOT&&!path.startsWith(ROOT+sep)) return send(res,403,'Non autorizzato','text/plain; charset=utf-8');
  if(path.startsWith(DATA+sep)) return send(res,404,'Non trovato','text/plain; charset=utf-8');
  try{if(!statSync(path).isFile()) throw Error();}catch{return send(res,404,'Non trovato','text/plain; charset=utf-8');}
  res.writeHead(200,{'Content-Type':mime[extname(path).toLowerCase()]||'application/octet-stream','X-Content-Type-Options':'nosniff','Cache-Control':'no-cache'});
  createReadStream(path).pipe(res);
});
server.listen(PORT,'127.0.0.1',()=>console.log(`filoMacchine attivo su http://127.0.0.1:${PORT}\nDatabase SQLite: ${DB_FILE}\nPremi CTRL+C per fermare il server.`));
for(const signal of ['SIGINT','SIGTERM']) process.on(signal,()=>{server.close(()=>{db.close();process.exit(0);});});
