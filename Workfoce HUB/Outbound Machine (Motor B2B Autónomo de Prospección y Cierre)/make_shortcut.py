import os
import sys
from pathlib import Path

def create_shortcut():
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        root = Path(__file__).resolve().parent
        shortcut_path = root / "OUTBOUND_MACHINE.lnk"
        target_bat = root / "INICIAR_OUTBOUND_MACHINE.bat"
        
        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = str(target_bat)
        shortcut.WorkingDirectory = str(root)
        shortcut.IconLocation = "shell32.dll,264" # Target / rocket / radar icon
        shortcut.Description = "OUTBOUND MACHINE — Motor B2B Autónomo de Prospección y Cierre"
        shortcut.Save()
        print("Shortcut created successfully at:", shortcut_path)
    except Exception as e:
        print("Error creating shortcut:", e)

if __name__ == "__main__":
    create_shortcut()
