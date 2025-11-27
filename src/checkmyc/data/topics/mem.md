### Correct use of dynamic memory

**Objective:**  
Evaluate the presence and the correctness and safety of all dynamic memory operations across allocation, use, reallocation, and deallocation.

**Evaluation Criteria:**
- Verify correct use of allocated memory without out-of-bounds access.
- Verify that all allocated memory is properly freed.
- Detect invalid memory reuse after failed allocation.
- Detect incorrect or unsafe resizing strategies.

**Reference-Solution Valid Elements:**  
In the reference program, the following aspects are present and **must be always considered correct and must not be considered errors with `goodness`: `-`**:

- The array of lines `dati->linee` is dynamically allocated with `malloc` and expanded using `realloc` as new data are read.
- Every allocation is checked for success (`if (tmp == NULL)` and `if (dati->linee == NULL)`), with memory safely freed upon failure (`free(dati->linee)`).
- The leggi_file function returns void and does not signal allocation failures to the caller.
- The reallocation strategy doubles the size of the line vector whenever the next insertion would exceed the currently allocated capacity.
- All allocated memory is correctly released at the end (`free(dati.linee)` in `main`).
- No redundant allocations or double frees are present.
- The final realloc occurs after all data are successfully read; failure at that point would not corrupt data or cause leaks.

**To achieve 10/10:**  
The code must demonstrate a complete and safe memory lifecycle — *allocation → use → possible reallocation → deallocation* — with systematic error checking, no memory leaks, and structural consistency between allocated data and program logic.
