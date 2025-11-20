@echo off
chcp 65001 >nul
echo ========================================
echo ?? LIMPEZA DE CACHE PYTHON
echo ========================================
echo.

echo ?? Diretório atual: %CD%
echo ?? Data/Hora: %date% %time%
echo.

echo ?? Removendo arquivos .pyc...
for /r %%i in (*.pyc) do (
    echo Removendo: %%i
    del "%%i" >nul 2>&1
)

echo ?? Removendo diretórios __pycache__...
for /d /r %%i in (__pycache__) do (
    echo Removendo: %%i
    rmdir /s /q "%%i" >nul 2>&1
)

echo ?? Removendo arquivos .pyo...
for /r %%i in (*.pyo) do (
    echo Removendo: %%i
    del "%%i" >nul 2>&1
)

echo.
echo ? Cache Python limpo com sucesso!
echo.
echo ?? PRÓXIMOS PASSOS:
echo 1. Execute: install.bat
echo 2. Execute: diagnostico_ambiente.bat
echo 3. Reinicie a aplicação
echo.
pause