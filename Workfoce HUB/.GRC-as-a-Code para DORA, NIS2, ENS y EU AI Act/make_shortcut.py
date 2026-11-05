import os
import sys
from pathlib import Path

def create_shortcut():
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        root = Path(__file__).resolve().parent
        shortcut_path = root / "COMPLIANCE_SENTINEL.lnk"
        target_bat = root / "INICIAR_COMPLIANCE_SENTINEL.bat"
        
        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = str(target_bat)
        shortcut.WorkingDirectory = str(root)
        shortcut.IconLocation = "shell32.dll,48" # Shield / security icon
        shortcut.Description = "COMPLIANCE SENTINEL — GRC-as-a-Code para DORA, NIS2, ENS y EU AI Act"
        shortcut.Save()
        print("Shortcut created successfully at:", shortcut_path)
    except Exception as e:
        print("Error creating shortcut:", e)

if __name__ == "__main__":
    create_shortcut()
