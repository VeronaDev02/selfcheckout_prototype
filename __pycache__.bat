@echo off
cd /d "%~dp0"
for /d /r %%i in (__pycache__) do (
	echo Deletando %%i
	rd /s /q "%%i"
)
echo Limpeza concluída!
pause