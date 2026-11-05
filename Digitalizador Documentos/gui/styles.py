"""Corporate Dark Theme and UI styling tokens for LALA Application.

Inspired by executive dashboard aesthetics:
- High contrast, dark slate and charcoal surfaces
- Sophisticated accents (Royal Blue, Emerald, Amber, Rose)
- Polished controls, clean table rendering, modern headers
"""

CORPORATE_DARK_STYLESHEET = """
/* ==========================================================================
   Global Base & Typography
   ========================================================================== */
QWidget {
    background-color: #13141a;
    color: #f3f4f6;
    font-family: 'Segoe UI', 'SF Pro Text', -apple-system, system-ui, Roboto, sans-serif;
    font-size: 13px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QMainWindow, QDialog {
    background-color: #13141a;
}

/* ==========================================================================
   Panels, Cards & GroupBoxes
   ========================================================================== */
QGroupBox {
    background-color: #1c1d25;
    border: 1px solid #2e303e;
    border-radius: 8px;
    margin-top: 24px;
    padding: 16px 14px 14px 14px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    top: 6px;
    padding: 2px 8px;
    color: #93c5fd;
    background-color: #13141a;
    border-radius: 4px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QFrame#card {
    background-color: #1c1d25;
    border: 1px solid #2e303e;
    border-radius: 8px;
    padding: 12px;
}

/* ==========================================================================
   Inputs, LineEdits & SpinBoxes
   ========================================================================== */
QLineEdit {
    background-color: #0f1014;
    border: 1px solid #333647;
    border-radius: 6px;
    padding: 8px 12px;
    color: #ffffff;
    selection-background-color: #3b82f6;
}

QLineEdit:hover {
    border: 1px solid #4f536c;
}

QLineEdit:focus {
    border: 1px solid #3b82f6;
    background-color: #151720;
}

QLineEdit:disabled {
    background-color: #181920;
    color: #6b7280;
    border: 1px solid #282a36;
}

QCheckBox {
    spacing: 8px;
    color: #e5e7eb;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #4b5563;
    background-color: #0f1014;
}

QCheckBox::indicator:hover {
    border: 1px solid #3b82f6;
}

QCheckBox::indicator:checked {
    background-color: #2563eb;
    border: 1px solid #3b82f6;
    image: none;
}

/* ==========================================================================
   Buttons
   ========================================================================== */
QPushButton {
    background-color: #262835;
    color: #ffffff;
    border: 1px solid #3a3d50;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #323547;
    border: 1px solid #4f536e;
}

QPushButton:pressed {
    background-color: #1f212c;
}

QPushButton:disabled {
    background-color: #181922;
    color: #64748b;
    border: 1px solid #232531;
}

/* Specific Action Button Styles */
QPushButton#primary_button {
    background-color: #2563eb;
    border: 1px solid #3b82f6;
    color: #ffffff;
    font-size: 13px;
    padding: 10px 20px;
}

QPushButton#primary_button:hover {
    background-color: #1d4ed8;
    border: 1px solid #60a5fa;
}

QPushButton#primary_button:pressed {
    background-color: #1e40af;
}

QPushButton#secondary_button {
    background-color: #4f46e5;
    border: 1px solid #6366f1;
    color: #ffffff;
    font-size: 13px;
    padding: 10px 20px;
}

QPushButton#secondary_button:hover {
    background-color: #4338ca;
    border: 1px solid #818cf8;
}

QPushButton#success_button {
    background-color: #059669;
    border: 1px solid #10b981;
    color: #ffffff;
    font-size: 13px;
    padding: 10px 20px;
}

QPushButton#success_button:hover {
    background-color: #047857;
    border: 1px solid #34d399;
}

QPushButton#danger_button {
    background-color: #dc2626;
    border: 1px solid #ef4444;
    color: #ffffff;
}

QPushButton#danger_button:hover {
    background-color: #b91c1c;
}

/* ==========================================================================
   Table Widget (QTableWidget)
   ========================================================================== */
QTableWidget {
    background-color: #16171f;
    alternate-background-color: #1c1e27;
    border: 1px solid #2e303e;
    border-radius: 6px;
    gridline-color: #282a38;
    color: #f3f4f6;
    selection-background-color: #1e3a8a;
    selection-color: #ffffff;
    outline: none;
}

QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #222430;
}

QTableWidget::item:hover {
    background-color: #242736;
}

QTableWidget::item:selected {
    background-color: #1e3a8a;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #222430;
    color: #93c5fd;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #2e303e;
    border-bottom: 2px solid #3b82f6;
    font-weight: bold;
    font-size: 12px;
    text-transform: uppercase;
}

QTableCornerButton::section {
    background-color: #222430;
    border: none;
}

/* ==========================================================================
   TextEdit & Log Console
   ========================================================================== */
QTextEdit#console_log {
    background-color: #0c0d10;
    color: #d1d5db;
    border: 1px solid #2a2c3a;
    border-radius: 6px;
    font-family: 'Cascadia Code', 'Fira Code', Consolas, 'Courier New', monospace;
    font-size: 12px;
    padding: 10px;
    line-height: 1.4;
}

/* ==========================================================================
   Scrollbars
   ========================================================================== */
QScrollBar:vertical {
    background: #121318;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #333647;
    min-height: 25px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #4f536c;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #121318;
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background: #333647;
    min-width: 25px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background: #4f536c;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ==========================================================================
   Progress Bar
   ========================================================================== */
QProgressBar {
    background-color: #16171f;
    border: 1px solid #2e303e;
    border-radius: 4px;
    height: 10px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #38bdf8);
    border-radius: 3px;
}

/* ==========================================================================
   Status Bar & Tooltip
   ========================================================================== */
QStatusBar {
    background-color: #0e0f13;
    color: #9ca3af;
    border-top: 1px solid #242633;
}

QToolTip {
    background-color: #1f212c;
    color: #f3f4f6;
    border: 1px solid #3b82f6;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}

/* ==========================================================================
   Splitter
   ========================================================================== */
QSplitter::handle {
    background-color: #242634;
}

QSplitter::handle:hover {
    background-color: #3b82f6;
}
"""
