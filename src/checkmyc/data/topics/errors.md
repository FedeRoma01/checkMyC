### Error detection and handling

**Objective:**  
Evaluate the correctness and completeness of runtime error checks and the program’s ability to handle invalid conditions deterministically.

**Evaluation Criteria:**  
- Verify validation of command-line arguments.
- Verify file opening checks.
- Verify dynamic allocation checks.
- Verify sscanf return-value.
- Verify controlled handling and termination on failures.
- Detect missing checks for critical operations.

**Reference-Solution Valid Elements:**  
In the reference program, the following aspects are present and **must be always considered correct and must not be considered errors with `goodness`: `-`**:

- Command-line arguments are validated (`if (argc != 2)`).
- File opening is checked and reported explicitly if it fails (`if ((f = fopen(...)) == NULL)`).
- Dynamic memory allocations are verified (`if (tmp == NULL)` and `if (dati->linee == NULL)`).
- Malformed lines are skipped but reported with debug messages (`# Linea ... not considered`).
- The program always terminates in a controlled manner (`return 1` on failure).
- The final realloc failure in `leggi_file` is only warned about but not treated as an error.
- All relevant runtime errors (invalid file, bad input, failed allocation) are detected and handled locally.

**To achieve 10/10:**
The program must handle all foreseeable error cases — invalid parameters, missing files, allocation failures, malformed input — without abnormal termination. Every error must be correctly handled preserving internal data consistency and ensuring controlled program exit.






