# *Bluesky Report.py*

Aquest document resumeix el funcionament i l'estructura del script bluesky_report.py, que genera un informe automàtic sobre l'activitat i xarxa d'un usuari de Bluesky.

---

## *Divisió General del projecte*

- *Primera part*  
  Extracció de dades i creació dels gràfics bàsics (gràfic de seguidors i gràfic de threads) a partir de l’API de Bluesky. Aquest pas permet obtenir els fitxers .gt que després s’analitzen.  

- *Segona part, seguidors*  
  Anàlisi del gràfic de seguidors:  
  - Detecció de comunitats.  
  - Identificació d’influents i receptors d’informació (mètodes de grau sortida i entrada).  
  - Cerca de possibles competidors basat en closseness centrality.
  - Ordre de seguidors per reputació.  
  - Generació de visualitzacions: imatges dels graf de seguidors i dels graf de comunitats (PNG).  

- *Segona part, threads*  
  Anàlisi del gràfic de threads (converses):  
  - Càlcul de punts de pas (nodes d’articulació que mantenen connectades parts de la conversa).  
  - Detecció de vèrtexs de sortida (usuaris que difonen converses fora de la base de seguidors del client).  
  - Generació de visualitzacions: imatges del graf de threads amb els punts de pas i vèrtexs destacats.  

- *Tercera part, bluesky_report.py`*  
  Orquestra tot el flux:  
  1. Neteja de fitxers antics (eliminació de .gt i .png obsolets).  
  2. Crida als mòduls d’extracció per crear els graf (primera_part).  
  3. Carrega dels graf amb graph-tool per fer els càlculs d’anàlisi (segona_part).  
  4. Generació d’un informe en text (.txt) amb totes les mètriques i recomanacions.  
  5. Creació d’un PDF final mitjançant fpdf2.

---

## *Generació de l’informe de text*

- S’obre un fitxer .txt (bluesky-report-<HANDLE>.txt) i s’hi escriu:  
  - Primera part: nom del client i data de creació de l’informe.  
  - Explicació de l’objectiu i l’abast de l’anàlisi.  
  - Estadístiques principals del gràfic de seguidors:  
    - Nombre de vèrtexs i arestes.  
    - Densitat de la xarxa i comentari contextual (alta o baixa connectivitat).  
    - Nombre de comunitats i recomanacions segons la quantitat detectada.  
    - Identificació d’influents i receptors amb suggeriments (col·laboracions, estratègies).  
    - Informació sobre possibles competidors segons la centralitat de proximitat.  
    - Ordre de seguidors per reputació amb els cinc primers destacats.  
  - Anàlisi de l’activitat en threads (gràfic de converses):  
    - Nombre total d’interaccions i nombre de participants.  
    - Descripció de l’aresta amb més pes (parell d’usuaris amb més interaccions).  
    - Comentari segons el volum d’interaccions (< 50 o ≥ 50).  
    - Llista de punts de pas amb etiquetes per a canals de difusió (excel·lent, bona influència).  
    - Llista de vèrtexs de sortida amb comentaris per a usuaris que difonen a públic extern.  
  - En tots aquests punts s’inclouen condicionalment comentaris que personalitzen l’informe en funció dels resultats obtinguts (per exemple, si la densitat supera un llindar, si hi ha més de 20 interaccions en un punt de pas, etc.).  

---

## *Creació del PDF*

- Utilitzant la biblioteca fpdf2, es llegeix línia a línia el fitxer .txt i s’escriu en cel·les multillarga (multi_cell) per mantenir un format coherent.  
- S’afegeixen automàticament les imatges dels gràfics generats:  
  1. graf_seguidors_<HANDLE>.png  
  2. graf_comunitats_<HANDLE>.png  
  3. graf_threads_<HANDLE>.png  
- El PDF resultants s’anomena bluesky-report-<HANDLE>.pdf i combina text i imatges disposades en una o diverses pàgines, amb salts de pàgina automàtics si cal.  
- El procés imprimeix per consola un missatge de confirmació amb la ruta del PDF creat.

---

## *Decisions de disseny*

- *Comentaris condicionals per personalitzar l’informe*  
  - S’han definit llindars per mostrar missatges adaptats. 

- *Neteja prèvia de fitxers*  
  - Abans de generar nous informes, es busquen i s’eliminen tots els fitxers .gt i .png de l’execució anterior (tanto de seguidors com de comunitats i threads).  
  - Això evita confusions amb dades antigues i garanteix que cada execució sigui idempotent, és a dir, que comenci en un estat net sense residus.  

- *Biblioteques*  
  - **graph-tool** : per treballar amb grafs.
  - **fpdf2** : per crear documents PDF amb text i imatges.

- *Problemes de compatibilitat*  
  - No s’ha pogut integrar la generació d’imatges en format SVG a causa d’incompatibilitats de graph-tool amb certes versions de llibreries de renderitzat. Finalment s’opta per PNG com a format universal.  

- *Ubicació dels arxius generats*
  - Els grafs generats es trobaran a la carpeta segona_part a dins de seguidors i threads depenent del tipus, i a dins de les carpetes graf_seguidors i graf_threads també respectivament.
  - El Report es genera a la mateixa carpeta que el codi principal, a tercera_part

---

## *Ús*
- Instal.la els paquets necessaris  (pip install fpdf2 graph-tool).
- Executa el programa i esriu el client que es vol analitzar un cop es demani a la terminal (handle).
- Després d'un cert temps, es generaran els següents fitxers: 
	-Un fitxer .txt amb l’informe complet escrit.
	-Un fitxer .pdf que combina el text amb les imatges dels gràfics.
	-Diverses imatges .png dels gràfics de seguidors i de threads (es guarden a les carpetes grafs_seguidors/ i grafs_threads/ ).