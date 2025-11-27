### Modularity

**Objective:**  
Evaluate whether the program is decomposed into clear, single-purpose functions and the separation of logic within the program..

**Evaluation Criteria:**  
- Verify that each major task is assigned to a dedicated function.
- Verify that functions avoid mixed responsibilities.
- Verify that main coordinates execution without performing heavy computation and prints results.
- Detect oversized or multi-purpose functions.

**Reference-Solution Valid Elements:**  
In the reference program, the following aspects are present and **must be always considered correct and must not be considered errors with `goodness`: `-`**:

- Each exam requirement is implemented in a separate function:
  `stampa_contrario`, `max_distribuzione`, `righe`, `stampa_min_max`, `stampa_somme`.
- The function `leggi_file` is solely responsible for reading and building the data structure, clearly separating input handling from computation.
- The `main` function coordinates execution without performing direct processing.
- Functions communicate exclusively through parameters (`struct file *dati`), without relying on global variables.
- The `leggi_file` function handles error messages and memory freeing internally and returns an error code, without propagating detailed error information.

**To achieve a full score (10/10):**  
The program must consist of cohesive functions with descriptive names, clear interfaces, and distinct responsibilities. Each part of the problem must be encapsulated in a reusable, self-contained module that can be tested independently.
