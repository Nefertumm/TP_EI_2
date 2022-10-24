from __future__ import annotations

def logger(log_string : str, arch : str = 'logs.log') -> None:
    with open(arch, 'a') as file:
        file.write(log_string + '\n')
