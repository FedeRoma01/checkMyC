### Appropriate data structures

#### **Objective:**  
Evaluate whether the chosen data structures fit the program’s functional tasks and whether they are correctly defined, not merely present. Detect inefficient, overcomplicated, or incorrect structure choices.

#### **Context**:   
The program reads some data from file and calculates different results based on such data. Each result corresponds to a task that have to be solved by the program.
The read file is composed of lines following a strictly structured format, where each element occupies a defined position.  
Consider the following definitions to correctly interpret the `Evaluated Conditions`:
- semantics of the file format: refers to the logical meaning and behavioral expectations of data fields, beyond their basic syntax or data types. It defines how raw input maps to specific functional states and constraints within the program's logic.
- disproportionate sizing: it is disproportionate with respect to the possible file data presented in `Context Section`. 

#### **Evaluated Conditions:**
1. The program does not define any data structure (goodness: -, criticality: high).
2. The defined data structures do not conceptually represents the semantics of the file format (goodness: -, criticality: medium).
3. The defined data structures, as currently implemented, are unnecessarely complex but still functional (goodness: -, criticality: medium).
4. The defined data structures, as currently implemented, are not functional to solve the required tasks (goodness: -, criticality: medium).
5. The defined arrays exhibit disproportionate sizing, resulting in either excessive memory overhead or insufficient capacity (goodness: =, criticality: neutral).
6. The defined data structures are tightely dimensioned according to the size of data to store (goodness: +, criticality: medium).
7. There is no macro usage (goodness: =, criticality: neutral).
8. Defined macros are not utilized anywhere to centralize symbolic constants and structural parameters (goodness: -, criticality: low).