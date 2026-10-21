@echo off
title PharmaLeaf AI Launcher
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================================
echo   PharmaLeaf AI — نظام استخراج وتحليل النشرات الدوائية
echo ========================================================
echo.

if exist "dist\PharmaLeaf-AI\PharmaLeaf-AI.exe" (
    echo [1/2] تشغيل النسخة التنفيذية المجمعة Standalone...
    start "" "dist\PharmaLeaf-AI\PharmaLeaf-AI.exe"
    exit /b 0
)

echo [2/2] تشغيل عبر بيئة Python المحلية...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo حدث خطأ أثناء تشغيل التطبيق. اضغط أي مفتاح للإغلاق...
    pause > nul
)
