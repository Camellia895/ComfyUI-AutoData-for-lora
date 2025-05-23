@echo off
setlocal enabledelayedexpansion

echo =====================================================
echo ==       ComfyUI 快速重启脚本       ==
echo =====================================================
echo.

REM 定义ComfyUI的根目录和启动脚本路径
set COMFYUI_ROOT=G:\ComfyUI_windows_portable
set COMFYUI_START_SCRIPT="%COMFYUI_ROOT%\run_nvidia_gpu.bat"

REM --- 步骤 1: 终止当前的 ComfyUI 进程 ---
echo [INFO] 正在尝试关闭当前运行的 ComfyUI 实例...

REM 方法 A: 尝试通过窗口标题关闭启动 ComfyUI 的 cmd.exe 窗口
REM run_nvidia_gpu.bat 通常会打开一个 cmd 窗口。我们需要找到这个窗口的标题。
REM 默认情况下，如果 .bat 文件直接运行 python，窗口标题可能是 python.exe 的路径。
REM 如果 .bat 文件有 title 命令，则可能是那个标题。
REM 假设 run_nvidia_gpu.bat 启动的窗口标题中包含 "ComfyUI" 或者就是脚本名 "run_nvidia_gpu.bat"
REM 你可能需要根据实际情况调整这里的 WINDOWTITLE 匹配。
REM taskkill /F /FI "WINDOWTITLE eq run_nvidia_gpu.bat*" /IM cmd.exe /T 2>NUL
REM taskkill /F /FI "WINDOWTITLE eq ComfyUI*" /IM cmd.exe /T 2>NUL

REM 方法 B: 更通用地查找运行 main.py 的 python.exe 进程
REM 这会尝试找到所有由 python.exe 运行且命令行包含 main.py 的进程
set found_pids=
for /f "tokens=2" %%i in ('tasklist /v /fi "imagename eq python.exe" ^| findstr /i /c:"main.py"') do (
    set found_pids=!found_pids! %%i
)

if defined found_pids (
    echo [INFO] 发现以下可能与 ComfyUI 相关的 Python 进程 PID(s):%found_pids%
    for %%p in (%found_pids%) do (
        echo [ACTION] 正在终止 PID: %%p ...
        taskkill /F /PID %%p
    )
    echo [INFO] ComfyUI Python 进程已尝试终止。
) else (
    echo [INFO] 未明确找到运行 main.py 的 Python 进程。可能是因为没有运行，或者查找方式不精确。
)

REM 方法 C: 也尝试关闭可能由 run_nvidia_gpu.bat 启动的 python.exe (如果它直接运行)
REM taskkill /F /IM python.exe /FI "MODULES eq cmd.exe" 2>NUL | findstr /C:"main.py" >NUL

echo [INFO] 等待进程关闭 (3 秒)...
timeout /t 3 /nobreak > NUL

REM --- 步骤 2: 重新启动 ComfyUI ---
echo [INFO] 正在启动 ComfyUI 从: %COMFYUI_START_SCRIPT% ...
cd /D "%COMFYUI_ROOT%"
if not exist %COMFYUI_START_SCRIPT% (
    echo [ERROR] 启动脚本 %COMFYUI_START_SCRIPT% 未找到!
    goto end
)

REM 使用 start 命令可以在新的窗口中异步启动 ComfyUI，
REM 这样这个重启脚本可以继续执行或关闭，而不会变成ComfyUI的控制台。
REM "/B" 选项会尝试在当前窗口启动（不创建新窗口），但如果bat本身就是控制台应用，效果不明显。
REM 为了让ComfyUI在它自己的窗口运行，并允许此脚本执行完毕：
start "ComfyUI Auto Restart" %COMFYUI_START_SCRIPT%
REM 如果你希望这个脚本窗口在ComfyUI启动后保持打开并显示ComfyUI的输出，则使用：
REM call %COMFYUI_START_SCRIPT%

echo [INFO] ComfyUI 启动命令已发送。它应该会在一个新的窗口中启动。

REM --- 步骤 3: 提示用户刷新浏览器 ---
echo.
echo [ACTION] 请等待 ComfyUI 完全启动 (通常需要几秒到几十秒)...
echo [ACTION] 然后，请手动刷新你的浏览器页面 (通常按 F5 或 Ctrl+R)。
echo.

:end
echo [INFO] 重启脚本执行完毕。
timeout /t 5 /nobreak 
exit /B 0