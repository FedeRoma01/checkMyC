### Correct use of dynamic memory

#### **Objective:**  
Evaluate the presence of dynamic memory operations across allocation, use, reallocation, and deallocation.

#### **Context**:   
Consider the following definitions to correctly interpret the `Evaluated Conditions`:
- temporary pointer: intermediate variable used to store the address returned by realloc before updating the original pointer.
- resizing strategy: condition that enable the resizing of the dynamic allocated vector; it does not consider the check for failure allocation.

#### **Evaluated Conditions:**
1. Allocated memory does not match the required type size, causing under-allocation or incorrect casting (goodness: -, criticality: medium).
2. Dynamic allocated memory without out-of-bounds access (goodness: +, criticality: high).
3. Allocated buffers are freed more than once or with wrong pointer (goodness: -, criticality: medium).
4. There are cases of dereferencing or accessing a pointer that may be NULL due to a failed or unchecked allocation (goodness: -, criticality: low).
5. There are incorrect or unsafe resizing strategies (goodness: -, criticality: medium).
6. The array used to store data read from file is dynamically allocated with malloc and expanded using realloc as new data are read (goodness: +, criticality: medium).
7. The reallocation strategy suitably increases the size of the dynamic reallocated vector whenever the next insertion would exceed the currently allocated capacity (goodness: +, criticality: medium).
8. The reallocation strategy increases the size of the dynamic reallocated vector by one or another value that leads to an excessive amount of reallocations (goodness: -, criticality: low).
9. The array used to store the data read from the file is dynamically allocated using malloc but not expanded with realloc in case of exceeding the capacity of the allocated array (goodness: -, criticality: medium).
10. Memory space is wasted due to an excessive size of the dynamic reallocated vector, whose size is not suitably reduced at the end of the reading loop (goodness: -, criticality: low).
11. Memory space is saved thanks to a suitable reduction of the size of the dynamic reallocated vector using realloc at the end of the reading loop (goodness: +, criticality: medium).   
12. Allocated memory is never explicitly relesead with free when it is no more needed (goodness: -, criticality: low).
13. Allocated memory is correctly released before terminating the program using free (goodness: +, criticality: low).
14. Dynamic memory reallocations use a temporary pointer in order to avoid losing previously dynamic allocated memory valid pointer (goodness: +, criticality: medium).
15. Dynamic memory reallocations do not use a temporary pointer in order to avoid losing previously dynamic allocated memory valid pointer (goodness: -, criticality: low).
16. Dynamic memory allocation is declared but never used (goodness: -, criticality: low).
17. No dynamic memory allocation is performed (goodness: -, criticality: high).