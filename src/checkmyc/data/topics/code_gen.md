### Code generality

**Objective:**  
Evaluate whether the program adheres to general-purpose, beginner-appropriate coding practices that improve readability, reuse, and usability, checking the correctness of use rather than mere presence.
Italian language usage is allowed and must not be detected.

**Evaluation Criteria:**  
- Verify correct use of CLI arguments for filenames and that no hard-coded filenames are used.
- Verify consistent formatting: indentation, spacing, brace style.
- Verify comments express intent, avoid redundancy, and are placed meaningfully.

**Reference-Solution Valid Elements:**  
In the reference program, the following aspects are present and **must be always considered correct and must not be considered errors with `goodness`: `-`**:

- File opened with the CLI argument (`f = fopen(argv[1], "r")`).
- Comments explain intent and avoid restating obvious code.
- Formatting is uniform throughout the file.

**To achieve 10/10:**  
The program must present clean formatting, meaningful comments, and correct CLI usage resulting in readable, general beginner-level C code suitable for exam evaluation.