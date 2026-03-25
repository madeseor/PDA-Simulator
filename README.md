# PDA Simulator

A graphical **Pushdown Automaton (PDA) simulator** developed in Python to recognize the language:

**L = { w^m a^n (i + j) d^n w^-m | n, m ≥ 0, w = (b + c)* }**

This project was created as **Practice #4: Pushdown Automata**, with the goal of building a computational simulation of a PDA that validates strings in the language above and visually shows how the automaton works.

## Overview

The simulator provides an interactive graphical interface where the user can enter a string from the keyboard and observe:

- the current automaton state
- the values of **n** and **m**
- the content of the stack
- the input tape
- step-by-step transitions
- final acceptance or rejection of the string

This helps illustrate how a pushdown automaton processes input and uses its stack to verify a formal language.

## Objective

The main objective of this project is to simulate a pushdown automaton capable of recognizing the language:

**L = { w^m a^n (i + j) d^n w^-m | n, m ≥ 0, w = (b + c)* }**

The program was designed to:

- receive input strings from the keyboard
- simulate the PDA behavior computationally
- graphically display states and transitions
- show the stack evolution during execution
- indicate whether the string is accepted or rejected

## Language Description

The language has the following structure:

- **w^m**: a sequence of symbols made of `b` and `c`
- **a^n**: a sequence of `a`
- **(i + j)**: a pivot symbol, either `i` or `j`
- **d^n**: a sequence of `d` that must match the number of `a`
- **w^-m**: the final part validated using the stack contents

### Informally:
1. The automaton reads a prefix made of `b` and `c` symbols.
2. Then it reads a block of `a` symbols.
3. It must find a pivot symbol: `i` or `j`.
4. After that, it reads `d` symbols to match the number of `a`.
5. Finally, it verifies the remaining symbols using the stack.
6. The string is accepted only if the input is fully consumed and the stack is empty.

## Features

- Interactive graphical interface
- Keyboard input for test strings
- Visual simulation of PDA states
- Real-time stack display
- Input tape visualization
- Step-by-step navigation
- Automatic animation mode
- Speed control for the simulation
- Acceptance/rejection feedback

## Technologies Used

- **Python 3**
- **Matplotlib**
- Native Matplotlib widgets:
  - `Button`
  - `TextBox`
  - `Slider`

## Requirements

Before running the project, make sure you have:

- Python 3 installed
- Matplotlib installed

Install Matplotlib with:

```bash
pip install matplotlib
