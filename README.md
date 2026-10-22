# 누리살핌 공개 탐지 지식

공공 웹사이트 불법광고 탐지 도구 누리살핌의 .skills/SKILL.md, 선언형 규칙, 광고·정상 회귀 사례를 함께 관리한다.
이 저장소는 탐지 지식만 담는다. 앱 전체 소스, API 키, 실제 사이트 수집물과 개인정보는 포함하지 않는다.

`관찰 → 실제 근거 확인 → 광고 사례 + 정상 반례 → PR/CI → 해시 고정 팩 업데이트 → 재검사`

| 버전 | 지침 | 누적 회귀 사례 | 차이 |
|---|---:|---:|---|
| 1.0.0 | 필수 4종 | 7 | 기본 팩 |
| 1.1.0 | 필수 4종 + ZERO_WIDTH | 12 | 보이지 않는 문자 복원 활성화, 광고 2 + 정상 3 사례 추가 |

## 사용

Python 3.13 이상에서 의존성 설치 없이 실행한다.
```text
python tools/pack.py
python tools/pack.py --check
```

누리살핌 앱의 .env에 SKILLS_URL과 SKILLS_SHA256을 설정한다. URL은 raw.githubusercontent.com/HosooJeong/nurisalpim-detection-skills/<40자리 커밋>/releases/1.1.0/detection.skills.json 형태로 고정하고, 파일 SHA-256은 manifest.json에서 가져온다.
주 화면의 지식 업데이트 링크에서 검증·적용한다. 실행 중인 검사는 팩을 바꾸지 않는다. 이전 정상 사례를 망가뜨리는 업데이트는 거부한다.

## 보장 범위

사례는 모두 합성이다. 공개 업로드 자체가 새로운 탐지 알고리즘이나 실사이트 성능 향상을 증명하지 않는다.
ZERO_WIDTH는 내장된 검증기의 활성화이며, 필수 result.json에는 넣지 않고 result_extra.json의 ETC/ZERO_WIDTH로 분리한다.
실행 코드·모델·사이트를 고정한 전후 비교로 이 팩의 실제 효과를 확인한다. 모델은 재학습하지 않는다.
tools/normalize.py는 누리살핌의 회귀용 정규화 참조 구현이다. DOM 검증·실사이트 성능 검증은 앱에서 별도로 수행한다.
현재 악성 패턴은 제한된 예제다. 임의 새 기법에 대한 코드 검증기를 자동 생성하지 않는다.

기여 방법은 CONTRIBUTING.md를 따른다. 원저작 팩·예제·도구는 MIT 라이선스로 제공한다.
