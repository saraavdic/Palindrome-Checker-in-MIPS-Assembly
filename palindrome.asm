.data
prompt: .asciiz "Enter a string: "
yes: .asciiz "\nPalindrome\n"
no: .asciiz "\nNot a palindrome\n"
check_more_prompt: .asciiz "\nDo you want to check another string? (y/n): "
buffer: .space 100

.text
.globl main

# === strlen ===
strlen:
li $v0, 0
move $t0, $a0
strlen_loop:
lb $t1, 0($t0)
beq $t1, $zero, strlen_done
addi $v0, $v0, 1
addi $t0, $t0, 1
j strlen_loop
strlen_done:
jr $ra

# === is_palindrome ===
# $a0 = address of string
# $v0 = 1 if palindrome, 0 otherwise
is_palindrome:
addiu $sp, $sp, -8
sw $ra, 4($sp)
sw $s0, 0($sp)

move $s0, $a0 # $s0 = input pointer
jal strlen
move $t3, $v0 # $t3 = length
move $t1, $s0 # $t1 = left pointer
add $t2, $s0, $t3
addi $t2, $t2, -1 # $t2 = right pointer

palindrome_loop:
bge $t1, $t2, palindrome_true

# Skip non-letters/space left
next_left:
lb $a1, 0($t1)
beq $a1, $zero, palindrome_true
beq $a1, 32, skip_left # space
blt $a1, 65, skip_left
bgt $a1, 122, skip_left
ble $a1, 90, upper_left
j check_right

upper_left:
addi $a1, $a1, 32 # to lowercase

check_right:
# Skip non-letters/space right
next_right:
lb $a2, 0($t2)
beq $a2, $zero, palindrome_true
beq $a2, 32, skip_right
blt $a2, 65, skip_right
bgt $a2, 122, skip_right
ble $a2, 90, upper_right
j compare_chars

upper_right:
addi $a2, $a2, 32

compare_chars:
bne $a1, $a2, palindrome_false
addi $t1, $t1, 1
addi $t2, $t2, -1
j palindrome_loop

skip_left:
addi $t1, $t1, 1
j palindrome_loop

skip_right:
addi $t2, $t2, -1
j palindrome_loop

palindrome_true:
li $v0, 1
j end_palindrome

palindrome_false:
li $v0, 0

end_palindrome:
lw $ra, 4($sp)
lw $s0, 0($sp)
addiu $sp, $sp, 8
jr $ra

# === main ===
main:
main_loop:
# Prompt user
li $v0, 4
la $a0, prompt
syscall

# Read input string
li $v0, 8
la $a0, buffer
li $a1, 100
syscall

# Remove newline
la $t0, buffer
remove_nl:
lb $t1, 0($t0)
beq $t1, $zero, after_nl
beq $t1, 10, replace_nl
addi $t0, $t0, 1
j remove_nl
replace_nl:
sb $zero, 0($t0)
after_nl:

# Check palindrome
la $a0, buffer
jal is_palindrome

beq $v0, 1, print_yes
la $a0, no
j print_result

print_yes:
la $a0, yes

print_result:
li $v0, 4
syscall

# Ask again
li $v0, 4
la $a0, check_more_prompt
syscall

li $v0, 8
la $a0, buffer
li $a1, 100
syscall

read_again:
lb $t0, 0($a0) # Get first char
li $t1, 121 # 'y'
li $t2, 89 # 'Y'
beq $t0, $t1, clear_buffer
beq $t0, $t2, clear_buffer

li $t1, 110 # 'n'
li $t2, 78 # 'N'
beq $t0, $t1, exit_program
beq $t0, $t2, exit_program

# Invalid input, re-ask
li $v0, 4
la $a0, check_more_prompt
syscall

li $v0, 8
la $a0, buffer
li $a1, 100
syscall
j read_again

clear_buffer:
la $t0, buffer
li $t1, 100
clear_loop:
sb $zero, 0($t0)
addi $t0, $t0, 1
addi $t1, $t1, -1
bgtz $t1, clear_loop
j main_loop

exit_program:
li $v0, 10
syscall
