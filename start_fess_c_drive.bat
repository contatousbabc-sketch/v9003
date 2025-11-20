@echo off 
REM Inicia Fess instalado em C:\fess 
echo ======================================== 
echo Iniciando Fess - Unidade C: 
echo ======================================== 
echo. 
 
REM Verifica se já está rodando 
netstat -an | find "8080" | find "LISTENING" >nul 
if %errorlevel% equ 0 ( 
    echo ✅ Fess já está rodando na porta 8080 
    echo 🌐 Interface: http://localhost:8080 
    goto :end 
) 
 
echo 🚀 Iniciando Fess... 
cd /d "C:\fess\fess-14.17.0" 
start /b "" "bin\fess.bat" -s 
echo ⏳ Aguardando inicialização (30s)... 
timeout /t 30 /nobreak >nul 
echo ✅ Fess iniciado! 
echo 🌐 Interface: http://localhost:8080 
echo 🔧 Admin: http://localhost:8080/admin (admin/admin) 
echo. 
:end 
pause 
