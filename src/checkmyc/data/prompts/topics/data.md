### Appropriate data structures

**Context**:
The program reads some data from file and calculates different results based on such data. Each result corresponds to a task that have to be solved by the program.
The read file is composed of lines following a strictly structured format, where each element occupies a defined position.

**Objective:**  
Evaluate whether the chosen data structures fit the program’s functional tasks and whether they are used correctly, not merely present ([*1]). Detect inefficient, overcomplicated, or incorrect structure choices.

**Evaluated Conditions:**
1. The program does not define any data structure (goodness: -, criticality: high).
2. The defined data structures do not match the semantics of the file format (goodness: -, criticality: high).
3. The defined data structures are unnecessarely complex but still functional (goodness: -, criticality: medium).
4. The defined data structures are not functional to solve the required tasks (goodness: -, criticality: high). [*0]
5. The defined arrays exhibit disproportionate sizing, resulting in either excessive memory overhead or insufficient capacity. (goodness: =, criticality: neutral).
6. The defined data structures are tightely dimensioned according to the size of data to store (goodness: +, criticality: medium).
7. There is no macro usage (goodness: =, criticality: neutral).
8. Present macros are not utilized to centralize symbolic constants and structural parameters, enhancing code maintainability and readability by replacing magic numbers with meaningful identifiers (goodness: -, criticality: low).
9. Data type of the defined data structures do not match the data they are intended to store (goodness: -, criticality: high).