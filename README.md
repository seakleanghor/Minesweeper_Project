This project implements the classic Minesweeper game using Python and Pygame.

#Features Implemented
Core Logic: Complete implementation of reveal() (including recursive zero-mine opening), placemines() (with first-click safety), and win/loss checks.
User Interaction: Full support for right-click Flagging (toggleflag) and Middle-Click Chording (handlemouse quick reveal).

#Git Workflow Summary
All development adhered to the project's strict Git requirements:
Development was performed exclusively on the implement branch.
Each function (is_inbounds, placemines, handlemouse, etc.) was committed individually using the message format: "implement [function name]".
The final project was merged from implement into main.

#How to Run the Game
Prerequisite: Ensure Python 3.x and Pygame are installed (pip install pygame).
Navigate to the project folder (cd Minesweeper_Project).
Run: python run.py
