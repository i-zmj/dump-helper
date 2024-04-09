@echo off

IF EXIST %1\* (
    FOR %%f IN (%1\*) DO (
        python3 analyze.py "%%f"
    )
) ELSE (
    python3 analyze.py %1
)
pause