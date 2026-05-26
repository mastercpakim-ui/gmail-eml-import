# credentials.json 만들기

이 파일은 Gmail API 접근을 위해 필요합니다.

혼자 하기 어렵다면, 개발을 아는 사람에게 이 문서를 보여주세요.

## 목표

최종적으로 아래 파일 하나를 만드는 것입니다.

```text
credentials.json
```

이 파일은 `run_import_wizard.bat`와 같은 폴더에 둡니다.

## 순서

1. Google Cloud Console에 접속합니다.
2. 새 프로젝트를 만듭니다.
3. `Gmail API`를 검색해서 사용 설정합니다.
4. OAuth 동의 화면을 만듭니다.
5. 사용자 데이터 접근을 선택합니다.
6. 범위에는 아래 값을 추가합니다.

```text
https://www.googleapis.com/auth/gmail.modify
```

7. OAuth 클라이언트 ID를 만듭니다.
8. 애플리케이션 유형은 `Desktop app`을 선택합니다.
9. JSON 파일을 다운로드합니다.
10. 파일 이름을 `credentials.json`으로 바꿉니다.

## 주의

`token.json`은 실행 후 생깁니다. 이 파일은 본인 Gmail 계정 접근 토큰이므로 절대 공유하지 마세요.
