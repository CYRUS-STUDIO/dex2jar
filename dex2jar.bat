@echo off
setlocal enabledelayedexpansion

:: 提示输入 dex 文件目录
set /p dex_dir=请输入 dex 文件所在的目录（绝对路径或相对路径）:

:: 判断目录是否存在
if not exist "%dex_dir%" (
    echo 目录不存在: %dex_dir%
    pause
    exit /b
)

:: 创建输出 jar 目录
set "jar_dir=%dex_dir%\jar"
if not exist "%jar_dir%" (
    mkdir "%jar_dir%"
)

:: 查找所有 dex 文件
for /r "%dex_dir%" %%f in (*.dex) do (
    set "dex_file=%%f"
    set "file_name=%%~nf"
    echo 正在转换: !dex_file!

    :: 构造输出路径
    set "out_jar=%jar_dir%\!file_name!.jar"

    :: 调用 dex2jar 脚本
    call ./d2j-dex2jar.bat -f -o "!out_jar!" "!dex_file!"
)

echo 所有 dex 文件已转换完成，jar 输出目录: %jar_dir%
pause
