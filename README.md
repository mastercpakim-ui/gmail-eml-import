# Gmail EML 가져오기 도구

백업받은 `.eml` 파일을 새 Gmail / Google Workspace Gmail 계정으로 가져오는 도구입니다.

개발을 모르는 사람도 쓰도록 만든 버전입니다.

## 제일 짧은 사용법

1. 이 GitHub 페이지에서 초록색 `Code` 버튼을 누릅니다.
2. `Download ZIP`을 누릅니다.
3. ZIP 파일을 풉니다.
4. 폴더 안에 `credentials.json` 파일을 넣습니다.
5. `run_import_wizard.bat`를 더블클릭합니다.
6. 화면 메뉴에서 순서대로 실행합니다.

권장 순서:

```text
1. Dry-run
2. Sample
Gmail에서 10개 확인
3. Full Inbox
4. Full Sent
```

## 이 도구가 하는 일

- 원본 EML 파일을 읽어서 Gmail API로 가져옵니다.
- SMTP를 쓰지 않습니다.
- Gmail API `users.messages.import`를 우선 사용합니다.
- 원본 메일 날짜와 첨부파일을 최대한 보존합니다.
- 원본 EML 파일은 수정, 삭제, 이동, 이름 변경하지 않습니다.
- 중복 파일은 SHA256 기준으로 다시 넣지 않습니다.
- 깨진 Cafe24 헤더는 import 직전에만 임시 보정합니다.

## 준비물

### 1. EML 백업 폴더

예:

```text
C:\Users\내이름\email-archive\eml
```

받은메일과 보낸메일 폴더가 따로 있으면 각각 따로 실행하면 됩니다.

### 2. credentials.json

Google Cloud에서 Gmail API용 Desktop OAuth 파일을 받아야 합니다.

파일 이름은 반드시 아래처럼 바꿉니다.

```text
credentials.json
```

그리고 `run_import_wizard.bat`와 같은 폴더에 넣습니다.

중요:

- `credentials.json`은 GitHub에 올리지 마세요.
- `token.json`은 절대 남에게 보내지 마세요.
- `token.json`은 실행 후 자동으로 생기는 본인 Gmail 접근 토큰입니다.

## Google Cloud에서 credentials.json 만들기

Google Cloud 화면은 자주 바뀌어서, 막히면 도움을 요청하세요.

대략 순서:

1. Google Cloud Console 접속
2. 프로젝트 생성
3. Gmail API 사용 설정
4. OAuth 동의 화면 생성
5. OAuth Client ID 생성
6. Application type은 `Desktop app`
7. JSON 다운로드
8. 파일 이름을 `credentials.json`으로 변경
9. 이 도구 폴더에 넣기

## 실행 화면에서 뭘 고르면 되나요?

`run_import_wizard.bat`를 더블클릭하면 메뉴가 나옵니다.

### 1. Dry-run

Gmail에 아무것도 넣지 않고 EML 파일을 검사합니다.

먼저 반드시 이것부터 하세요.

### 2. Sample

Gmail에 10개만 테스트로 넣습니다.

브라우저에서 Google 로그인/승인 화면이 뜨면 본인 계정이 맞는지 확인하고 직접 승인하세요.

Gmail에서 확인할 것:

- `Inbox-eml import` 라벨이 생겼는지
- 메일 10개가 보이는지
- 날짜가 맞는지
- 첨부파일이 열리는지
- 한글 제목, 본문, 파일명이 깨지지 않는지
- Gmail 검색으로 찾을 수 있는지

### 3. Full Inbox

받은메일 EML 폴더 전체를 `Inbox-eml import` 라벨로 가져옵니다.

### 4. Full Sent

보낸메일 EML 폴더 전체를 `Sent-eml import` 라벨로 가져옵니다.

## 문제가 생기면

아래 파일을 보내면 확인할 수 있습니다.

```text
logs\dry_run_report.csv
logs\failed.csv
logs\final_missing_imports.csv
```

절대 보내면 안 되는 파일:

```text
token.json
credentials.json
```

## 보안 메모

이 도구는 로컬 PC에서 실행됩니다.

메일 데이터와 OAuth 토큰을 외부 서버로 보내지 않습니다.
