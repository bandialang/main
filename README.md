# Persistent Login WebView Android App

`https://grpmb.sehan.ac.kr/mobile/#/login` 로그인 상태를 앱에서 최대한 유지하도록 만든 Android(WebView) 샘플입니다.

## 적용된 로그인 유지 방식

- `CookieManager`로 쿠키 수용 (`setAcceptCookie`, `setAcceptThirdPartyCookies`)
- 페이지 로딩 완료 시점과 `onPause()` 시점에 쿠키를 저장
- 저장한 쿠키를 앱 시작 시 `SharedPreferences`에서 복원해 재로그인 빈도 감소
- `domStorageEnabled`, `javaScriptEnabled` 등 로그인 페이지 호환 옵션 활성화

## 대상 URL

- 기본 로드 URL: `https://grpmb.sehan.ac.kr/mobile/#/login`

## 진짜 쉬운 APK 만들기 (Android Studio 버튼만 사용)

아래 순서대로만 하면 됩니다.

1. **Android Studio 설치**
   - Android Studio(최신 버전) 설치
   - 처음 실행 시 SDK 설치까지 완료

2. **프로젝트 열기**
   - Android Studio 실행
   - `Open` 클릭
   - 이 프로젝트 폴더(`build.gradle.kts` 파일이 있는 폴더) 선택

3. **동기화 완료 기다리기**
   - 하단 상태바에 `Gradle project sync finished`가 뜰 때까지 대기
   - 오류가 나면 인터넷 연결 상태 확인 후 `Sync Now` 다시 클릭

4. **APK 빌드 버튼 클릭**
   - 상단 메뉴에서 `Build > Build APK(s)` 클릭

5. **APK 위치 열기**
   - 빌드 완료 후 오른쪽 아래 알림에서 `locate` 클릭
   - 또는 직접 경로로 이동:
   - `app/build/outputs/apk/debug/app-debug.apk`

6. **폰에 설치**
   - `app-debug.apk`를 휴대폰으로 복사
   - 설치가 막히면 “알 수 없는 앱 설치 허용”을 켜고 설치

---

## 터미널로 APK 만들기 (선택)

Android Studio 대신 명령어로 만들려면:

```bash
gradle assembleDebug
```

생성 위치:

- `app/build/outputs/apk/debug/app-debug.apk`

> 참고: 환경에 따라 `gradle` 대신 `./gradlew`를 쓰기도 하지만,
> 이 저장소에는 Gradle Wrapper 파일(`gradlew`)이 없어서 기본 `gradle` 명령을 사용했습니다.

## 파일 9개 다운로드 방법

아래 방법 중 편한 걸 쓰세요.

### 방법 1) Git으로 한 번에 받기 (추천)

```bash
git clone <저장소주소>
cd <저장소폴더>
```

### 방법 2) ZIP으로 받기

- GitHub 저장소 페이지에서 **Code > Download ZIP** 클릭
- 압축 해제하면 파일이 모두 들어있습니다.

### 방법 3) 현재 폴더를 직접 ZIP으로 만들기

```bash
zip -r persistent-login-app.zip .
```

생성된 `persistent-login-app.zip` 파일 하나만 전달하면 됩니다.

## 실행 방법

1. Android Studio에서 프로젝트 열기
2. Gradle Sync 실행
3. 앱 실행 후 최초 1회 로그인
4. 앱 재실행 시 로그인 유지 여부 확인

## 한계/주의사항

- 서버에서 매우 짧은 세션 만료 정책을 쓰면 자동 로그아웃될 수 있습니다.
- 계정 보안 정책(2FA, 단말 바인딩, IP 정책)에 따라 로그인 유지가 제한될 수 있습니다.
- 앱 데이터 삭제 시 저장된 쿠키도 함께 삭제됩니다.
