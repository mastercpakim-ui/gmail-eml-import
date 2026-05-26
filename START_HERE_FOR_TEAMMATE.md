# 먼저 이것부터 보세요

이 문서는 개발을 모르는 사람 기준입니다.

목표는 딱 하나입니다.

> 내 PC에 있는 `.eml` 백업 메일을 새 Gmail 계정으로 옮기기

## 가장 쉬운 방법: Claude Code에게 시키기

Claude Code를 쓸 수 있으면, 직접 명령어를 외울 필요가 없습니다.

먼저 아래 순서대로 준비만 해 주세요.

1. 이 GitHub repo를 ZIP으로 다운로드합니다.
2. ZIP 압축을 풉니다.
3. 압축 푼 폴더 안에 아래 폴더 2개를 만듭니다.

```text
받은편지
보낸편지
```

4. 받은메일 EML 파일들은 `받은편지` 폴더 안에 넣습니다.
5. 보낸메일 EML 파일들은 `보낸편지` 폴더 안에 넣습니다.
6. `CREATE_CREDENTIALS_STEP_BY_STEP.md`를 보고 `credentials.json`을 만듭니다.
7. `credentials.json`을 `run_import_wizard.bat`와 같은 폴더에 넣습니다.
8. Claude Code를 열고, 압축 푼 폴더를 작업 폴더로 선택합니다.
9. Claude Code에 아래 문장을 그대로 붙여넣습니다.

```text
나는 개발을 잘 모릅니다.
이 폴더의 START_HERE_FOR_TEAMMATE.md와 README.md를 읽고,
내 백업 EML을 Gmail로 import해 주세요.

폴더 구조는 다음과 같습니다.
- 받은메일 EML: ./받은편지
- 보낸메일 EML: ./보낸편지
- Gmail OAuth 파일: ./credentials.json

반드시 이 순서로 진행해 주세요.
1. credentials.json 존재 여부 확인
2. 받은편지 폴더 dry-run
3. 보낸편지 폴더 dry-run
4. 받은편지 sample 10개만 Gmail로 import
5. 내가 Gmail에서 10개 확인할 때까지 멈추기
6. 내가 OK하면 받은편지 전체 import
7. 내가 OK하면 보낸편지 전체 import
8. timeout이나 누락이 있으면 재시도
9. 마지막에 final_missing_imports.csv 기준으로 누락 0개인지 확인

중요:
- 원본 EML 파일은 수정, 삭제, 이동, 이름 변경하지 마세요.
- token.json은 절대 공유하지 마세요.
- full import는 내가 OK하기 전에는 실행하지 마세요.
- OAuth 승인 화면이 뜨면 내가 직접 계정 확인 후 승인하겠습니다.
```

이 방식이면 팀원이 직접 dry-run이나 Python 명령어를 이해할 필요가 없습니다.

## Claude Code 없이 직접 실행하는 경우

아래 순서대로만 하면 됩니다.

1. 이 GitHub repo를 ZIP으로 다운로드
2. ZIP 압축 풀기
3. 압축 푼 폴더 안에 `받은편지`, `보낸편지` 폴더 만들기
4. 받은메일 EML은 `받은편지`에 넣기
5. 보낸메일 EML은 `보낸편지`에 넣기
6. Google에서 `credentials.json` 파일 만들기
7. `credentials.json`을 압축 푼 폴더에 넣기
8. `run_import_wizard.bat` 더블클릭
9. 메뉴에서 `1`번 실행
10. 메뉴에서 `2`번 실행
11. Gmail에서 10개 확인
12. 문제 없으면 `3`번 또는 `4`번 실행

## 1. GitHub에서 다운로드

1. GitHub repo 화면을 엽니다.
2. 초록색 `Code` 버튼을 누릅니다.
3. `Download ZIP`을 누릅니다.
4. 다운로드된 ZIP 파일을 압축 풉니다.

압축을 풀면 이런 파일들이 보여야 합니다.

```text
import_eml.py
requirements.txt
run_import_wizard.bat
README.md
CREATE_CREDENTIALS_STEP_BY_STEP.md
```

