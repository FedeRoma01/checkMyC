### Modularity

**Context**:  
The program reads some data from file and calculates different results based on such data. Each result corresponds to a **task** that have to be solved by the program. Each task result is printed after specifying the related task with the format `[TASK-NAME]`.

**Objective:**  
Evaluate whether the program is decomposed into clear functions dedicated to each single task, where one of the tasks is the reading of file.

**Evaluated Conditions:**  
1. We do not consider commented functions (goodness: =, criticality: neutral).
2. Functions defined but not called are irrelevant (goodness: =, criticality: neutral).
3. To evaluate the modularity we do not consider the quality of the code that solves a single task within a dedicated function (goodness: =, criticality: neutral).
4. A function addresses more than one task (goodness: -, criticality: medium).
5. All, or almost all the code, is contained in the main function (goodness: -, criticality: high).
6. Functions communicate through global variables instead of parameters (goodness: -, criticality: medium).
7. Section names and results are printed in the main function (goodness: +, criticality: medium).
8. Some tasks are not addressed in the evaluated program (goodness: =, criticality: neutral); To evaluate the modularity we do not require to evaluate the completeness of the evaluated program in terms of which tasks have been solved.
9. The file is opened in the main function (goodness: =, criticality: neutral).
10. The function that contains the file reading logic is solely responsible for reading, building and filling the data structure, clearly separating input handling from computation (goodness: +, criticality: high).
11. The main function coordinates execution, calling the functions that address each task, without performing direct processing for the solution of a task (goodness: +, criticality: high).
12. Functions communicate exclusively through parameters, without relying on global variables (goodness: +, criticality: high).
13. The file reading function handles error messages and memory freeing internally and returns an error code, without propagating detailed error information (goodness: +, criticality: low).
14. Section names and results are printed within the function that calculates the result of the task (goodness: =, criticality: neutral).