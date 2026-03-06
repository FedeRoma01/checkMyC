### Correct use of dynamic memory

**Objective:**  
Evaluate the presence of dynamic memory operations across allocation, use, reallocation, and deallocation. The logic that checks the correctness of the allocation is not to be evaluated since the error checking is evaluated by a different topic.

**Evaluated Conditions:**
1. Allocated memory does not match the required type size, causing under-allocation or incorrect casting (goodness: -, criticality: high).
2. Dinamic allocated memory without out-of-bounds access (goodness: +, criticality: high).
3. Allocated buffers are freed more than once or with wrong pointer (goodness: -, criticality: high).
4. There are cases of memory reuse after failed allocation (goodness: -, criticality: high).
5. There are incorrect or unsafe resizing strategies (goodness: -, criticality: high).
6. The array used to store data read from file is dynamically allocated with malloc and expanded using realloc as new data are read (goodness: +, criticality: medium).
7. The reallocation strategy suitably increases the size of the dynamic reallocated vector whenever the next insertion would exceed the currently allocated capacity (goodness: +, criticality: high).
8. The reallocation strategy increases the size of the dynamic reallocated vector by one or another value that leads to an excessive amount of reallocations (goodness: -, criticality: low).
9. The vector that stores the data read from file is dynamic allocated with malloc but its size is not adapted in case of exceeding the capacity of the allocated vector; i.e. no realloc is used to increase the size of the vector (goodness: -, criticality: high).
10. Memory space is wasted due to an excessive size of the dynamic reallocated vector, whose size is not suitably reduced at the end of the reading loop (goodness: -, criticality: low).
11. Memory space is saved thanks to a suitable reduction of the size of the dynamic reallocated vector using realloc at the end of the reading loop (goodness: +, criticality: medium).  
12. All allocated memory is correctly released when it is no more needed using free (goodness: +, criticality: low). 
13. All allocated memory is never relesead with free when it is no more needed (goodness: -, criticality: low).
14. All allocated memory is released before terminating the program using free (goodness: +, criticality: low).
15. Dynamic memory reallocations use a temporary pointer in order to avoid losing previously dynamic allocated memory valid pointer (goodness: +, criticality: medium).
16. Dynamic memory reallocations do not use a temporary pointer in order to avoid losing previously dynamic allocated memory valid pointer (goodness: -, criticality: low).
17. Dynamic memory allocation is declared but never used (goodness: -, criticality: low).
18. No dynamic memory allocation is performed (goodness: -, criticality: low).