# Fondamenti di Informatica 28/07/2022

* salvare il proprio programma nella directory di lavoro
* assegnare il nome del file in base al proprio cognome, chiamandolo con il proprio (es. `facchinetti.c`)
* il primo commento del programma deve riportare **nome** e **cognome** e **numero di matricola**
* vengono valutati positivamente aspetti quali la leggibilità del programma, una buona formattazione del sorgente, l'uso appropriato dei commenti, modularità e generalità del codice
* è possibile far uso di manuali, testi, appunti e dispense, ma non di eserciziari (raccolte di esercizi risolti)

ATTENZIONE: la directory di lavoro contiene già un file denominato con il proprio cognome. Si può semplicemente aprirlo e scrivere il programma.

# Contesto

Un file di testo è composto da righe ciascuna delle quali contiene esattamente 10 valori numerici interi separati da spazi.

Un esempio di tale file è il seguente:

    1 2 3 4 5 6 7 8 9 10
    10 20 30 40 50 60 70 80 90 100 

Il numero di righe non è noto.
i valori interi possono essere sia positivi che negativi e possono avere valori nell'intervallo [-100000, 100000].

# Informazioni sul programma richiesto

Si scriva un programma in linguaggio C in grado di elaborare un file avente il formato descritto, al fine di restituire i risultati richiesti nei punti specificati di seguito.
Il programma deve poter essere invocato da linea di comando. 
Un esempio di invocazione è la seguente:

    ./a.out nome_input_file

dove **a.out** è il nome del programma eseguibile da invocare; **nome_input_file** è il nome del file di dati da elaborare.

Il buon funzionamento del programma può essere verificato col comando

    pvcheck ./a.out

dove **a.out** è il nome del file eseguibile.


**IMPORTANTE**: il programma finale dovrà produrre la stampa di risultati _esattamente_ col formato specificato nei vari punti.
In particolare, _non aggiungere all'output del testo non richiesto_.

Eventuali righe di output aggiuntive che si vogliono generare in fase di debug, ma che si vogliono escludere dai test, possono essere stampate includendo in prima posizione il carattere `#`.

# RICHIESTE

# 1) Stampa al contrario

Stampare il contenuto del file al contrario, sia per quanto riguarda le righe che per quanto riguarda i numeri in ciascuna riga.

Si stampi quindi l'intero contenuto del file partendo dall'ultima riga fino alla prima.
Per ciascuna riga, stampare i numeri dall'ultimo al primo, separandoli con un singolo spazio.

Esempio di formato, basato sul file di esempio sopra riportato:

    [CONTRARIO]
    100 90 80 70 60 50 40 30 20 10
    10 9 8 7 6 5 4 3 2 1

# 2) Distribuzione valori

Considerando solo i valori compresi nell'intervallo [-100, 100], estremi compresi, conteggiare i valori che compaiono più frequentemente nel file.

Stampare tali valori con il seguente formato (esempio basato sul file sopra riportato):

    [DISTRIBUZIONE]
    10

Se vengono identificati più valori, li si stampi tutti in ordine crescente.

# 3) Confronto di righe successive

Conteggiare tutte le coppie di righe consecutive che contengono almeno un numero in comune.
In altri termini, incrementare il conteggio di 1 se almeno un numero compare in due righe che sono collocate consecutivamente nel file.

Detto N i valore del conteggio, stamparlo con il seguente formato:

    [NRIGHE]
    N

# 4) Massimo e minimo

Calcolare il valore massimo e il valore minimo tra tutti i numeri presenti nel file.

Stampare il risultato con il seguente formato:

    [MIN-MAX]
    MIN
    MAX

# 5) Ordinamento

Ordinare le righe in base alla somma dei numeri di ciascuna riga in senso crescente.
In altri termini, collocare prima le righe la cui somma dei numeri è minore.

Stampare il risultato con il seguente formato:

    [ORDINAMENTO]
    1 2 3 4 5 6 7 8 9 10 (50)
    10 20 30 40 50 60 70 80 90 100 (500) 

I numeri interi devono essere stampati separandoli con esattamente uno spazio.
A seguire, separata da un ulteriore spazio e posta tra parentesi, stampare la somma dei valori.

# Esempio

Dato il file di input:

    1 2 3 4 5 6 7 8 9 10
    10 20 30 40 50 60 70 80 90 100 

Lanciando il programma sul file di dati denominato `esempio.txt` con il comando

    ./a.out esempio.txt

L'output da generare, correttamente formattato, è il seguente:

    [CONTRARIO]
    100 90 80 70 60 50 40 30 20 10 
    10 9 8 7 6 5 4 3 2 1 

    [DISTRIBUZIONE]
    10

    [NRIGHE]
    1

    [MIN-MAX]
    1
    100

    [ORDINAMENTO]
    1 2 3 4 5 6 7 8 9 10 (55)
    10 20 30 40 50 60 70 80 90 100 (550)
