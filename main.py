import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout
from GUI.MainWindow import MainWindow
from AI.MainController import MainController


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    # Initialize MovementController with drones and obstacles
    drones = main_window.drones
    obstacles = main_window.obstacles
    target = main_window.target
    mainController = MainController(drones, obstacles, target)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
