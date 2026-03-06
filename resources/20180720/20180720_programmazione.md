# 20180720 – Programmazione

## Fondamenti di Informatica  
20/07/2018

## Contesto
Si consideri un ventilatore da soffitto come quello rappresentato nella figura a sinistra. Il ventilatore, che integra una lampada, viene controllato tramite il telecomando mostrato nella figura a destra.

Il telecomando dispone di **7 pulsanti** con le seguenti funzionalità:

- **OFF** – Spegnimento della ventola.  
- **LIGHT** – Accensione/spegnimento della luce; se la luce è accesa, la pressione del pulsante la spegne e viceversa.  
- **L / M / H** – Accensione della ventola rispettivamente a velocità *bassa*, *media*, *alta*.  
- **1h / 3h** – Impostano un timer per lo spegnimento automatico della ventola dopo 1 ora o 3 ore.  
  - Se il timer è già impostato, la pressione di uno dei due pulsanti lo riavvia.  
  - Se la ventola è spenta, il comando del timer non ha effetto.

Il ventilatore è inserito in un sistema di automazione domestica che riceve e registra i comandi in un file di testo, uno per riga.

### Formato linea del file
```
timestamp comando
```

- **timestamp**: millisecondi trascorsi dalla mezzanotte del giorno corrente  
- **comando**: uno tra `{OFF, LIGHT, L, M, H, 1h, 3h}` (case‑sensitive)

Le registrazioni sono in ordine crescente di timestamp.  
A mezzanotte: **luce accesa**, **ventola spenta**.

### Esempio di file
```
10000 LIGHT
15050 L
20132 1h
21000 OFF
```

---

## Specifiche del Programma Richiesto

Il programma C deve elaborare un file nel formato descritto ed essere invocabile da linea di comando:

```
./a.out nome_input_file
```

Il programma deve produrre **esattamente** gli output richiesti, senza testo aggiuntivo.  
Le righe di debug devono iniziare con `#`.

Per verificare il funzionamento:
```
./pvcheck ./a.out
```

---

## Richieste

### 1. Pulsante maggiormente premuto
Determinare il pulsante con il maggior numero di pressioni.  
In caso di parità, scegliere quello che compare **prima** nel file.

Output:
```
[MAX-PRESSIONI]
comando
```

---

### 2. Tempo medio di accensione della luce
Calcolare il tempo totale in cui la luce è stata accesa.  
Arrotondare ai secondi **per difetto**.

Se l’ultimo comando LIGHT accende la luce, considerarla accesa fino a mezzanotte.

Output:
```
[MEDIA-LUCE]
MEDIA
```

---

### 3. Tempo totale di accensione della ventola a velocità alta
Calcolare la durata totale della ventola alla velocità impostata con il comando **H**, ignorando gli effetti del timer.

Se non arriva più un comando che modifica la velocità o spegne la ventola, considerare attiva fino a mezzanotte.

Output:
```
[TOT-ALTA-VELOCITA]
DURATA
```

---

### 4. Tempo totale di accensione della ventola (qualsiasi velocità)
Calcolare il tempo totale di accensione della ventola, indipendentemente dalla velocità, ignorando i timer.

Se non arriva un OFF dopo un'accensione, considerarla accesa fino a mezzanotte.

Output:
```
[TOT-ACCENSIONE]
DURATA
```

---

### 5. Ordinamento
Ordinare alfabeticamente (strcmp) le misurazioni in base al comando.  
A parità di comando, ordinare per timestamp crescente.  
Non esistono due righe con lo stesso timestamp.

Output:
```
[ORDINAMENTO]
timestamp_1 comando_1
...
timestamp_n comando_n
```

---

## Note Finali
- Salvare il programma nella directory di lavoro.  
- Nome file: **cognome.c**  
- Il primo commento del programma deve contenere: nome, cognome, matricola.  
- Sono valutati positivamente leggibilità, formattazione, commenti, modularità e generalità.  
- Si possono usare manuali, testi, appunti, dispense. Non eserciziari.
