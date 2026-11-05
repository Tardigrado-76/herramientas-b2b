from pathlib import Path

def create_shortcut():
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        root = Path(__file__).resolve().parent
        
        # Shortcut inside AUTONOMOUS_CFO_LEGAL_GUARD
        shortcut_path = root / "CFO_LEGAL_GUARD.lnk"
        target_bat = root / "INICIAR_CFO_LEGAL_GUARD.bat"
        
        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = str(target_bat)
        shortcut.WorkingDirectory = str(root)
        shortcut.IconLocation = "shell32.dll,47" # Padlock / Security icon
        shortcut.Description = "AUTONOMOUS CFO & LEGAL GUARD — Dirección Financiera y Compliance Legal Autónomo"
        shortcut.Save()
        print("Shortcut created at:", shortcut_path)

        # Shortcut in parent directory NEW TOOLS
        parent_root = root.parent
        parent_shortcut_path = parent_root / "CFO_LEGAL_GUARD.lnk"
        parent_shortcut = shell.CreateShortcut(str(parent_shortcut_path))
        parent_shortcut.TargetPath = str(target_bat)
        parent_shortcut.WorkingDirectory = str(root)
        parent_shortcut.IconLocation = "shell32.dll,47"
        parent_shortcut.Description = "AUTONOMOUS CFO & LEGAL GUARD — Dirección Financiera y Compliance Legal Autónomo"
        parent_shortcut.Save()
        print("Root shortcut created at:", parent_shortcut_path)

    except Exception as e:
        print("Error creating shortcut:", e)

if __name__ == "__main__":
    create_shortcut()
