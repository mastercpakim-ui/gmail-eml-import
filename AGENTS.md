# 작업 안내 (AI 코딩 에이전트용)

이 repo는 백업 `.eml` 파일을 Gmail API로 가져오는 도구입니다.
사용자는 개발을 모를 수 있습니다. 이 파일을 읽는 에이전트(Claude Code, Codex 등)는 아래 절차를 그대로, 순서대로 진행하세요.

## 진행 순서

1. `pip install -r requirements.txt` 로 라이브러리 설치
2. 사용자에게 EML 백업 폴더 경로를 확인한다.
3. 그 폴더 안에 `받은편지`(받은메일), `보낸편지`(보낸메일) 폴더가 있는지 확인한다.
   - 나뉘어 있지 않으면, 사용자에게 받은/보낸 폴더로 나눠 달라고 안내한다.
4. `credentials.json`이 repo 폴더에 있는지 확인한다.
   - 없으면 `CREATE_CREDENTIALS_STEP_BY_STEP.md`를 보고 만들도록 안내한다.
5. dry-run으로 먼저 검사한다 (Gmail에 아무것도 넣지 않음).

   ```bash
   python import_eml.py --mode dry-run --source-dir "<받은편지 경로>"
   ```

6. 받은편지에서 sample 10개만 import한다.

   ```bash
   python import_eml.py --mode sample --source-dir "<받은편지 경로>" --limit 10 --label "받은메일" --repair-malformed-headers
   ```

7. 사용자가 Gmail에서 10개를 직접 확인할 때까지 멈춘다.
   (날짜, 첨부파일, 한글 제목·본문·파일명, 검색 가능 여부)
8. 사용자가 OK하면 받은편지 전체를 import한다.

   ```bash
   python import_eml.py --mode full --source-dir "<받은편지 경로>" --label "받은메일" --repair-malformed-headers --confirm-full-import
   ```

9. 이어서 보낸편지 전체를 import한다. (`--source-dir`을 보낸편지 경로로, `--label`을 "보낸메일"로)

## 반드시 지킬 것

- 원본 EML 파일은 수정·삭제·이동·이름변경 금지.
- sample 확인 전에는 절대 full import 하지 않는다.
- full import는 `--confirm-full-import` 플래그가 있어야 동작한다.
- OAuth 승인 화면은 사용자가 직접 본인 계정을 확인하고 승인하게 한다.
- `credentials.json`, `token.json`은 절대 외부로 보내거나 출력하지 않는다.

## 라벨 규칙

- `받은편지` 폴더 → Gmail 라벨 "받은메일"
- `보낸편지` 폴더 → Gmail 라벨 "보낸메일"
