from pathlib import Path


def create_shortcut():
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        root = Path(__file__).resolve().parent
        shortcut_path = root / "WORKFORCE_AI_HUB.lnk"
        target_bat = root / "INICIAR_WORKFORCE_AI.bat"
        
        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = str(target_bat)
        shortcut.WorkingDirectory = str(root)
        shortcut.IconLocation = "shell32.dll,269" # Network / users icon
        shortcut.Description = "WORKFORCE AI HUB — Empleados de IA Autónomos a Demanda"
        shortcut.Save()
        print("Shortcut created successfully at:", shortcut_path)
    except (OSError, RuntimeError, ImportError) as e:
        print("Error creating shortcut:", e)

if __name__ == "__main__":
    create_shortcut()
