"""
Main file for the Filament manager application.
Used for initializing and launching the GUI.

Creator: Adam Romero
Last Updated: 6/30/2026
"""

from PyQt6.QtWidgets import QApplication
from logic import Logic

def main() -> None:
    """
    Initializes the QApplication and displays the main window.
    """
    application = QApplication([])
    window = Logic()
    window.show()
    application.exec()

if __name__ == "__main__":
    main()