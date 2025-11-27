### Appropriate data structures

**Objective:**  
Evaluate whether the chosen data structures fit the program’s functional goals. Detect inefficient, overcomplicated, or incorrect structure choices.

**Evaluation Criteria:**
- Verify that structures match the semantics of the file format.
- Verify that stored fields minimize redundancy.
- Detect unnecessary complexity in struct design.
- Detect misuse of arrays or structs that harms clarity or performance.

**Reference-Solution Valid Elements:**  
In the reference program, the following aspects are present and **must be always considered correct and must not be considered errors with `goodness`: `-`**:

- The structure `struct linea` encapsulates the ten integers of a line, with an array, along with their sum, creating a clear, self-contained data unit.
- The structure `struct file` organizes the total number of lines and their dynamic array, providing a complete in-memory representation of the file.
- Using an array of structures (`struct linea *linee`) enables direct sorting with `qsort` and efficient sequential access.
- The histogram in `max_distribuzione` is implemented as a static array of 201 integers, an optimal solution for the range [-100, 100].

**To achieve 10/10:**  
Data structures must be designed to match the semantics of the problem, minimizing redundancy and maximizing clarity. They should simplify each required operation, not complicate it. Structures should be logically cohesive, efficient, and directly aligned with the intended processing tasks.
