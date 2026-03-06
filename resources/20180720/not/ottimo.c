/* NOME COGNOME - MATRICOLA
   Sostituire con i propri dati prima della consegna */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define TOT_COMANDI 7
#define MAXCHAR 10
#define TIMESTAMP_MEZZANOTTE (1000 * 60 * 60 * 24)

static const char *elenco_comandi[TOT_COMANDI] = {"OFF", "LIGHT", "L", "M", "H", "1h", "3h"};

struct comando_t {
    int timestamp;           /* millisecondi dalla mezzanotte */
    char comando[MAXCHAR];
};

struct comando_t *leggi_file(FILE *fin, int *n);
int seleziona_comando(const char *c);
void conta_pressioni(const struct comando_t *comandi, int n, int press[], int first_pos[]);
int indice_massimo_con_tie(const int counts[], const int first_pos[], int n);
long long tempo_luce(const struct comando_t *comandi, int n);
long long tempo_ventola_veloce(const struct comando_t *comandi, int n);
long long tempo_ventola_accesa(const struct comando_t *comandi, int n);
int confronta(const void *a, const void *b);
void stampa_comandi(const struct comando_t *comandi, int n);

int main(int argc, char *argv[]) {
    FILE *fin;
    struct comando_t *comandi;
    int n_com;

    if (argc != 2) {
        printf("Inserire nome file come parametro\n");
        return 1;
    }
    fin = fopen(argv[1], "r");
    if (fin == NULL) {
        printf("Errore in apertura file\n");
        return 1;
    }

    comandi = leggi_file(fin, &n_com);
    if (comandi == NULL) {
        printf("Errore in lettura file\n");
        fclose(fin);
        return 1;
    }

    int pressioni[TOT_COMANDI] = {0};
    int first_pos[TOT_COMANDI];
    for (int i = 0; i < TOT_COMANDI; ++i) first_pos[i] = INT_MAX;

    conta_pressioni(comandi, n_com, pressioni, first_pos);

    printf("[MAX-PRESSIONI]\n");
    int ind_max = indice_massimo_con_tie(pressioni, first_pos, TOT_COMANDI);
    if (ind_max >= 0)
        printf("%s\n", elenco_comandi[ind_max]);
    else
        printf("\n");

    printf("[MEDIA-LUCE]\n");
    long long durata_luce_ms = tempo_luce(comandi, n_com);
    printf("%lld\n", (long long)(durata_luce_ms / 1000)); /* arrotondamento per difetto */

    printf("[TOT-ALTA-VELOCITA]\n");
    long long durata_h_ms = tempo_ventola_veloce(comandi, n_com);
    printf("%lld\n", (long long)(durata_h_ms / 1000));

    printf("[TOT-ACCENSIONE]\n");
    long long durata_tot_ms = tempo_ventola_accesa(comandi, n_com);
    printf("%lld\n", (long long)(durata_tot_ms / 1000));

    printf("[ORDINAMENTO]\n");
    qsort(comandi, n_com, sizeof(*comandi), confronta);
    stampa_comandi(comandi, n_com);

    free(comandi);
    fclose(fin);
    return 0;
}

struct comando_t *leggi_file(FILE *fin, int *n) {
    struct comando_t *comandi = NULL;
    int dim = 8;
    struct comando_t tmp;

    *n = 0;
    comandi = malloc(dim * sizeof(*comandi));
    if (comandi == NULL) return NULL;

    while (fscanf(fin, "%d %9s", &tmp.timestamp, tmp.comando) == 2) {
        if (*n >= dim) {
            dim *= 2;
            struct comando_t *p = realloc(comandi, dim * sizeof(*comandi));
            if (p == NULL) {
                free(comandi);
                return NULL;
            }
            comandi = p;
        }
        comandi[*n] = tmp;
        (*n)++;
    }

    if (*n == 0) {
        free(comandi);
        return malloc(0); /* ritorna array vuoto allocato */
    }

    /* shrink to fit */
    struct comando_t *p = realloc(comandi, (*n) * sizeof(*comandi));
    if (p != NULL) comandi = p;
    return comandi;
}

int seleziona_comando(const char *c) {
    for (int i = 0; i < TOT_COMANDI; ++i) {
        if (strcmp(c, elenco_comandi[i]) == 0) return i;
    }
    return -1;
}

void conta_pressioni(const struct comando_t *comandi, int n, int press[], int first_pos[]) {
    for (int i = 0; i < n; ++i) {
        int idx = seleziona_comando(comandi[i].comando);
        if (idx == -1) continue; /* ignora comandi sconosciuti */
        press[idx]++;
        if (first_pos[idx] == INT_MAX) first_pos[idx] = i; /* posizione nel file */
    }
}

