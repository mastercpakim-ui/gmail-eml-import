# Gmail EML Import

백업받은 `.eml` 파일을 Gmail로 가져오는 도구입니다. (Claude Code 전용)

원본 메일의 날짜·첨부파일·발신자/수신자·본문을 그대로 보존하며,
이미 가져온 메일은 자동으로 건너뜁니다.

## 준비

EML 백업을 아래처럼 두 폴더로 나눠 둡니다.

```text
EML백업/
├─ 받은편지/   ← 받은메일 .eml 파일
└─ 보낸편지/   ← 보낸메일 .eml 파일
```

메일 백업은 보통 이미 받은/보낸이 나뉘어 있습니다.
섞여 있으면 폴더 2개로 나눠 주세요.

## 사용법

Claude Code에 아래 문장을 붙여넣으세요. (경로는 본인 것으로 바꾸세요.)

```text
https://github.com/mastercpakim-ui/gmail-eml-import
이 repo 읽고 내 백업 메일을 Gmail로 옮겨줘.
백업 경로는 C:\Users\내이름\EML백업 이고, 받은편지/보낸편지로 나뉘어 있어.
credentials.json은 내가 만들게.
```

그러면 Claude Code가 알아서 진행합니다.

1. 코드와 라이브러리 준비
2. credentials.json 만드는 법 안내
3. dry-run (Gmail에 넣지 않고 검사)
4. 받은편지 10개만 테스트 import
5. 사용자가 Gmail에서 직접 확인할 때까지 멈춤
6. OK하면 받은편지 전체 → 보낸편지 전체 import

## 직접 할 일 하나: credentials.json

Gmail 접근을 허가하는 파일입니다.
[CREATE_CREDENTIALS_STEP_BY_STEP.md](CREATE_CREDENTIALS_STEP_BY_STEP.md) 를 보고 만드세요.
(Claude Code가 이 과정도 함께 안내합니다.)

## 안전

- 원본 EML 파일은 수정·삭제·이동·이름변경하지 않습니다.
- 같은 메일은 SHA256 기준으로 중복 import하지 않습니다.
- `credentials.json`, `token.json`은 절대 남에게 보내지 마세요.
