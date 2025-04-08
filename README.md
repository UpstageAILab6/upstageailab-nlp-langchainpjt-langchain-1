[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/5BS4k7bR)
# **LangChain 프로젝트** *(예시)*

LangChain를 활용하여, 실제로 패스트캠퍼스/Upstage AI Lab 6기 수강 과정 문서 기반 Q&A 시스템을 구축하는 프로젝트입니다.  
RAG(Retrieval-Augmented Generation) 구조를 바탕으로 문서 검색 및 응답 시스템을 구현하였습니다.

- **프로젝트 기간:** 2025.04.02 ~ 2025.04.08  
- **주제:** LangChain 기반 문서 검색 + Q&A 자동화 시스템  

---

# **팀원 소개**

| 이름      | 역할             | GitHub                | 담당 기능                                         |
|-----------|------------------|------------------------|--------------------------------------------------|
| **강태화** |  팀장 | [GitHub 링크](#)| 아키텍쳐 구조 설게, 휴가/출석대장 작성법과 과정시간표 데이터 수집 및 임베딩, Langchain 통합 |
| **정혜린** |  팀원 | [https://github.com/jhyerin31](#) | 온라인 강의 데이터 수집 및 임베딩, LCEL 구현  |
| **정인복** |  팀원 | [GitHub 링크](#)| 내일배움카드 관련 법령 데이터 수집 및 임베딩, 프롬프트 출력 요약 |
| **진우재** |  팀원 | [GitHub 링크](#)|            |
| **박진신** |  팀원 | [GitHub 링크](#)|               |

---

# **파이프라인 워크플로우**

LangChain 기반 패스트캠퍼스/Upstage AI Lab 6기 과정 전반적인 QA 시스템의 구축 및 운영을 위한 파이프라인입니다.

## **1. 비즈니스 문제 정의**
- 다양한 소스로 존재하는 여러 문서들을 필요 시 마다 찾는것에 대한 번거로움을 느낌 
- 부트캠프 수강과 관련된 QA Engine 생성으로 업무 효율성 증대 기대

## **2. 데이터 수집 및 전처리**
1. **데이터 수집**
   - 휴가/출석 대장 작성법 html, 내일배움카드 관련 법령 PDF, 강의 시간표 csv, 과정 스케줄.xlsx 문서 데이터 수집 
2. **문서 파싱 및 전처리**
   - 각 데이터 소스에 따라 LangChain의 DocumentLoader 사용
   - Chunking, Text Cleaning
3. **임베딩 및 벡터화**
   - OpenAI / HuggingFace Embedding 모델 사용
   - FAISS / Chroma  활용한 벡터 DB 구축

## **3. LLM 및 RAG 파이프라인 구성**
- LangChain의 RetrievalQA 모듈 활용
- Chain 구성: Embedding → Retriever → LLM(응답)
- LLM: OpenAI GPT-4 / UpstageChat 등 선택 가능

---

## **프로젝트 실행 방법**

본 프로젝트는 웹 서비스 형태로 배포하지 않아도 되며,  
**로컬 환경 또는 클라우드 인스턴스에서 터미널 기반으로 실행** 가능합니다.

```bash
# 1. 프로젝트 클론
git clone https://github.com/your-org/langchain-qa-project.git
cd langchain-qa-project

# 2. 가상환경 설정 및 패키지 설치
python -m venv QAEngine
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 환경 변수 설정
export OPENAI_API_KEY=your-api-key
export UPSTAGE_API_KEY=your-api-key
export HUGGINGFACEHUB_API_KEY=your-api-key

# 4. 실행
python main.py
```

---

## **활용 장비 및 사용 툴**

### **활용 장비**
- **서버:** AWS EC2 (m5.large), S3, ECR
- **개발 환경:** Ubuntu 22.04, Python 3.10+
- **테스트 환경:** NVIDIA V100 GPU 서버 (Lambda Labs 등)

### **협업 툴**
- **소스 관리:** GitHub
- **커뮤니케이션:** Slack

### **사용 도구**
- **LLM 통합:** LangChain, OpenAI API, HuggingFace

---

## **기대 효과 및 향후 계획**
- 문서 기반 질문 응답 자동화로 고객 응대 시간 절감
- 사내 문서 검색 정확도 및 사용성 향상
- 향후 다양한 도메인 문서(QA, 정책, 교육자료 등)에 확장 적용 예정

---
## **강사님 피드백 및 프로젝트 회고**

프로젝트 진행 중 담당 강사님과의 피드백 세션을 통해 얻은 주요 인사이트는 다음과 같습니다.

### 📌 **1차 피드백 (2025.04.02)**
- **LangChain Retriever 선택 기준에 대한 설명 및 근거**  
  → 다양한 Chunking size에 대해 비교 분석하고, 왜 특정 벡터 DB(FAISS, Chroma)를 선택했는지 근거 추가.

### 📌 **2차 피드백 (2025.04.03)**
- **Routing 적용해보기**  

### 📌 **3차 피드백 (2025.04.04)**
- **프롬프트 설계 최적화 피드백**  
  → 단순 질문-응답 프롬프트가 아닌, 문맥 유지형 시스템 메시지 설계 제안.
