from pathlib import Path


def create_shortcut():
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        root = Path(__file__).resolve().parent
        shortcut_path = root / "CFO_AUTONOMO.lnk"
        target_bat = root / "INICIAR_CFO_AUTONOMO.bat"
        
        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = str(target_bat)
        shortcut.WorkingDirectory = str(root)
        shortcut.IconLocation = "shell32.dll,44" # Standard briefcase/calculator icon
        shortcut.Description = "Director Financiero Autónomo para PYMEs"
        shortcut.Save()
        print("Shortcut created successfully at:", shortcut_path)
    except (OSError, RuntimeError, ImportError) as e:
        print("Fallback or error:", e)

if __name__ == "__main__":
    create_shortcut()