그리고 직접 아래 폴더 2개를 만들어 주세요.

```text
받은편지
보낸편지
```

최종 폴더 모양은 대략 이렇게 됩니다.

```text
gmail-eml-import
├─ 받은편지
├─ 보낸편지
├─ credentials.json
├─ import_eml.py
├─ requirements.txt
├─ run_import_wizard.bat
├─ README.md
└─ CREATE_CREDENTIALS_STEP_BY_STEP.md
```

## 2. credentials.json 만들기

이 단계가 제일 어렵습니다.

아래 파일을 열고 그대로 따라 하세요.

```text
CREATE_CREDENTIALS_STEP_BY_STEP.md
```

최종 목표는 압축 푼 폴더 안에 아래 파일이 생기는 것입니다.

```text
credentials.json
```

반드시 `run_import_wizard.bat`와 같은 폴더에 있어야 합니다.

## 3. run_import_wizard.bat 실행

`run_import_wizard.bat`를 더블클릭합니다.

검은 화면이 뜨고 메뉴가 나옵니다.

```text
1. Dry-run
2. Sample
3. Full Inbox
4. Full Sent
5. 종료
```

### 먼저 1번 Dry-run

`1`을 입력하고 Enter를 누릅니다.

그러면 EML 폴더 경로를 물어봅니다.

이 문서의 권장 구조대로라면 받은메일 경로는 보통 아래처럼 됩니다.

```text
C:\Users\내이름\Downloads\gmail-eml-import\받은편지
```

보낸메일 경로는 보통 아래처럼 됩니다.

```text
C:\Users\내이름\Downloads\gmail-eml-import\보낸편지
```

먼저 받은메일 폴더인 `받은편지`를 넣으세요.

Dry-run은 Gmail에 아무것도 넣지 않습니다.

그냥 “메일 파일이 몇 개인지, 날짜/첨부/중복 문제가 있는지” 검사만 합니다.

### 그 다음 2번 Sample

`2`를 입력하고 Enter를 누릅니다.

다시 EML 폴더 경로를 붙여넣습니다.

이 단계에서는 Gmail에 딱 10개만 넣습니다.

처음 실행하면 브라우저가 열리고 Google 로그인/승인 화면이 나옵니다.

여기서는 반드시 본인 새 Gmail 계정인지 확인하고 직접 승인하세요.

### Gmail에서 확인

Gmail을 열고 왼쪽 라벨에서 아래 라벨을 찾습니다.

```text
Inbox-eml import
```

확인할 것:

- 메일 10개가 보이는지
- 날짜가 옛날 날짜로 들어갔는지
- 첨부파일이 열리는지
- 한글 제목이 깨지지 않는지
- 한글 첨부파일명이 깨지지 않는지
- Gmail 검색으로 찾을 수 있는지

문제가 있으면 여기서 멈추세요.

문제 없으면 전체 import로 갑니다.

## 4. 전체 받은메일 import

받은메일 폴더인 `받은편지`를 넣을 때는 메뉴에서 `3`을 누릅니다.

화면에서 정말 진행할지 물어보면:

```text
YES
```

라고 입력해야 시작됩니다.

받은메일은 Gmail에서 아래 라벨로 보입니다.

```text
Inbox-eml import
```

## 5. 전체 보낸메일 import

보낸메일 폴더인 `보낸편지`를 넣을 때는 메뉴에서 `4`를 누릅니다.

화면에서 정말 진행할지 물어보면:

```text
YES
```

라고 입력해야 시작됩니다.

보낸메일은 Gmail에서 아래 라벨로 보입니다.

```text
Sent-eml import
```

## 절대 보내면 안 되는 파일

문제가 생겨서 도움을 요청할 때도 아래 파일은 보내지 마세요.

```text
credentials.json
token.json
```

특히 `token.json`은 내 Gmail 접근 토큰입니다.

## 도움 요청할 때 보내도 되는 파일

아래 파일들은 보내도 됩니다.

```text
logs\dry_run_report.csv
logs\failed.csv
logs\final_missing_imports.csv
```