int indice_massimo_con_tie(const int counts[], const int first_pos[], int n) {
    int best = -1;
    int best_count = -1;
    int best_pos = INT_MAX;
    for (int i = 0; i < n; ++i) {
        if (counts[i] > best_count) {
            best_count = counts[i];
            best = i;
            best_pos = first_pos[i];
        } else if (counts[i] == best_count) {
            /* tie: scegliere quello la cui registrazione compare prima nel file */
            int pos_i = first_pos[i];
            if (pos_i < best_pos) {
                best = i;
                best_pos = pos_i;
            }
        }
    }
    return best;
}

/* tempo luce: inizialmente accesa alle 00:00 */
long long tempo_luce(const struct comando_t *comandi, int n) {
    int luce_on = 1; /* a mezzanotte la luce e' accesa */
    int last_change = 0; /* istante dell'ultima accensione */
    long long accum = 0;

    for (int i = 0; i < n; ++i) {
        if (strcmp(comandi[i].comando, "LIGHT") == 0) {
            if (luce_on) {
                /* LIGHT spegne */
                accum += (long long)comandi[i].timestamp - last_change;
                luce_on = 0;
            } else {
                /* LIGHT accende */
                luce_on = 1;
                last_change = comandi[i].timestamp;
            }
        }
    }
    if (luce_on) {
        accum += (long long)TIMESTAMP_MEZZANOTTE - last_change;
    }
    return accum;
}

/* tempo ventola a velocita' H, ignorando timer */
long long tempo_ventola_veloce(const struct comando_t *comandi, int n) {
    int stata_h = 0;
    int last_h = 0;
    long long accum = 0;

    for (int i = 0; i < n; ++i) {
        const char *c = comandi[i].comando;
        if (!stata_h) {
            if (strcmp(c, "H") == 0) {
                stata_h = 1;
                last_h = comandi[i].timestamp;
            }
        } else {
            /* H rimane attiva fino a OFF o L o M */
            if ((strcmp(c, "OFF") == 0) || (strcmp(c, "L") == 0) || (strcmp(c, "M") == 0) || (strcmp(c, "H") == 0)) {
                /* se arriva un nuovo H mentre gia' siamo in H, consideriamo che si sovrascriva il tempo: trattiamo nuovo H come restart */
                if (strcmp(c, "H") == 0) {
                    /* sovrascrive: aggiungi tempo precedente e riapri */
                    accum += (long long)comandi[i].timestamp - last_h;
                    last_h = comandi[i].timestamp;
                    /* stata_h rimane 1 */
                } else {
                    accum += (long long)comandi[i].timestamp - last_h;
                    stata_h = 0;
                }
            }
        }
    }
    if (stata_h) accum += (long long)TIMESTAMP_MEZZANOTTE - last_h;
    return accum;
}

/* tempo totale ventola accesa (L,M,H), ignorando timer */
long long tempo_ventola_accesa(const struct comando_t *comandi, int n) {
    int accesa = 0;
    int last = 0;
    long long accum = 0;

    for (int i = 0; i < n; ++i) {
        const char *c = comandi[i].comando;
        if (!accesa) {
            if ((strcmp(c, "L") == 0) || (strcmp(c, "M") == 0) || (strcmp(c, "H") == 0)) {
                accesa = 1;
                last = comandi[i].timestamp;
            }
        } else {
            if ((strcmp(c, "OFF") == 0)) {
                accum += (long long)comandi[i].timestamp - last;
                accesa = 0;
            } else if ((strcmp(c, "L") == 0) || (strcmp(c, "M") == 0) || (strcmp(c, "H") == 0)) {
                /* cambio velocita' mantiene accesa: nessuna aggiunta, ma aggiorna last per il caso in cui si voglia contare da nuovo istante */
                /* non aggiornare last: il periodo di accensione continua senza interruzione */
            }
        }
    }
    if (accesa) accum += (long long)TIMESTAMP_MEZZANOTTE - last;
    return accum;
}

int confronta(const void *a, const void *b) {
    const struct comando_t *ca = a;
    const struct comando_t *cb = b;
    int comp = strcmp(ca->comando, cb->comando);
    if (comp != 0) return comp;
    return (ca->timestamp - cb->timestamp);
}

void stampa_comandi(const struct comando_t *comandi, int n) {
    for (int i = 0; i < n; ++i) {
        printf("%d %s\n", comandi[i].timestamp, comandi[i].comando);
    }
}
