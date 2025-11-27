### Code Generality

**Objective:**  
Evaluate whether the program adheres to general-purpose, beginner-appropriate coding practices that improve readability, reuse, and usability.

**Evaluation Criteria:**  
- Verify that the program accepts the input filename through CLI arguments, without using hard-coded filenames.
- Verify consistent formatting: indentation, spacing, brace style.
- Verify comment clarity and placement.

**Reference-Solution Valid Elements:**  
In the reference program, the following aspects are present and **must be always considered correct and must not be considered errors with `goodness`: `-`**:

- File opened with the CLI argument (`f = fopen(argv[1], "r")`).
- Comments explain intent and avoid restating obvious code.
- Formatting is uniform throughout the file.

**To achieve 10/10:**  
The program must present clean formatting, meaningful comments, and correct CLI usage resulting in readable, general beginner-level C code suitable for exam evaluation.