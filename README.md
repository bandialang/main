# Persistent Login WebView Android App

`https://grpmb.sehan.ac.kr/mobile/#/login` 로그인 상태를 앱에서 최대한 유지하도록 만든 Android(WebView) 샘플입니다.

## 적용된 로그인 유지 방식

- `CookieManager`로 쿠키 수용 (`setAcceptCookie`, `setAcceptThirdPartyCookies`)
- 페이지 로딩 완료 시점과 `onPause()` 시점에 쿠키를 저장
- 저장한 쿠키를 앱 시작 시 `SharedPreferences`에서 복원해 재로그인 빈도 감소
- `domStorageEnabled`, `javaScriptEnabled` 등 로그인 페이지 호환 옵션 활성화

## 대상 URL

- 기본 로드 URL: `https://grpmb.sehan.ac.kr/mobile/#/login`

## 파일 9개 다운로드 방법

아래 2가지 중 편한 방법으로 받으시면 됩니다.

### 방법 1) Git으로 한 번에 받기 (추천)

```bash
git clone <저장소주소>
cd <저장소폴더>
```

### 방법 2) ZIP으로 받기

- GitHub 저장소 페이지에서 **Code > Download ZIP** 클릭
- 압축 해제하면 9개 파일이 모두 들어있습니다.

### 방법 3) 현재 폴더를 직접 ZIP으로 만들기

```bash
zip -r persistent-login-app.zip .
```

생성된 `persistent-login-app.zip` 파일 하나만 전달하면 됩니다.

## APK 만드는 방법 (로컬 PC)

이 저장소는 소스코드 프로젝트라서, APK는 아래 명령으로 직접 생성할 수 있습니다.

```bash
./gradlew assembleDebug
```

생성 위치:

- `app/build/outputs/apk/debug/app-debug.apk`

## 실행 방법

1. Android Studio에서 프로젝트 열기
2. Gradle Sync 실행
3. 앱 실행 후 최초 1회 로그인
4. 앱 재실행 시 로그인 유지 여부 확인

## 한계/주의사항

- 서버에서 매우 짧은 세션 만료 정책을 쓰면 자동 로그아웃될 수 있습니다.
- 계정 보안 정책(2FA, 단말 바인딩, IP 정책)에 따라 로그인 유지가 제한될 수 있습니다.
- 앱 데이터 삭제 시 저장된 쿠키도 함께 삭제됩니다.
