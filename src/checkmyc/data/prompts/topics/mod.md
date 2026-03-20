### Modularity

#### **Objective:**  
Evaluate whether the program is decomposed into clear functions dedicated to each single task, where one of the tasks is the reading of file.   

#### **Context**:  
The program reads some data from file and calculates different results based on such data. Each result corresponds to a **task** that have to be solved by the program. Each task result is printed after printing the related task tag with the format `[TASK-TAG]`. Printings can be done both within the main function and the tasks related functions.   
Do consider the following aspects, they can trigger any of the `Evaluated Conditions`: 
- commented code.   

Do **not** consider the following aspects, they must **not** trigger any of the `Evaluated Conditions`:   
  - quality of the code that solves a single task within a dedicated function.
  - functional correctness of the defined functions.   

Consider the following definitions to correctly interpret the `Evaluated Conditions`:
- Coordination: program setup (e.g., fopen), calling sub-functions, and printing the final output returned by those functions.
- Direct Processing: any logic that solves a core task requirement, excluding task tag and result printings and task-solving functions calls. It includes data structure traversal (loops), business logic, or parsing file content.
- Reading logic: reading, building and filling the data structure in order to perform the tasks.

#### **Evaluated Conditions:**  
1. A function addresses more than one task (goodness: -, criticality: medium).
2. All, or almost all the code that performs direct processing for the solution of a task, is contained in the main function (goodness: -, criticality: high).
3. Functions communicate through global variables instead of parameters (goodness: -, criticality: low).
4. Task tags and/or results are printed in the main function (goodness: +, criticality: medium).
5. Some tasks are not addressed in the evaluated program (goodness: =, criticality: neutral).
6. The file is opened in the main function (goodness: =, criticality: neutral).
7. The function that contains the file reading logic is solely responsible for reading, building and filling the data structure, clearly separating input handling from computation (goodness: +, criticality: medium).
8. The main function coordinates functions execution, calling the functions that address each task, without performing direct processing for the solution of a task (goodness: +, criticality: high).
9. Functions communicate exclusively through parameters, without relying on global variables (goodness: +, criticality: medium).
10. The file reading function handles error messages and memory freeing internally and returns an error code, without propagating detailed error information (goodness: +, criticality: low).
11. Task tags and/or results are printed within the function that calculates the result of the task (goodness: =, criticality: neutral).