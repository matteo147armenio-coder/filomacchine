# filoMacchine · app locale

Prototipo PWA per macchinari, registro lavori, promemoria e ricambi. Il backend usa Python standard library e SQLite, oppure Node.js 22.5+ con `node:sqlite`; non richiede pacchetti aggiuntivi.

## Avvio rapido su Windows

1. Scarica `filomacchine-portable.zip` dal repository GitHub e salvalo sul computer.
2. Estrai il file ZIP in una cartella. Se hai scaricato `Source code (zip)` da GitHub, estrai quello e apri la cartella `filomacchine-main`.
3. Verifica che sia installato Python 3.8+ oppure Node.js 22.5+.
4. Fai doppio clic su `start.bat` nella cartella estratta.
5. Si aprirà il browser sulla porta locale scelta da `start.bat`. La finestra “filoMacchine - server locale” deve restare aperta. Chiudila per fermare il server.

Se filoMacchine è già in esecuzione, `start.bat` riapre l’istanza esistente senza avviare un server duplicato. Se la porta predefinita è occupata da un altro programma, seleziona automaticamente la successiva porta locale disponibile.

Al primo avvio `start.bat` sceglie un runtime disponibile e crea la cartella `data` e il database `data/filomacchine.sqlite3`, prepara le tabelle SQLite e inserisce i dati demo. Usa `server.py` se trova Python o `server.mjs` se trova Node. Ai successivi avvii conserva le modifiche. La PWA può essere installata dal browser quando è aperta sull’indirizzo locale.

## Dati locali

Macchine, lavori e manutenzioni vengono salvati in tabelle SQLite locali. Il database resta nella cartella `data` vicino all’app: per fare un backup copia `data/filomacchine.sqlite3`; per trasferire l’app su un altro computer copia anche il database. Lo ZIP distribuito non contiene il database e lo crea al primo avvio.

Il server ascolta solo su `127.0.0.1`, quindi è utilizzabile dal computer locale. Non espone il database sulla rete.

## Funzioni incluse

- Dashboard con tre macchine demo e scadenze di manutenzione.
- Schede macchina, registro lavori, chat aziendale dimostrativa, report ed esportazione CSV.
- Pannello assistente laterale con contesto aggiornato in base alla sezione aperta. L’accesso ChatGPT non è ancora collegato.
- Sezione filoMacchine 3D con immagine illustrativa, hotspot per cinque aree, schede ricambio e richiesta simulata.
- Chat guasti che propone una sezione da controllare a partire dal sintomo.
- Installazione PWA e cache della shell per riaprire l’interfaccia.

Codici, prezzi, disponibilità e compatibilità ricambi sono dimostrativi. La vista usa una foto con aree cliccabili e non un modello 3D; gli ordini non vengono inoltrati a un rivenditore. Le chat sono locali e non consultano manuali tecnici reali.
