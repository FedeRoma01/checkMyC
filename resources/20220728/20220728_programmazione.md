## **Specifiche Tecniche**

* **Linguaggio:** C (monoscript).
* **Input:** File di testo passato come argomento da linea di comando (`./a.out file_input`).
* **Formato Dati:** Numero ignoto di righe; ogni riga contiene esattamente **10 interi**.
* **Intervallo Valori:** $[-100.000, 100.000]$.
* **Vincoli Output:** Formattazione rigorosa (testo extra vietato, debug ammesso solo se preceduto da `#`).

## **Task: Richieste Funzionali**

### **1. Stampa al Contrario**

* Invertire l'ordine delle righe (dall'ultima alla prima).
* Invertire l'ordine dei numeri all'interno di ogni riga.
* **Tag:** `[CONTRARIO]`.

### **2. Distribuzione Valori**

* Analizzare solo i valori nel range $[-100, 100]$.
* Trovare il valore (o i valori) con la frequenza massima.
* Stampare i risultati in ordine crescente.
* **Tag:** `[DISTRIBUZIONE]`.

### **3. Confronto Righe Successive**

* Contare quante coppie di righe consecutive ($R_i$ e $R_{i+1}$) hanno almeno un numero in comune.
* **Tag:** `[NRIGHE]`.

### **4. Massimo e Minimo**

* Trovare il valore minimo e massimo assoluti nell'intero file.
* **Tag:** `[MIN-MAX]`.

### **5. Ordinamento**

* Calcolare la somma dei 10 numeri per ogni riga.
* Ordinare le righe in base alla loro somma (ordine crescente).
* Output: `num1 num2 ... num10 (somma)`.
* **Tag:** `[ORDINAMENTO]`.

---
