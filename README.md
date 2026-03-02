# Daily Paper Alert to KakaoTalk (Me)

웹툰/애니메이션 + 텍스트마이닝 관련 신규 논문을 매일 수집해 카카오톡 `나에게 보내기`로 전달하는 MVP입니다.

## 1) 준비

1. Python 3.10+ 설치
2. 카카오 디벨로퍼스 앱 생성
3. 플랫폼/Redirect URI 등록 (`KAKAO_REDIRECT_URI`)
4. 동의항목에서 `talk_message` 사용 설정

## 2) 설치

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env`에 `KAKAO_REST_API_KEY`, `KAKAO_REDIRECT_URI` 입력.  
플랫폼 키에서 클라이언트 시크릿 사용 중이면 `KAKAO_CLIENT_SECRET`도 입력.

## 3) 최초 토큰 발급

```powershell
python kakao_oauth_helper.py
```

출력된 `access_token`, `refresh_token` 값을 `.env`에 넣습니다.

## 4) 수동 실행 테스트

```powershell
python paper_alert.py
```

정상 동작하면 카카오톡 `나와의 채팅`에 논문 목록이 도착합니다.

## 5) 매일 자동 실행 (Windows 작업 스케줄러)

아래 예시는 매일 오전 9시 실행:

```powershell
schtasks /Create /SC DAILY /ST 09:00 /TN "DailyPaperAlertKakao" /TR "powershell -NoProfile -ExecutionPolicy Bypass -Command \"cd 'C:\Users\ymhong\Desktop\2026.03.02_thesis'; .\.venv\Scripts\python.exe .\paper_alert.py\""
```

## 해외 논문 / SCI 유사 필터

- 해외 논문 소스:
  - `arXiv` (영문 preprint)
  - `Crossref` (국제 학술지 메타데이터)
- 한국어 논문 강화:
  - `Crossref`에서 한국어(`ko`) 또는 한글 제목/초록을 별도 수집
  - `KCI_LOOKBACK_DAYS`, `MAX_KCI_ITEMS`로 한국어 후보를 더 넓게 탐색
- `STRICT_JOURNAL_FILTER=true`로 두면 `journal_whitelist.txt` 저널명에 포함된 저널만(단, arXiv는 예외) 전송합니다.
- 진짜 SCI 인덱스 판별은 WoS 라이선스 데이터가 필요해서, MVP에서는 저널 화이트리스트 기반으로 대체합니다.

## 커스터마이즈

- `KEYWORDS` 환경변수(콤마 구분)로 키워드 교체 가능
- `LOOKBACK_DAYS`, `MAX_ITEMS_PER_SOURCE`로 수집량 조절 가능
- `MAX_SEND_COUNT`로 하루 전송 개수 조절 가능

## Kakao 버튼 관련

- 카카오 `기본 템플릿`은 `link` 필드가 필수라 `자세히 보기` 영역을 API로 완전 제거할 수 없습니다.
- 대신 본문에 DOI 링크를 직접 포함해 버튼 없이도 논문 링크를 바로 열 수 있게 구성했습니다.
