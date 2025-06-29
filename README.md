# Gold Inventory App - Refactored Version

이 문서는 원본 Gold Inventory App과 이 브랜치(Refactored Version)에서 적용된 주요 변경점과 개선사항을 설명합니다.

---

## 1. 프로젝트 구조 변경

**원본**
```
├── db.py
├── gui.py
├── main.py
├── models.py
├── repository.py
├── requirements.txt
└── gold_data.db
```

**리팩터링 후**
```
├── DB/                  # 데이터베이스 파일 보관
│   └── gold_data.db
├── src/                 # 애플리케이션 소스 코드
│   ├── __init__.py
│   ├── config.py        # 설정 및 경로 관리
│   ├── db.py            # DB 초기화 및 마이그레이션
│   ├── models.py        # SQLAlchemy 모델 정의
│   ├── repository.py    # Optional: Repository 레이어
│   ├── gui.py           # PyQt5 UI
│   ├── main.py          # 애플리케이션 진입점
│   └── icons/           # UI 아이콘
├── requirements.txt     # 의존성 목록
└── README.md            # 프로젝트 설명
``` 

- `src/` 디렉터리에 모든 `.py` 파일을 이동하여 모듈화 및 패키지화  
- `DB/` 디렉터리에 데이터베이스 파일을 이동하여 코드와 분리  
- `requirements.txt` 및 `README.md`는 최상위에 유지  

---

## 2. 데이터베이스 레이어 최적화

- **SQLAlchemy ORM 도입**: 커넥션 풀링, 세션 관리, ORM 쿼리 캐싱을 통해 성능 및 안정성 향상  
- **자동 스키마 마이그레이션**: `init_db()`에서 `PRAGMA table_info`로 기존 컬럼을 확인하고, 누락된 컬럼만 `ALTER TABLE`로 추가  
- **CRUD 통합**: `DataManager` 클래스에 add/update/delete/get/get_all 메서드를 통합하여 중복 코드 제거  

---

## 3. 선언적 모델 & 타입 힌트

- `models.py`에 `Product` 모델을 SQLAlchemy `declarative_base` 방식으로 정의  
- GUI에서 사용하는 모든 필드(`size`, `total_qb_qty`, `labor_cost1`, `labor_cost2`, `set_no` 등)를 모델에 추가  
- 함수 반환 타입에 `Optional[Product]`, `List[Product]` 등 타입 힌트 적용  

---

## 4. 선택적 레이어: Repository Pattern

- `repository.py`에 `ProductRepository` 클래스 추가  
- `DataManager` 대신 또는 함께 사용하여 테스트 용이성 및 백엔드 교체 유연성 증가  

---

## 5. GUI 개선사항

- **편집 기능 수정**: `get_product()`로 단일 제품 로드, 변경된 필드만 딕셔너리로 추출하여 `update_product` 호출  
- **코드 가독성**: 복잡한 한 줄 코드를 명확한 블록으로 분리, 주석 추가  

---

## 6. 설정 및 실행 방법

1. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```
2. 애플리케이션 실행 (프로젝트 루트에서):
   ```bash
   python -m src.main
   ```
3. 최초 실행 시 자동으로 DB 마이그레이션 수행  

---

## 7. 성능 향상 요약

- **커넥션 풀링**: DB 연결/해제 비용 감소  
- **ORM 쿼리 캐싱**: SQLAlchemy가 SQL 컴파일 결과를 재사용  
- **DB 레벨 필터링/정렬**: `WHERE`, `ORDER BY` 활용으로 Python 레벨 처리 비용 절감  
- **세션 범위 관리**: 메서드 단위 세션 사용으로 락 경합 및 메모리 누수 최소화  

---

*이 README는 원본 버전과의 차이점을 명확히 보여주고, 리팩터링된 코드의 주요 의도를 설명합니다.*  
