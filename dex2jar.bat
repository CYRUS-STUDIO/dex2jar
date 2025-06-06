@echo off
setlocal enabledelayedexpansion

:: ��ʾ���� dex �ļ�Ŀ¼
set /p dex_dir=������ dex �ļ����ڵ�Ŀ¼������·�������·����:

:: �ж�Ŀ¼�Ƿ����
if not exist "%dex_dir%" (
    echo Ŀ¼������: %dex_dir%
    pause
    exit /b
)

:: ������� jar Ŀ¼
set "jar_dir=%dex_dir%\jar"
if not exist "%jar_dir%" (
    mkdir "%jar_dir%"
)

:: �������� dex �ļ�
for /r "%dex_dir%" %%f in (*.dex) do (
    set "dex_file=%%f"
    set "file_name=%%~nf"
    echo ����ת��: !dex_file!

    :: �������·��
    set "out_jar=%jar_dir%\!file_name!.jar"

    :: ���� dex2jar �ű�
    call ./d2j-dex2jar.bat -f -o "!out_jar!" "!dex_file!"
)

echo ���� dex �ļ���ת����ɣ�jar ���Ŀ¼: %jar_dir%
pause
