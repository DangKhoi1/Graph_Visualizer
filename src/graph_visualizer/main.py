"""Application entry point."""
import sys
from pathlib import Path

# IDEs often execute this file directly instead of running the package.
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "graph_visualizer"

from PyQt5.QtWidgets import QApplication
from .gui import GraphGUI


def main():
    app = QApplication(sys.argv)
    window = GraphGUI()
    window.showMaximized()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
