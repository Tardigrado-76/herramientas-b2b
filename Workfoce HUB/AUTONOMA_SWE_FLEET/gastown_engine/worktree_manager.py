"""
Gestor Físico de Git Worktrees para Aislamiento Total de Agentes de Codificación.
Permite que N agentes (Polecats) trabajen en paralelo sin colisiones de Git.
"""

import os
import shutil
import subprocess
from pathlib import Path
from pydantic import BaseModel


class WorktreeInfo(BaseModel):
    bead_id: str
    branch_name: str
    worktree_path: str
    is_active: bool
    is_git_native: bool


class WorktreeManager:
    """Gestiona la creación, aislamiento y destrucción de Git Worktrees."""

    def __init__(self, base_repo_path: str, worktrees_dir: str = "sandbox/isolated_worktrees"):
        self.base_repo_path = os.path.abspath(base_repo_path)
        self.worktrees_dir = os.path.abspath(worktrees_dir)
        os.makedirs(self.worktrees_dir, exist_ok=True)
        self.active_worktrees: dict[str, WorktreeInfo] = {}

    def create_worktree(self, bead_id: str, base_branch: str = "main") -> WorktreeInfo:
        """Crea un nuevo worktree aislado y una rama dedicada para el Bead."""
        branch_name = f"polecat/{bead_id}"
        target_path = os.path.join(self.worktrees_dir, bead_id)

        # Si ya existe el directorio, limpiarlo previamente
        if os.path.exists(target_path):
            shutil.rmtree(target_path, ignore_errors=True)

        is_git_native = False
        # Intentar crear git worktree nativo si base_repo_path es un repo git válido
        if os.path.exists(os.path.join(self.base_repo_path, ".git")):
            try:
                # Comprobar si la rama ya existe para no duplicar
                subprocess.run(
                    ["git", "branch", "-D", branch_name],
                    cwd=self.base_repo_path,
                    capture_output=True,
                    text=True
                )
                cmd = ["git", "worktree", "add", "-b", branch_name, target_path, base_branch]
                res = subprocess.run(cmd, cwd=self.base_repo_path, capture_output=True, text=True)
                if res.returncode == 0:
                    is_git_native = True
            except Exception:
                is_git_native = False

        # Si no se pudo usar git worktree nativo (ej. modo sandbox inicial), clonar/copiar directorio base
        if not is_git_native:
            os.makedirs(target_path, exist_ok=True)
            for item in os.listdir(self.base_repo_path):
                if item in [".git", "isolated_worktrees"]:
                    continue
                s = os.path.join(self.base_repo_path, item)
                d = os.path.join(target_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

        info = WorktreeInfo(
            bead_id=bead_id,
            branch_name=branch_name,
            worktree_path=target_path,
            is_active=True,
            is_git_native=is_git_native
        )
        self.active_worktrees[bead_id] = info
        return info

    def remove_worktree(self, bead_id: str) -> bool:
        """Elimina el worktree y libera los recursos del sistema de archivos."""
        info = self.active_worktrees.get(bead_id)
        target_path = os.path.join(self.worktrees_dir, bead_id)

        if info and info.is_git_native and os.path.exists(os.path.join(self.base_repo_path, ".git")):
            try:
                subprocess.run(
                    ["git", "worktree", "remove", "--force", target_path],
                    cwd=self.base_repo_path,
                    capture_output=True
                )
            except Exception:
                pass

        if os.path.exists(target_path):
            shutil.rmtree(target_path, ignore_errors=True)

        if bead_id in self.active_worktrees:
            self.active_worktrees[bead_id].is_active = False
            del self.active_worktrees[bead_id]

        return True

    def list_active_worktrees(self) -> list[WorktreeInfo]:
        return list(self.active_worktrees.values())
