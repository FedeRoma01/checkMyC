#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NCOMANDI 7
#define MAXC 8
#define GIORNO_MS (24 * 60 * 60 * 1000)

/* vettore dei comandi validi, usato per mapping e stampa */
static const char *comandi_validi[NCOMANDI] = {
    "OFF", "LIGHT", "L", "M", "H", "1h", "3h"
};

/* struttura che rappresenta una singola misurazione del file */
struct riga {
    int timestamp;        /* millisecondi dalla mezzanotte */
    char comando[MAXC];   /* comando associato al pulsante premuto */
};

/* struttura che contiene tutte le misurazioni lette */
struct file {
    int n;               /* numero totale di righe lette */
    struct riga *v;      /* vettore dinamico delle misurazioni */
};

/* PROTOTIPI */
int leggi_file(FILE *f, struct file *d);
int indice_comando(const char *c);
void conta_pressioni(struct file *d, int press[]);
int indice_massimo(const int v[], int n);
int durata_luce(struct file *d);
int durata_veloce(struct file *d);
int durata_ventola(struct file *d);
int cmp(const void *a, const void *b);
void stampa(struct file *d);

int main(int argc, char *argv[])
{
    struct file d;
    FILE *f;
    int press[NCOMANDI] = {0};

    /* controllo numero parametri */
    if (argc != 2) {
        printf("Uso: ./a.out nomefile\n");
        return 1;
    }

    /* apertura del file di input */
    if ((f = fopen(argv[1], "r")) == NULL) {
        printf("Errore nell'apertura del file %s\n", argv[1]);
        return 1;
    }

    /* lettura e costruzione della struttura dati */
    if (leggi_file(f, &d) != 0) {
        fclose(f);
        return 1;
    }
    fclose(f);

    /* caso di file vuoto */
    if (d.n == 0) {
        puts("Nessuna riga valida trovata nel file. Uscita.");
        free(d.v);
        return 0;
    }

    /* 1 - pulsante più premuto */
    puts("[MAX-PRESSIONI]");
    conta_pressioni(&d, press);
    printf("%s\n", comandi_validi[indice_massimo(press, NCOMANDI)]);

    /* 2 - durata media di accensione della luce */
    puts("[MEDIA-LUCE]");
    printf("%d\n", durata_luce(&d) / 1000);

    /* 3 - tempo di rotazione a velocità alta */
    puts("[TOT-ALTA-VELOCITA]");
    printf("%d\n", durata_veloce(&d) / 1000);

    /* 4 - tempo totale di accensione della ventola */
    puts("[TOT-ACCENSIONE]");
    printf("%d\n", durata_ventola(&d) / 1000);

    /* 5 - ordinamento secondo specifica */
    puts("[ORDINAMENTO]");
    qsort(d.v, d.n, sizeof(*(d.v)), cmp);
    stampa(&d);

    free(d.v);
    return 0;
}

/*
 * Lettura del file e costruzione del vettore dinamico.
 * Gestisce riallocazioni progressive e ignora righe non valide.
 */
int leggi_file(FILE *f, struct file *d)
{
    char buf[128];
    int dim = 4;
    struct riga *tmp;

    d->n = 0;
    d->v = malloc(dim * sizeof(*(d->v)));
    if (d->v == NULL) return -1;

    while (fgets(buf, sizeof(buf), f)) {

        struct riga r;

        /* parsing essenziale: timestamp + comando */
        if (sscanf(buf, "%d %7s", &r.timestamp, r.comando) != 2) {
            printf("# Avviso: riga non valida, ignorata\n");
            continue;
        }

        d->v[d->n] = r;
        d->n++;

        /* raddoppio della capacità quando necessario */
        if (d->n >= dim) {
            dim *= 2;
            tmp = realloc(d->v, dim * sizeof(*(d->v)));
            if (tmp == NULL) {
                printf("Errore di riallocazione della memoria\n");
                free(d->v);
                return -1;
            }
            d->v = tmp;
        }
    }

    /* ottimizzazione finale dell’allocazione */
    if (d->n > 0) {
        tmp = realloc(d->v, d->n * sizeof(*(d->v)));
        if (tmp != NULL) d->v = tmp;
        else printf("# Avviso: realloc finale fallita\n");
    } else {
        free(d->v);
    }

    return 0;
}

