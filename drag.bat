@echo off

IF EXIST %1\* (
    FOR %%f IN (%1\*) DO (
        analyze.exe "%%f"
    )
) ELSE (
    analyze.exe %1
)
pause