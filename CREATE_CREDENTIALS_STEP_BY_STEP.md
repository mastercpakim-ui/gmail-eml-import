# credentials.json 만들기: 화면별 안내

이 문서는 Google Cloud에서 Gmail API용 `credentials.json`을 만드는 절차입니다.

어려우면 중간 화면을 캡처해서 도움을 요청하세요.

## 최종 목표

아래 파일을 다운로드해서:

```text
credentials.json
```

`run_import_wizard.bat`와 같은 폴더에 넣는 것입니다.

## 1. Google Cloud Console 접속

아래 주소를 엽니다.

```text
https://console.cloud.google.com/
```

Google 로그인이 나오면, 메일을 가져올 새 Gmail / Google Workspace 계정으로 로그인합니다.

## 2. 프로젝트 만들기

화면 위쪽의 프로젝트 선택 버튼을 누릅니다.

새 프로젝트를 만듭니다.

프로젝트 이름은 예를 들어 이렇게 씁니다.

```text
gmail-eml-import
```

이미 비슷한 프로젝트가 있으면 그대로 써도 됩니다.

프로젝트 이름이 `gmail-eml-export`처럼 되어 있어도 괜찮습니다.

중요한 것은 프로젝트 이름이 아니라 Gmail API와 OAuth 파일입니다.

## 3. Gmail API 사용 설정

Google Cloud 상단 검색창에 아래를 입력합니다.

```text
Gmail API
```

`Gmail API`를 클릭합니다.

버튼이 보이면 `사용 설정` 또는 `Enable`을 누릅니다.

이미 사용 설정되어 있으면 그대로 다음 단계로 갑니다.

## 4. 사용자 인증 정보 만들기

왼쪽 메뉴에서:

```text
API 및 서비스
```

아래로 들어갑니다.

```text
사용자 인증 정보
```

또는 상단/본문에 있는:

```text
사용자 인증 정보 만들기
```

를 누릅니다.

## 5. 어떤 API를 사용하나요?

`어떤 API를 사용 중이신가요?` 같은 화면이 나오면:

```text
Gmail API
```

를 선택합니다.

## 6. 액세스할 데이터는 무엇인가요?

여기서 매우 중요합니다.

아래 둘 중 하나를 고르는 화면이 나옵니다.

```text
사용자 데이터
애플리케이션 데이터
```

반드시:

```text
사용자 데이터
```

를 선택합니다.

`애플리케이션 데이터`가 아닙니다.

그 다음 `다음`을 누릅니다.

## 7. OAuth 동의 화면

앱 정보를 묻는 화면이 나옵니다.

대충 아래처럼 입력하면 됩니다.

```text
앱 이름: gmail-eml-import
사용자 지원 이메일: 본인 이메일 선택
개발자 연락처 이메일: 본인 이메일 입력
```

저장 또는 다음을 누릅니다.

## 8. 범위 추가

`범위` 또는 `Scopes` 화면이 나옵니다.

목록에서 찾기 어려우면 아래쪽의:

```text
직접 범위 추가
```

를 찾습니다.

거기에 아래 값을 그대로 붙여넣습니다.

```text
https://www.googleapis.com/auth/gmail.modify
```

그 다음:

```text
표에 추가
```

또는:

```text
Add to table
```

을 누릅니다.

추가되면 다음으로 갑니다.

## 9. OAuth 클라이언트 ID 만들기

`OAuth 클라이언트 ID` 단계가 나옵니다.

`애플리케이션 유형` 드롭다운을 누릅니다.

반드시 아래를 선택합니다.

```text
데스크톱 앱
```

이름은 이렇게 입력합니다.

```text
gmail-eml-import
```

그 다음 `완료` 또는 `만들기`를 누릅니다.

## 10. JSON 다운로드

완료 후 JSON 다운로드 버튼이 나옵니다.

다운로드합니다.

처음 파일 이름은 보통 이런 식입니다.

```text
client_secret_어쩌고저쩌고.apps.googleusercontent.com.json
```

파일 이름을 아래처럼 바꿉니다.

```text
credentials.json
```

## 11. 파일 위치

`credentials.json`을 `run_import_wizard.bat`와 같은 폴더에 넣습니다.

폴더 안이 대략 이렇게 보여야 합니다.

```text
credentials.json
import_eml.py
requirements.txt
run_import_wizard.bat
README.md
```

이제 `run_import_wizard.bat`를 더블클릭하면 됩니다.

## 자주 막히는 화면

### 로드할 수 없습니다

Google Cloud에서 가끔 나옵니다.

`재시도`를 누릅니다.

그래도 안 되면 새로고침하거나 다시 Google Cloud Console로 들어갑니다.

### 사용자 데이터 / 애플리케이션 데이터

반드시 `사용자 데이터`입니다.

### Desktop app이 어디 있나요?

`애플리케이션 유형` 드롭다운 안에 있습니다.

### OAuth 승인 화면이 무섭습니다

이 도구가 Gmail 메일함에 EML을 넣으려면 Gmail 수정 권한이 필요합니다.

본인이 만든 로컬 도구이고, 본인 PC에서만 실행합니다.

단, 계정이 본인 새 Gmail 계정인지 꼭 확인하고 승인하세요.
