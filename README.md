# Palindrome Checker in MIPS Assembly

##  Project Overview
A MIPS Assembly program that checks whether a given string is a palindrome. The program runs in the QTSpim simulator, supports case-insensitive comparison, ignores spaces and non-letter characters, and allows the user to check multiple strings in one session.

##  Features
-  Case-insensitive comparison (e.g., "RaceCar" = palindrome)
-  Ignores spaces and punctuation (e.g., "a man a plan a canal Panama")
-  User-friendly prompts and error handling
-  Reusable session loop (continue checking until user exits)
-  Handles strings up to 100 characters

##  File Structure
project/
├── palindrome_checker.asm # Main MIPS Assembly source code
├── README.md # This file
└── documentation.docx # Full project report (optional)

##  Requirements
- **QTSpim Simulator** (MIPS32 simulator)
- Basic understanding of MIPS assembly (for modification/debugging)

##  How to Run
1. Open **QTSpim**
2. Load the file: `File → Load File` → select `palindrome_checker.asm`
3. Run the program: `Simulator → Run / Continue`
4. Follow the console prompts:
   - Enter a string to check
   - Type `y` to check another or `n` to exit

##  Code Highlights
- **`strlen` function**: Computes string length
- **`is_palindrome` function**: Core palindrome-checking logic with pointer comparison
- **Main loop**: Handles repeated user input and session management
- 
## 🧠Key Concepts Demonstrated
- MIPS memory access (`lb`, `sb`)
- Register usage and stack management
- Loops and conditional branching (`beq`, `bne`, `blt`)
- System calls for I/O
- String manipulation in assembly

##  Authors
- Farah Mašić
- Hatidža Imamović
- Sara Avdić   
- Date: April 11, 2025

## 📚 References
- MIPS Assembly Guide (TutorialsPoint)
- QTSpim Simulator Documentation
- Academic sources on palindromes and low-level programming


- **Buffer clearing**: Ensures clean state between checks

## 📊 Example Output