/* ritorna l'indice del comando nel vettore comandi_validi */
int indice_comando(const char *c)
{
    for (int i = 0; i < NCOMANDI; i++)
        if (strcmp(c, comandi_validi[i]) == 0)
            return i;
    return -1;
}

/* conteggio semplice della frequenza di ogni comando */
void conta_pressioni(struct file *d, int press[])
{
    for (int i = 0; i < d->n; i++) {
        int k = indice_comando(d->v[i].comando);
        if (k >= 0) press[k]++;
    }
}

/* ritorna l’indice del massimo valore nel vettore v */
int indice_massimo(const int v[], int n)
{
    int max = v[0], idx = 0;
    for (int i = 1; i < n; i++)
        if (v[i] > max) {
            max = v[i];
            idx = i;
        }
    return idx;
}

/*
 * Calcolo del tempo totale in cui la luce è accesa.
 * La luce inizialmente è ON.
 */
int durata_luce(struct file *d)
{
    int acc = 0;
    int stato = 1; /* 1 = acceso, 0 = spento */
    int t0 = 0;

    for (int i = 0; i < d->n; i++) {

        /* evento LIGHT: toggle */
        if (strcmp(d->v[i].comando, "LIGHT") == 0) {

            if (stato == 1) { /* spegnimento */
                acc += d->v[i].timestamp - t0;
                stato = 0;

            } else { /* accensione */
                stato = 1;
                t0 = d->v[i].timestamp;
            }
        }
    }

    /* se la luce era ancora accesa a fine giornata */
    if (stato == 1)
        acc += GIORNO_MS - t0;

    return acc;
}

/*
 * Tempo totale di funzionamento a velocità alta.
 * Timer ignorati come da testo.
 */
int durata_veloce(struct file *d)
{
    int acc = 0;
    int on = 0;
    int t0 = 0;

    for (int i = 0; i < d->n; i++) {
        const char *c = d->v[i].comando;

        if (on == 0) {
            if (strcmp(c, "H") == 0) {
                on = 1;
                t0 = d->v[i].timestamp;
            }
        } else {
            if (strcmp(c, "M") == 0 || strcmp(c, "L") == 0 || strcmp(c, "OFF") == 0) {
                acc += d->v[i].timestamp - t0;
                on = 0;
            }
        }
    }

    if (on == 1)
        acc += GIORNO_MS - t0;

    return acc;
}

/*
 * Tempo totale di accensione della ventola (qualsiasi velocità).
 */
int durata_ventola(struct file *d)
{
    int acc = 0;
    int on = 0;
    int t0 = 0;

    for (int i = 0; i < d->n; i++) {
        const char *c = d->v[i].comando;

        if (on == 0) {
            if (strcmp(c, "H") == 0 || strcmp(c, "M") == 0 || strcmp(c, "L") == 0) {
                on = 1;
                t0 = d->v[i].timestamp;
            }
        } else {
            if (strcmp(c, "OFF") == 0) {
                acc += d->v[i].timestamp - t0;
                on = 0;
            }
        }
    }

    if (on == 1)
        acc += GIORNO_MS - t0;

    return acc;
}

/*
 * Confronto per l’ordinamento:
 * 1. ordine alfabetico sul comando
 * 2. a parità, timestamp crescente
 */
int cmp(const void *a, const void *b)
{
    const struct riga *x = a;
    const struct riga *y = b;

    int c = strcmp(x->comando, y->comando);
    if (c != 0) return c;

    return (x->timestamp - y->timestamp);
}

/* stampa del vettore ordinato */
void stampa(struct file *d)
{
    for (int i = 0; i < d->n; i++)
        printf("%d %s\n", d->v[i].timestamp, d->v[i].comando);
}
