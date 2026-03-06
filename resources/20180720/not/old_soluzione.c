#include<stdio.h>
#include<stdlib.h>
#include<string.h>

#define TOT_COMANDI 7
#define MAXCHAR 10
#define TIMESTAMP_MEZZANOTTE (1000 * 60 * 60 * 24)

char *elenco_comandi[] = {"OFF", "LIGHT", "L", "M", "H", "1h", "3h"};

struct comando_t {
	int timestamp;
	char comando[MAXCHAR];
};

struct comando_t * leggi_file(FILE *fin, int *n);
int seleziona_comando (char c[]);  //dato un comando ritorna il numero corrispondente
void conta_pressioni(struct comando_t *comandi, int n, int press[]);
int massimo(int v[], int n);   //ritorna l'indice del valore massimo contenuto tra quelli contenuti nel vettore
int conta_accensioni(struct comando_t *comandi, int n_com);
int tempo_ventola_veloce(struct comando_t *comandi, int n);
int tempo_ventola_accesa(struct comando_t *comandi, int n);
int confronta(const void *a, const void *b);  //funzione di confronto da usare in qsort
void stampa_comandi(struct comando_t *comandi, int n);

int main (int argc, char *argv[]) {
	FILE *fin;
	struct comando_t *comandi;
	int n_com, n_pressioni[TOT_COMANDI]={0}, accensioni;

	if (argc != 2) {
		printf("Inserire nome file come parametro\n");		
		return 1;
	}
	if((fin = fopen (argv[1], "r"))==NULL) {
		printf("Errore in apertura file\n");
		return 1;
	}
	comandi = leggi_file(fin, &n_com);
	if(comandi == NULL) {
		printf("Errore in lettura file\n");
		return 1;
	}
	printf("[MAX-PRESSIONI]\n");
	conta_pressioni(comandi, n_com, n_pressioni);
	printf("%s\n", elenco_comandi[(massimo(n_pressioni, TOT_COMANDI))]);
	printf("[MEDIA-LUCE]\n");
	accensioni = conta_accensioni(comandi, n_com);
	printf("%d\n", accensioni/1000);
	printf("[TOT-ALTA-VELOCITA]\n%d\n", tempo_ventola_veloce(comandi, n_com)/1000);
	printf("[TOT-ACCENSIONE]\n%d\n", tempo_ventola_accesa(comandi, n_com)/1000);
	printf("[ORDINAMENTO]\n");
	qsort(comandi, n_com, sizeof(*comandi), confronta);
	stampa_comandi(comandi, n_com);
	
	free(comandi);
	fclose(fin);
	return 0;
}

struct comando_t * leggi_file(FILE *fin, int *n) {
	struct comando_t *comandi, tmp;
	char buf[100];
	int dim=8;
	
	(*n)=0;
	comandi = malloc(dim * sizeof(*comandi));
	if (comandi==NULL)
		return NULL;
	while((fgets(buf, sizeof(buf), fin))!=NULL) {
		sscanf(buf, "%d %s", &tmp.timestamp, tmp.comando);
		comandi[(*n)] = tmp;
		(*n)++;
		if ((*n)>=dim) {
			dim *= 2;
			comandi = realloc(comandi, dim * sizeof(*comandi));
			if (comandi==NULL)
				return NULL;
		}
	}
	comandi = realloc(comandi, (*n) * sizeof(*comandi));
	return comandi;
}

int seleziona_comando (char c[]) {
	int i;
	for(i=0; i<TOT_COMANDI; i++) {
		if (strcmp(c, elenco_comandi[i])==0) {
			return i;
		}
	}
	return -1;
}

void conta_pressioni(struct comando_t *comandi, int n, int press[]) {
	int i;
	for(i=0; i<n; i++) {
		press[(seleziona_comando(comandi[i].comando))]++;
	}
}

int massimo(int v[], int n) {
	int i, max_val=0, ind_max;
	for(i=0; i<n; i++) {
		if(v[i]>max_val) {
			max_val = v[i];
			ind_max = i;
		}
	}
	return ind_max;
}

int conta_accensioni(struct comando_t *comandi, int n_com) {
	int i, accensioni=0, ultima_accensione=0;  
	
	for(i=0; i<n_com; i++) {
		if(strcmp(comandi[i].comando, "LIGHT")==0) {
			if(ultima_accensione==-1) {   /*ultima_accensione vale -1 quando la luce e' stata spenta con il precedente comando LIGHT*/
				ultima_accensione = comandi[i].timestamp;
				
			} else {
				accensioni += (comandi[i].timestamp - ultima_accensione);
				ultima_accensione = -1;
			}
		}
	}
	if(ultima_accensione!=-1) {
		accensioni += TIMESTAMP_MEZZANOTTE - ultima_accensione;
	}

	return accensioni;
}

int tempo_ventola_veloce(struct comando_t *comandi, int n) {
	int tempo=0, i, accesa=0, time_acc;  //accesa==1 se la ventola e' accesa a velocita' alta
	for(i=0; i<n; i++) {
		if(accesa==0) {
			if(strcmp(comandi[i].comando, "H")==0) {
				accesa=1;
				time_acc = comandi[i].timestamp;
			}
		} else {
			if((strcmp(comandi[i].comando, "M")==0) || (strcmp(comandi[i].comando, "L")==0) || (strcmp(comandi[i].comando, "OFF")==0)) {
				accesa = 0;
				tempo += (comandi[i].timestamp - time_acc);
			}
		}
	}
	if(accesa==1)
		tempo += TIMESTAMP_MEZZANOTTE - time_acc;
	
	return tempo;	
}

int tempo_ventola_accesa(struct comando_t *comandi, int n) {
	int tempo=0, i, accesa=0, time_acc;  //accesa==1 se la ventola e' accesa
	for(i=0; i<n; i++) {
		if(accesa==0) {
			if((strcmp(comandi[i].comando, "H")==0) || (strcmp(comandi[i].comando, "M")==0) || (strcmp(comandi[i].comando, "L")==0)) {
				accesa=1;
				time_acc = comandi[i].timestamp;
			}
		} else {
			if((strcmp(comandi[i].comando, "OFF")==0)) {
				accesa = 0;
				tempo += (comandi[i].timestamp - time_acc);
			}
		}
	}
	if(accesa==1)
		tempo += TIMESTAMP_MEZZANOTTE - time_acc;
	
	return tempo;	
}

int confronta(const void *a, const void *b) {
	const struct comando_t *ca=a, *cb=b;
	int comp;
	
	comp=strcmp(ca->comando, cb->comando);
	if (comp!=0)
		return comp;
	return ((ca->timestamp)-(cb->timestamp));

}

void stampa_comandi(struct comando_t *comandi, int n) {
	int i;
	for(i=0; i<n; i++)
		printf("%d %s\n", comandi[i].timestamp, comandi[i].comando);
}

