/* Soluzione del tema d'esame del 2022-07-28 */

#include <stdio.h>
#include <stdlib.h>

// numero di valori numerici in ciascuna riga
#define NNUM (10)

// una struttura per memorizzare i 10 valori delle singole righe
struct linea {
    int numeri[NNUM];   // valori numerici
    int somma;          // somma
};

// contiene tutte le righe del file
struct file {
    int n;                  // numero di righe lette
    struct linea *linee;    // vettore di linee
};

/* Lettura del file; la struttura dati contiene tutte le informazioni relative al file,
 * incluso il numero di righe lette; è quindi sufficiente per restituire tutte le
 * informazioni necessarie alla funzione chiamante. */
void leggi_file(FILE *f, struct file *dati)
{
    int dimc = 1, s, i;
    struct linea *linea, *tmp;
    char buf[2048];
    
    dati->n = 0;
    dati->linee = malloc(dimc * sizeof(*(dati->linee)));
    if (dati->linee == NULL) return;

    while (fgets(buf, sizeof(buf), f)) {
        // assegno l'indirizzo dell'elemento di interesse ad un puntatore,
        // per evitare di ripetere l'indirizzamento per ogni valore da passare alla sscanf
        linea = dati->linee + dati->n;
        sscanf(buf, "%d %d %d %d %d %d %d %d %d %d",
                linea->numeri + 0,
                linea->numeri + 1,
                linea->numeri + 2,
                linea->numeri + 3,
                linea->numeri + 4,
                linea->numeri + 5,
                linea->numeri + 6,
                linea->numeri + 7,
                linea->numeri + 8,
                linea->numeri + 9);
        // calcolo la somma dei valori nella riga
        s = 0;
        for (i = 0; i < NNUM; ++i) {
            s += linea->numeri[i];
        }
        linea->somma = s;

        // indice della riga successiva
        dati->n += 1;

        // ridimensionamento del vettore di righe
        if (dati->n >= dimc) {
            dimc *= 2;
            tmp = realloc(dati->linee, dimc * sizeof(*(dati->linee)));
            if (tmp == NULL) {
                free(dati->linee);
                return;
            }
            dati->linee = tmp;
        }
    }
    // ridimensionamento del vettore per contenere solo i dati effettivamente letti
    dati->linee = realloc(dati->linee, dati->n * sizeof(*(dati->linee)));
}

/* Funzione che risolve il punto 1 */
void stampa_contrario(struct file *dati)
{
    int i, j;
    // ciclo che itera sulle righe, dall'ultima alla prima
    for (i = dati->n - 1; i >= 0; --i) {
        // ciclo che itera sugli elementi, dall'ultimo al primo
        for (j = NNUM - 1; j >= 0; --j) {
            printf("%d ", dati->linee[i].numeri[j]);
        }
        puts("");   // andata a capo a fine di ciascuna riga stampata
    }
}

/* Funzione che risolve il punto 2 */
void max_distribuzione(struct file *dati)
{
    int i, j, num;
    int istogramma[201] = {0};   // vettore di 201 valori per conteggiare i numeri da -100 a +100 compresi
    int max;

    for (i = 0; i < dati->n; ++i) {
       for (j = 0; j < NNUM; ++j) {
           // assegna il numero ad una variabile per non portarsi dietro l'indicizzazione
           num = dati->linee[i].numeri[j];
           // verifica che il numero da conteggiare sia contenuto nell'intervallo richiesto
           if ((num >= -100) && (num <= 100)) {
               // incrementa il conteggio
               // il +100 serve per fare in modo che l'elemento di indice 0
               // conteggi il valore -100, e così via
               istogramma[num + 100]++;
           }
       }
    }
    // trova il massimo all'interno dell'istogramma
    // il massimo viene inizialmente impostato pari al primo valore dell'array
    max = istogramma[0];
    for (i = 0; i < 201; ++i) {
        if (istogramma[i] > max)
            max = istogramma[i];
    }
    // stampa gli indici dell'istogramma il cui conteggio corrisponde al massimo
    for (i = 0; i < 201; ++i) {
        if (istogramma[i] == max)
            printf("%d\n", i - 100);
    }
}

