### Error handling

#### **Objective:**  
Evaluate the correctness and completeness of runtime error checks and the program’s ability to handle invalid conditions deterministically, verifying not only whether checks exist but whether they are placed and used correctly. Errors handling must ensure the program flow to actually stop or react to the errors.

#### **Context**:   
The program processes a text file composed of lines following a strictly structured pattern, where each element occupies a defined position.   
Consider the following definitions to correctly interpret the `Evaluated Conditions`:
- Dynamic memory allocations: refer to the family of standard library functions used to manage memory on the heap, specifically malloc, realloc, calloc, and aligned_alloc.
- Dynamic memory reallocation: exclusively refers to realloc function.

#### **Evaluated Conditions:**
1. All relevant critical runtime errors are detected and handled locally (goodness: +, criticality: high).
2. The program always terminates in a controlled manner in case of critical runtime errors thanks to critical error handling throughout the entire program (goodness: +, criticality: high).
3. There are unreachable error checks (goodness: -, criticality: low).
4. The error is suitably checked but no effective measure is taken to deal with the error condition, leading to a program crash (goodness: -, criticality: medium).
5. Error handling contains explanatory prints (goodness: +, criticality: low).
6. The reading file function can return NULL pointer to the caller due to not checking and handling allocation failures (goodness: -, criticality: low).
7. The number of command-line arguments is not checked (goodness: -, criticality: medium).
8. Command-line arguments number is checked and handled by terminating the program (goodness: +, criticality: medium).
9. File opening failure is not checked (goodness: -, criticality: medium).
10. File opening failure is checked and handled by terminating the program (goodness: +, criticality: medium).
11. Empty file case is not handled (goodness: =, criticality: neutral).
12. Empty file case is handled (goodness: =, criticality: neutral).
13. Dynamic memory allocations are checked for failure and correctly handled by terminating the program (goodness: +, criticality: medium).
14. Dynamic memory allocations are checked for failure and handled by returning NULL (goodness: =, criticality: neutral).
15. Dynamic memory allocations are not checked for failure, risking unsafe use (goodness: -, criticality: medium).
16. Dynamic memory reallocation failure inside the reading file loop is checked and handled by exiting the loop; the program continues with data dynamically allocated until that point (goodness: +, criticality: medium).
17. Dynamic memory reallocation failure at the end of the reading file loop is checked but not handled by terminating the program (goodness: +, criticality: low).
18. sscanf return-value is not checked (goodness: -, criticality: low).
19. sscanf return-value is checked and handled (goodness: +, criticality: low).
20. Malformed lines of the reading file are skipped but reported with debug messages (goodness: =, criticality: neutral).
21. There is no error checking neither error handling throughtout the entire program (goodness: -, criticality: high).
