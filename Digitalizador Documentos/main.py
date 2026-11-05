"""Entry point for the LALA Desktop Application.

Initializes PySide6 QApplication, applies executive high-DPI scaling,
and displays the primary MainWindow.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from config import AppConfig
from gui.main_window import MainWindow


def main() -> None:
    """Initialize and run LALA application."""
    # Ensure High DPI attributes
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(AppConfig.APP_NAME)
    app.setApplicationVersion(AppConfig.APP_VERSION)
    app.setOrganizationName("LALA Intelligence")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