/* Funzione che risolve il punto 3 */
int righe(struct file *dati)
{
    int i, j1, j2;
    int trovato, count = 0;

    // un ciclo per ogni riga, tranne l'ultima che non ha una riga successiva
    for (i = 0; i < dati->n - 1; ++i) {
        // per il momento non ho ancora trovato un valore della riga successiva
        // che sia uguale ad uno della riga corrente (quindi trovato <- falso)
        trovato = 0;
        // un ciclo per ogni valore della riga corrente
        for (j1 = 0; j1 < NNUM; ++j1) {
            // un ciclo per ogni valore della riga successiva
            for (j2 = 0; j2 < NNUM; ++j2) {
                // verifica se l'elemento j1-esimo della riga corrente (i-esima)
                // è uguale all'elemento j2-esimo della riga successiva ((i+1)-esimo)
                if (dati->linee[i].numeri[j1] == dati->linee[i + 1].numeri[j2])
                    // se sì, ho trovato un elemento in comune e imposto trovato a 1
                    trovato = 1;
            }
       }
       // dal momento che "trovato" può valere solo o 0 o 1, lo uso
       // direttamente per incrementare il conteggio
       count += trovato;
    }
    return count;
}

/* Funzione che risolve il punto 4 */
void stampa_min_max(struct file *dati)
{
    int i, j, num;
    // il massimo e il minimo sono inizialmente impostati pari al primo numero della prima riga
    int min = dati->linee[0].numeri[0], max = min;

    // itera su tutte le righe
    for (i = 0; i < dati->n; ++i) {
        // itera su tutti i valori della riga i-esima
        for (j = 0; j < NNUM; ++j) {
            // assegna il valore alla variabile per evitare di ripetere gli indirizzamenti
            num = dati->linee[i].numeri[j];
            // confronti per stabilire massimo e minimo
            if (num > max) max = num;
            if (num < min) min = num;
        }
    }
    printf("%d\n%d\n", min, max);
}

/* Funzione di stampa per il punto 5 */
void stampa_somme(struct file *dati)
{
    int i, j;

    for (i = 0; i < dati->n; ++i) {
        // stampa una riga
        for (j = 0; j < NNUM; ++j) {
            printf("%d ", dati->linee[i].numeri[j]);
        }
        // aggiunge il valore della sommma col formato richiesto
        printf("(%d)\n", dati->linee[i].somma);
    }
}

/* Funzione di confronto per il punto 5 */
int cmp(const void *p1, const void *p2)
{
    const struct linea *a = p1, *b = p2;
    // il confronto delle singole righe viene fatto in base alla somma
    // dei valori della riga, come richiesto dal quesito
    if (a->somma > b->somma) return 1;
    if (a->somma < b->somma) return -1;
    return 0;
}

int main(int argc, char *argv[])
{
    FILE *f;
    struct file dati;    // è una struttura, non un puntatore; così viene allocata memoria per salvare i dati
    
    // controllo del numero di parametri sulla linea di comando
    if (argc != 2) {
        printf("Uso: ./a.out nomefile\n");
        return 1;
    }
    
    // apertura del file in lettura
    if ((f = fopen(argv[1], "r")) == NULL) {
        printf("Errore nell'apertura del file %s\n", argv[1]);
        return 1;
    }
    // lettura del file
    leggi_file(f, &dati);
    fclose(f);

    // ogni quesito viene indirizzato all'interno di una funzione dedicata
    puts("[CONTRARIO]");
    stampa_contrario(&dati);
    puts("");
    puts("[DISTRIBUZIONE]");
    max_distribuzione(&dati);
    puts("");
    puts("[NRIGHE]");
    printf("%d\n", righe(&dati));
    puts("[MIN-MAX]");
    stampa_min_max(&dati);
    puts("");
    puts("[ORDINAMENTO]");
    qsort(dati.linee, dati.n, sizeof(*(dati.linee)), cmp);
    stampa_somme(&dati);
    
    return 0;
}
