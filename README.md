# filoMacchine · app locale

Prototipo PWA per macchinari, registro lavori, promemoria e ricambi. Il backend usa solo Python standard library e SQLite: non richiede pacchetti Python aggiuntivi.

## Avvio rapido su Windows

1. Estrai `filomacchine-portable.zip` in una cartella.
2. Installa Python 3.8 o successivo se non è già presente.
3. Fai doppio clic su `start.bat`.
4. Si aprirà il browser su `http://127.0.0.1:8765`. La finestra “filoMacchine - server locale” deve restare aperta. Chiudila per fermare l’app.

Al primo avvio `server.py` crea la cartella `data` e il database `data/filomacchine.sqlite3`, prepara le tabelle SQLite e inserisce i dati demo. Ai successivi avvii conserva le modifiche. La PWA può essere installata dal browser quando è aperta sull’indirizzo locale.

## Dati locali

Macchine, lavori e manutenzioni vengono salvati in tabelle SQLite locali. Il database resta nella cartella `data` vicino all’app: per fare un backup copia `data/filomacchine.sqlite3`; per trasferire l’app su un altro computer copia anche il database. Lo ZIP distribuito non contiene il database e lo crea al primo avvio.

Il server ascolta solo su `127.0.0.1`, quindi è utilizzabile dal computer locale. Non espone il database sulla rete.

## Funzioni incluse

- Dashboard con tre macchine demo e scadenze di manutenzione.
- Schede macchina, registro lavori, chat aziendale dimostrativa, report ed esportazione CSV.
- Sezione filoMacchine 3D con immagine illustrativa, hotspot per cinque aree, schede ricambio e richiesta simulata.
- Chat guasti che propone una sezione da controllare a partire dal sintomo.
- Installazione PWA e cache della shell per riaprire l’interfaccia.

Codici, prezzi, disponibilità e compatibilità ricambi sono dimostrativi. La vista usa una foto con aree cliccabili e non un modello 3D; gli ordini non vengono inoltrati a un rivenditore. Le chat sono locali e non consultano manuali tecnici reali.
