#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime

from engineering_team.crew import EngineeringTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

requirements = """
A modular calculator application written in Python that performs both basic and scientific mathematical operations.
The calculator must support addition, subtraction, multiplication, and division between two or more numbers.
Division must handle division by zero and display an appropriate error message.
The calculator must also support scientific operations, including power (x^y), square root, sine, cosine, tangent, and natural logarithm.
All trigonometric operations are to be calculated in radians.
The calculator must include an operation history feature that stores the last 10 operations performed.
The user should be able to view the full history or clear it when desired.
The history is kept only in memory during the program execution and is not persisted to disk.
The application should provide a command-line interface (CLI) where the user can type expressions such as '5 + 3 * 2' and receive a computed result.
Optional: a simple web interface can be implemented for user interaction using Flask or a basic HTML front-end.
Input validation must ensure that only valid mathematical expressions are processed, rejecting any invalid or unsafe input.
Clear error messages must be shown for invalid syntax, math errors (like log of a negative number), or unsupported characters.
The code must be organized into separate modules: one for basic operations, one for scientific functions, one for managing history, one for the user interface, and one main entry point that connects them.
The math module should be used for advanced calculations.
Unit tests must be included to verify correct operation results, error handling, and history management.
"""
module_name = "calculator.py"
class_name = "Calculator"


def run():
    """
    Run the research crew.
    """
    inputs = {
        'requirements': requirements,
        'module_name': module_name,
        'class_name': class_name
    }

    # Create and run the crew
    result = EngineeringTeam().crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    run()