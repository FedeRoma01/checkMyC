### Modularity

**Objective:**  
Evaluate whether the program is decomposed into clear, single-purpose functions and whether the division of responsibilities is correct and coherent, not merely present.

**Evaluation Criteria:**  
- Verify that each major task is assigned to a dedicated function and implemented correctly.
- Verify that functions avoid mixed responsibilities.
- Verify that main coordinates execution without performing heavy computation and that prints results.
- Detect incoherent, oversized or multi-purpose functions.

**Reference-Solution Valid Elements:**  
In the reference program, the following aspects are present and **must be always considered correct and must not be considered errors with `goodness`: `-`**:

- Each exam requirement is implemented in a separate function:
  `stampa_contrario`, `max_distribuzione`, `righe`, `stampa_min_max`, `stampa_somme`.
- The function `leggi_file` is solely responsible for reading and building the data structure, clearly separating input handling from computation.
- The `main` function coordinates execution without performing direct processing.
- Functions communicate exclusively through parameters (`struct file *dati`), without relying on global variables.
- The `leggi_file` function handles error messages and memory freeing internally and returns an error code, without propagating detailed error information.

**To achieve a full score (10/10):**  
The program must consist of cohesive functions with descriptive names and distinct responsibilities. Each part of the problem must be resolved by one well-defined function.