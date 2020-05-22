from pathlib import Path
from typing import List, Union

from ._types import BlacklistType, PathLike




def modify_weakaura(blacklist: BlacklistType, sv_path: Union[str, Path]) -> None:
    # Check that the SavedVariables path is correct
    path = Path(sv_path) # everything from here on will be a pathlib.Path obj
    _check_savedvars_path(path)
    
    # Check that the SavedVariables file exists
    path = path / "WeakAuras.lua"
    _check_wa_savedvars_path(path)

    sv = load_wa_savedvars(path) # Get WeakAuras.lua as a string

    start = sv.find("local MoPBlacklist = {")
    stop = start
    for _ in range(3):
        stop = sv.find("}", stop+1)
    s = f"{sv[:start]}{get_blacklist_str(blacklist)}{sv[stop+1:]}"

    save_wa_savedvars(path, s)
    

def _check_savedvars_path(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError("SavedVariables path does not exist")
    elif not path.is_dir():
        raise ValueError("Must be a path to a directory")
    elif not path.name == "SavedVariables":
        raise ValueError(
            "Incorrect path. It should look something like this:\n"
            "C:/<WoW Path>/WTF/Account/<Your Account>/SavedVariables"
        )


def _check_wa_savedvars_path(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            "Unable to find 'WeakAuras.lua'. "
            "Make sure the addon is installed and you've typed /wa at least once."
        )


def get_blacklist_str(blacklist: BlacklistType) -> str:
    def _iter_items(l: List[str]) -> str:
        return ",\\n".join([f'      \\"{b}\\"' for b in l])
    
    s = "local MoPBlacklist = {"

    # Add players
    s += '\\n    [\\"players\\"] = {\\n'
    s += _iter_items(blacklist["players"])
    s += "\\n    },\\n"

    # Add guilds
    s += '    [\\"guilds\\"] = {\\n'
    s += _iter_items(blacklist["guilds"])
    s += "\\n    }\\n"

    s+= "\\n  }"

    return s


def load_wa_savedvars(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_wa_savedvars(path: Path, saved_vars: str) -> None:
    backup = path.parent/"WeakAuras.lua.blbak"
    if backup.exists():
        backup.unlink()
    path.rename(path.parent/"WeakAuras.lua.blbak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(saved_vars)
