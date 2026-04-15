@echo off
chcp 65001 >nul
cd /d %~dp0
python md_reader.py
if errorlevel 1 (
    echo.
    echo 需要安装 PySide6，正在安装...
    pip install PySide6
    python md_reader1.4.2.py
)
pause

