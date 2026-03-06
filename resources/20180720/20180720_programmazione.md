## **Specifiche Tecniche**

* **Linguaggio:** C (monoscript).
* **Input:** File di testo da linea di comando (`./a.out nome_input_file`).
* **Formato Dati:** Righe con `timestamp` (ms da mezzanotte) e `comando` (stringa).
* **Comandi validi:** `OFF`, `LIGHT`, `L`, `M`, `H`, `1h`, `3h` (case-sensitive).
* **Stato Iniziale (Mezzanotte):** Luce **ACCESA**, Ventola **SPENTA**.
* **Vincoli:** Output rigoroso; righe di debug precedute da `#`.

## **Task: Richieste Funzionali**

### **1. Pulsante maggiormente premuto**

* Identificare il comando con il maggior numero di occorrenze.
* In caso di parità, dare priorità al comando che appare per primo nel file.
* **Tag:** `[MAX-PRESSIONI]`.

### **2. Tempo medio di accensione della luce**

* Calcolare la durata media di accensione della lampada (toggle tramite `LIGHT`).
* Se l'ultimo stato è "acceso", considerarla accesa fino a fine giornata (mezzanotte successiva).
* Arrotondare il risultato in secondi per difetto.
* **Tag:** `[MEDIA-LUCE]`.

### **3. Durata velocità Alta (H)**

* Calcolare il tempo totale in cui la ventola è rimasta su **H**.
* **Nota:** Ignorare gli effetti dei timer (`1h`, `3h`) per questo calcolo.
* Se non interrotto, contare fino a mezzanotte.
* **Tag:** `[TOT-ALTA-VELOCITA]`.

### **4. Tempo totale accensione ventola**

* Calcolare la durata totale in cui la ventola è stata attiva (qualsiasi velocità: L, M, H).
* **Nota:** Ignorare gli effetti dei timer (`1h`, `3h`).
* Se non interrotto da `OFF`, contare fino a mezzanotte.
* **Tag:** `[TOT-ACCENSIONE]`.

### **5. Ordinamento**

* Ordinare le righe del file alfabeticamente per comando (`strcmp`).
* In caso di comandi identici, ordinare per timestamp crescente.
* **Tag:** `[ORDINAMENTO]`.

---