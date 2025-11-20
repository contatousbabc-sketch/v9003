@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM EXECUÇÃO GLOBAL - NÃO USA AMBIENTE VIRTUAL

echo ========================================
echo ARQV40 Enhanced - Análise de Mercado IA
echo Versão Atualizada - Python 3.11+ Ready (GLOBAL)
echo ========================================
echo.

REM Define o caminho do Python explicitamente
set PYTHON_PATH=C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe

REM Verifica se Python está instalado no caminho especificado
if not exist "%PYTHON_PATH%" (
    echo ? ERRO: Python não encontrado em %PYTHON_PATH%!
    echo Por favor, execute install_global.bat primeiro.
    pause
    exit /b 1
)

echo ? Python encontrado em: %PYTHON_PATH%
"%PYTHON_PATH%" --version
echo.
echo ========================================
echo ?? VERIFICANDO SISTEMA (GLOBAL)
echo ========================================
echo.

REM === INICIALIZAÇÃO DO FESS ===
echo ?? Verificando Fess Search Engine...

REM Verifica se já está rodando
netstat -an | find "8080" | find "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo ? Fess já está rodando na porta 8080
    goto :check_apis
)

echo ?? Fess não está rodando, verificando instalações...

REM Verifica C:\fess primeiro (sem espaços)
if exist "C:\fess\fess-14.17.0\bin\fess.bat" (
    echo ?? Iniciando Fess de C:\fess (sem espaços)...
    cd /d "C:\fess\fess-14.17.0"
    start /b "" "bin\fess.bat" -s
    cd /d "%~dp0"
    echo ? Aguardando Fess inicializar (20s)...
    timeout /t 20 /nobreak >nul
    echo ? Fess iniciado como fallback do Google CSE
    goto :check_apis
)

REM Verifica diretório pai
if exist "..\fess\fess-14.17.0\bin\fess.bat" (
    echo ?? Iniciando Fess do diretório pai...
    echo ?? AVISO: Caminho com espaços pode causar problemas
    cd /d "..\fess\fess-14.17.0"
    start /b "" "bin\fess.bat" -s
    cd /d "%~dp0"
    echo ? Aguardando Fess inicializar (20s)...
    timeout /t 20 /nobreak >nul
    echo ? Fess iniciado como fallback do Google CSE
    goto :check_apis
)

REM Verifica local
if exist "fess\fess-14.17.0\bin\fess.bat" (
    echo ?? Iniciando Fess local...
    echo ?? AVISO: Caminho com espaços pode causar problemas
    set "FESS_LOCAL_PATH=%~dp0fess\fess-14.17.0"
    cd /d "!FESS_LOCAL_PATH!"
    start /b "" "!FESS_LOCAL_PATH!\bin\fess.bat" -s
    cd /d "%~dp0"
    echo ? Aguardando Fess inicializar (20s)...
    timeout /t 20 /nobreak >nul
    echo ? Fess iniciado como fallback do Google CSE
    goto :check_apis
)

echo ?? Fess não encontrado - funcionará apenas com APIs externas
echo ?? Para instalar Fess sem problemas: execute install_fess_c_drive.bat
echo ?? Locais verificados:
echo    - C:\fess\fess-14.17.0\ (recomendado - sem espaços)
echo    - ..\fess\fess-14.17.0\
echo    - fess\fess-14.17.0\

:check_apis
echo.
echo ?? Verificando APIs de IA...
"!PYTHON_PATH!" -c "import os; from pathlib import Path; from dotenv import load_dotenv; env_path = Path('.env'); load_dotenv(env_path) if env_path.exists() else None; apis = []; [apis.append('Gemini') for k in [os.getenv('GEMINI_API_KEY')] if k and k != 'sua-chave-aqui']; [apis.append('OpenAI') for k in [os.getenv('OPENAI_API_KEY')] if k and k != 'sua-chave-aqui']; [apis.append('OpenRouter') for k in [os.getenv('OPENROUTER_API_KEY')] if k and k != 'sua-chave-aqui']; print(f'? APIs configuradas: {apis}') if apis else print('?? Nenhuma API externa configurada - usando modelos locais')" 2>nul

echo.
echo ========================================
echo ?? INICIANDO APLICAÇÃO
echo ========================================
echo.

REM Inicia a aplicação principal
echo ?? Iniciando servidor Flask...
echo ?? Interface será aberta em: http://localhost:5000
echo ?? Aguarde o carregamento completo...
echo.
echo ?? Para parar: pressione Ctrl+C
echo ========================================
echo.

REM Executa a aplicação
cd /d "%~dp0"
"!PYTHON_PATH!" src/run.py

echo.
echo ========================================
echo ?? APLICAÇÃO FINALIZADA
echo ========================================
pause