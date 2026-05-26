@echo off
setlocal EnableExtensions
chcp 65001 >nul

cd /d "%~dp0"

echo.
echo ==========================================
echo Gmail EML Import Wizard
echo ==========================================
echo.
echo 이 도구는 원본 EML 파일을 수정/삭제/이동하지 않습니다.
echo.

if not exist "import_eml.py" (
  echo [ERROR] import_eml.py 파일이 이 폴더에 없습니다.
  pause
  exit /b 1
)

if not exist "requirements.txt" (
  echo [ERROR] requirements.txt 파일이 이 폴더에 없습니다.
  pause
  exit /b 1
)

if not exist "credentials.json" (
  echo [ERROR] credentials.json 파일이 이 폴더에 없습니다.
  echo Google Cloud에서 Desktop OAuth JSON을 받아 credentials.json 이름으로 저장하세요.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Python 가상환경을 만듭니다. 처음 한 번만 실행됩니다.
  py -3 -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Python 가상환경 생성 실패
    pause
    exit /b 1
  )
)

echo 필요한 Python 패키지를 확인/설치합니다.
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] 패키지 설치 실패
  pause
  exit /b 1
)

if not exist "logs" mkdir logs
if not exist "state" mkdir state

:menu
echo.
echo ==========================================
echo 실행할 작업을 선택하세요
echo ==========================================
echo 1. Dry-run: Gmail에 넣지 않고 EML 검사만 하기
echo 2. Sample: Gmail에 10개만 테스트로 넣기
echo 3. Full Inbox: 받은메일 전체 넣기
echo 4. Full Sent: 보낸메일 전체 넣기
echo 5. 종료
echo.
set /p choice="번호를 입력하세요: "

if "%choice%"=="1" goto dryrun
if "%choice%"=="2" goto sample
if "%choice%"=="3" goto full_inbox
if "%choice%"=="4" goto full_sent
if "%choice%"=="5" goto end

echo 잘못된 번호입니다.
goto menu

:ask_path
echo.
echo EML 파일들이 들어있는 폴더 경로를 붙여넣으세요.
echo 예: C:\Users\username\email-archive\eml
set /p eml_dir="EML 폴더: "
if not exist "%eml_dir%" (
  echo [ERROR] 폴더를 찾을 수 없습니다: %eml_dir%
  goto ask_path
)
exit /b 0

:dryrun
call :ask_path
echo.
echo Dry-run을 실행합니다. Gmail에는 아무것도 넣지 않습니다.
".venv\Scripts\python.exe" import_eml.py --mode dry-run --source-dir "%eml_dir%"
echo.
echo 완료. logs 폴더의 dry_run_report.csv를 확인하세요.
pause
goto menu

:sample
call :ask_path
echo.
echo Gmail에 테스트 메일 10개만 넣습니다.
echo 브라우저 로그인/승인 화면이 뜨면 본인 Gmail 계정인지 직접 확인하고 승인하세요.
".venv\Scripts\python.exe" import_eml.py --mode sample --source-dir "%eml_dir%" --limit 10 --label "Inbox-eml import" --repair-malformed-headers
echo.
echo Gmail에서 Inbox-eml import 라벨을 확인하세요.
pause
goto menu

:full_inbox
call :ask_path
echo.
echo [중요] 받은메일 전체 import를 시작합니다.
echo Sample 10개 확인이 끝난 뒤에만 진행해야 합니다.
set /p ok="정말 진행하려면 YES 입력: "
if /i not "%ok%"=="YES" (
  echo 취소했습니다.
  goto menu
)
".venv\Scripts\python.exe" import_eml.py --mode full --source-dir "%eml_dir%" --label "Inbox-eml import" --repair-malformed-headers --confirm-full-import
echo.
echo 받은메일 import가 끝났습니다.
pause
goto menu

:full_sent
call :ask_path
echo.
echo [중요] 보낸메일 전체 import를 시작합니다.
echo Sample 확인이 끝난 뒤에만 진행해야 합니다.
set /p ok="정말 진행하려면 YES 입력: "
if /i not "%ok%"=="YES" (
  echo 취소했습니다.
  goto menu
)
".venv\Scripts\python.exe" import_eml.py --mode full --source-dir "%eml_dir%" --label "Sent-eml import" --repair-malformed-headers --confirm-full-import
echo.
echo 보낸메일 import가 끝났습니다.
pause
goto menu

:end
echo 종료합니다.
endlocal
