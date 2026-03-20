### Code generality and quality

#### **Objective:**  
Evaluate whether the program adheres to general-purpose, beginner-appropriate coding practices that improve readability, reuse, and usability, checking the correctness of use rather than mere presence. 

#### **Context**:   
Italian language usage is allowed and must not be signalized nor penalized.  
Do not consider the following aspects, they must not trigger any of the `Evaluated Conditions`:  
- commented code.
Consider the following definitions to correctly interpret the `Evaluated Conditions`:
- consistent formatting: regular and coherent among the entire code.

#### **Evaluated Conditions:**  
1. There are hard-coded filenames used instead of using command-line arguments (goodness: -, criticality: medium).
2. The name of data files are passed to the program as command-line parameters (goodness: +, criticality: medium).
3. Formatting (indentation, spacing, brace style) is inconsistent, preventing an acceptable level of clarity and readability (goodness: -, criticality: low).
4. Formatting (indentation, spacing, brace style) is mainly consistent and makes the code accetably readable and clear (goodness: +, criticality: low).
5. There are no comments to support code understandability or to explain complex logic (goodness: -, criticality: low).