import os
import shutil


def available_shells():
    # Exercise native shells plus pkgsrc variants when installed.
    candidates = ["/bin/sh", "/bin/bash", "/bin/ksh", "/bin/zsh",
                  "/opt/pkg/bin/bash", "/opt/pkg/bin/zsh",
                  "/usr/pkg/bin/bash", "/usr/pkg/bin/ksh", "/usr/pkg/bin/zsh"]
    for name in ("bash", "ksh", "zsh"):
        path = shutil.which(name)
        if path:
            candidates.append(path)
    return sorted({path for path in candidates if os.access(path, os.X_OK)})


def without_startup_files(shell):
    # Keep each shell from reading the developer's own startup files.
    name = os.path.basename(shell)
    if name == "bash":
        return ["--noprofile", "--norc"]
    if name == "zsh":
        return ["-f"]
    return []
