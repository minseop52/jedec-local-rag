# JEDEC-local-rag

Local RAG system for studying JEDEC-style technical PDF documents with table-aware retrieval and citation-grounded answers.



\## 0. Notice

This project does not aim to fine-tune or memorize a single JEDEC document; it aims to build a reusable local RAG pipeline that can parse, index, retrieve, and answer from JEDEC-style technical PDFs.



\## 1. Project Motivation

Semiconductor technology standard documents, such as JEDEC specifications, possess distinct characteristics that set them apart from general documents:



&#x20;- Large Document Size: They are voluminous and contain a high page count.

&#x20;- Abundance of Acronyms and Parameters: They feature heavy use of technical abbreviations and timing parameters (e.g., DQ, DQS, VDD, tRCD, tRAS, tCK).

&#x20;- Critical Importance of Tables and Numerical Data: Numerical accuracy within structured formats is paramount.

&#x20;- Complex Document Structure: They contain intricate layouts including timing diagrams, tables, and extensive cross-sectional references.

&#x20;- High Risk of Error: A single misinterpreted numerical value can lead to incorrect technical decisions.



When using existing LLM-based tools (such as GPT, Gemini, or NotebookLM) to study these large-scale technical documents, several critical limitations arise:



&#x20;- Degraded Context Retrieval: As document size increases, the models often fail to reliably ingest and reflect the entire content.

&#x20;- Structural Breakdown: Tables and matrix structures frequently break down, leading to misinterpretation of row-and-column relationships. 

&#x20;- **Hallucinations: The system may generate unfounded answers regarding specific values, units, or timing parameters.**

&#x20;- Lack of Traceability: It is difficult to trace which page, table, or section of the document the generated answer is based on.

&#x20;- **Data Privacy Constraints: Proprietary or confidential corporate documents cannot be uploaded to external cloud-based AI services due to security policies.**



\## 2. Project Goal

The ultimate objective of this project is as follows:



> To build a local RAG system where a user uploads a technical PDF document within a local environment; the system then parses the document, stores tables and text in a searchable format, and answers user queries accompanied by explicit source citations from the document.



In achieving this goal, the project will heavily focus on the following key requirements:



&#x20;- Local-First Execution: Fully operational within a local environment to ensure data privacy.

&#x20;- Advanced PDF Parsing: Robust extraction of complex document layouts.

&#x20;- Preservation of Tables and Numerical Data: Maintaining the integrity of tabular structures and exact values.

&#x20;- Optimized Domain Search: Enhancing retrieval performance specifically for acronyms and domain-specific technical terminology.

&#x20;- Hybrid Retrieval: Combining lexical search (BM25) and semantic search (Dense Embedding) to maximize accuracy.

&#x20;- Granular Citation: Providing precise citations (including page numbers, sections, and table IDs) for every generated answer.

&#x20;- Strict Grounding: Implementing strict guardrails so the system admits when it does not know the answer, rather than guessing or hallucinating info missing from the document.



\## 3. Key Problems

\### 3.1 Large Technical PDF Problem

Large-scale technical documents are difficult to process using standard LLM upload methods. The model may fail to precisely retain or retrieve information across the entire document, often missing details on specific pages or within critical tables.





\### 3.2 Table Parsing Problem

Tables carry the most critical information in JEDEC specifications. For instance, timing parameters and voltage specifications are predominantly presented in tabular formats.



Using conventional PDF text extraction tools often leads to the following issues:



&#x20;- Shuffled Rows and Columns: Structural alignment is lost during extraction.

&#x20;- Missing Column Headers: Contextual labels for data points disappear.

&#x20;- Broken Merged Cells: Multi-row or multi-column spans fail to render properly.

&#x20;- Ambiguous Unit Associations: The relationship between numerical values and their corresponding units becomes unclear.

&#x20;- Mismatched Specifications: Min, Typ, and Max values are incorrectly mapped to their parameters.

&#x20;- To prevent these issues, this project places a strong emphasis on table-to-markdown conversion, table metadata enrichment, and table-aware retrieval.



\### 3.3 Acronym and Domain Term Problem

Semiconductor documents are dense with acronyms and domain-specific terminology that standard language models may fail to contextualize effectively.



Examples include:



&#x20;- DQ (Data Input/Output)

&#x20;- DQS (Data Strobe)

&#x20;- VDD (Supply Voltage)

&#x20;- VSS (Ground Voltage)

&#x20;- tRCD (RAS to CAS Delay)

&#x20;- tRAS (Row Active Time)

&#x20;- tCK (Clock Cycle Time)



Because semantic-only dense retrieval can overlook these precise keyword matches, this system implements a hybrid retrieval architecture that combines BM25-based lexical search with dense embedding search.



\### 3.4 Confidential Document Problem

Internal corporate specs, NDA-protected documents, and proprietary technical assets cannot be uploaded to external cloud-based AI services. Consequently, this project is strictly architected to execute document indexing, retrieval, and response generation entirely within a secured local environment.





\## 4. Planned Architecture

&#x09;text

PDF Document

&#x20;    ↓

PDF Parsing

&#x20;    ↓

Text / Table / Metadata Extraction

&#x20;    ↓

Chunking

&#x20;    ↓

Embedding

&#x20;    ↓

Vector DB + BM25 Index

&#x20;    ↓

Hybrid Retrieval

&#x20;    ↓

Reranking

&#x20;    ↓

Local LLM

&#x20;    ↓

Citation-grounded Answer


## 5. Tech Stack

Planned technologies:

- Python
- pdfplumber / Marker
- Sentence-Transformers
- BGE-M3 or other local embedding models
- ChromaDB / FAISS
- BM25
- Ollama
- Qwen / Llama local models
- Streamlit or FastAPI

## 6. Current Status

Project initialized.

- [x] GitHub repository created
- [x] Project directory structure created
- [x] `.gitignore` configured for private PDF files
- [x] Initial README written
- [ ] PDF parsing prototype
- [ ] Chunking pipeline
- [ ] Embedding pipeline
- [ ] Vector database integration
- [ ] Hybrid retrieval
- [ ] Local LLM integration
- [ ] Evaluation set
- [ ] Local UI

## 7. Repository Policy

This repository does not include copyrighted JEDEC documents, confidential documents, or private company documents.

Private PDFs should be stored only in local directories such as:

```text
data/sample_private/
data/raw/
```






\## 0. Notice

이 프로젝트는 특정 JEDEC 문서 하나를 파인튜닝하거나 외우게 만드는 것이 아니라, JEDEC과 같은 기술 PDF를 로컬에서 파싱, 인덱싱, 검색하고 근거 기반으로 답변할 수 있는 재사용 가능한 RAG 파이프라인을 구축하는 것을 목표로 한다. 



JEDEC 스타일의 기술 PDF 문서를 연구하기 위한 로컬 RAG 시스템으로, 표 기반 검색 및 인용 기반 답변을 제공.



\## 1. Project Motivation

JEDEC와 같은 반도체 기술 표준 문서는 일반적인 문서와 다르게 다음과 같은 특징을 가진다.



\- 문서 크기가 크고 페이지 수가 많다.

\- 약어와 파라미터가 많다.  

&#x20; 예: `DQ`, `DQS`, `VDD`, `tRCD`, `tRAS`, `tCK`

\- 표와 수치 데이터가 매우 중요하다.

\- timing diagram, table, section reference 등 문서 구조가 복잡하다.

\- 잘못된 수치 하나가 잘못된 기술적 판단으로 이어질 수 있다.



기존의 GPT, Gemini, NotebookLM과 같은 언어모델 기반 도구에 대용량 기술 문서를 업로드해서 공부할 경우 다음과 같은 한계가 있었다.



\- 문서 크기가 커질수록 전체 내용을 안정적으로 반영하지 못하는 경우가 있다.

\- 표와 테이블 구조가 깨져서 행과 열의 관계를 잘못 이해하는 경우가 있다.

\- 특정 수치, 단위, timing parameter에 대해 근거 없는 답변을 생성할 수 있다.

\- 답변이 문서의 어느 페이지, 어느 표, 어느 섹션을 근거로 하는지 추적하기 어렵다.

\- 기밀 문서나 회사 내부 문서는 외부 AI 서비스에 업로드할 수 없다.



따라서 본 프로젝트는 JEDEC 스타일의 기술 PDF 문서를 로컬 환경에서 처리하고, 문서 내부 근거에 기반해 답변하는 RAG 시스템을 구현하는 것을 목표로 한다.



\## 2. Project Goal



이 프로젝트의 최종 목표는 다음과 같다.



> 사용자가 로컬 환경에서 기술 PDF 문서를 업로드하면, 시스템이 문서를 파싱하고, 표와 텍스트를 검색 가능한 형태로 저장한 뒤, 질문에 대해 문서 근거와 함께 답변하는 로컬 RAG 시스템을 구축한다.



특히 다음 요소를 중요하게 다룬다.



\- 로컬 환경에서 동작

\- PDF 문서 파싱

\- 표와 수치 데이터 보존

\- 약어 및 기술 용어 검색 성능 개선

\- BM25와 dense embedding을 결합한 hybrid retrieval

\- 답변에 page, section, table 등의 citation 제공

\- 문서에 없는 내용은 추측하지 않고 모른다고 답변

## 3. Key Problems

\### 3.1 Large Technical PDF Problem

대용량 기술 문서는 일반적인 LLM 업로드 방식으로 처리하기 어렵다.  

모델이 문서 전체를 정확히 기억하거나 검색하지 못할 수 있으며, 특정 페이지나 표의 내용을 놓칠 수 있다.



\### 3.2 Table Parsing Problem

JEDEC 문서에서 표는 핵심 정보다.  

예를 들어 timing parameter나 voltage specification은 대부분 표 형태로 제공된다.



일반적인 PDF text extraction을 사용하면 다음 문제가 발생할 수 있다.



\- 행과 열이 뒤섞임

\- column header가 사라짐

\- merged cell이 깨짐

\- 수치와 단위의 관계가 불명확해짐

\- min / typ / max 값이 잘못 연결됨



따라서 본 프로젝트에서는 table-to-markdown, table metadata, table-aware retrieval을 중요하게 다룬다.



\### 3.3 Acronym and Domain Term Problem

반도체 문서에는 일반 언어모델이 잘 모르는 약어와 도메인 용어가 많다.



예:



\- `DQ`

\- `DQS`

\- `VDD`

\- `VSS`

\- `tRCD`

\- `tRAS`

\- `tCK`



이러한 용어는 의미 기반 검색만으로는 놓칠 수 있으므로, BM25 기반 lexical search와 dense embedding search를 함께 사용하는 hybrid retrieval 구조를 사용한다.



\### 3.4 Confidential Document Problem



회사 내부 문서, NDA 문서, 기밀 기술 문서는 외부 AI 서비스에 업로드할 수 없다.  

따라서 본 프로젝트는 로컬 PC에서 문서 인덱싱, 검색, 답변 생성을 수행하는 구조를 지향한다.



\## 4. Planned Architecture

&#x09;text

PDF Document

&#x20;   ↓

PDF Parsing

&#x20;   ↓

Text / Table / Metadata Extraction

&#x20;   ↓

Chunking

&#x20;   ↓

Embedding

&#x20;   ↓

Vector DB + BM25 Index

&#x20;   ↓

Hybrid Retrieval

&#x20;   ↓

Reranking

&#x20;   ↓

Local LLM

&#x20;   ↓

Citation-grounded Answer

## 5. Tech Stack
계획된 기술 스택:

 - Python
 - pdfplumber / Marker
 - Sentence-Transformers
 - BGE-M3 또는 기타 로컬 임베딩 모델
 - ChromaDB / FAISS
 - BM25
 - Ollama
 - Qwen / Llama 로컬 모델
 - Streamlit 또는 FastAPI

## 6. Current Status
프로젝트 초기화 완료.

- [x] GitHub 저장소 생성
- [x] 프로젝트 디렉토리 구조 생성
- [x] 개인 PDF 파일을 위한 .gitignore 설정
- [x] 초기 README 작성
- [ ] PDF 파싱 프로토타입 개발
- [ ] 청킹(Chunking) 파이프라인 구축
- [ ] 임베딩 파이프라인 구축
- [ ] 벡터 데이터베이스 연동
- [ ] 하이브리드 검색(Hybrid Retrieval) 구현
- [ ] 로컬 LLM 연동
- [ ] 평가 데이터셋(Evaluation set) 구축
- [ ] 로컬 UI 개발

## 7. Repository Policy
본 저장소에는 저작권이 있는 JEDEC 문서, 기밀 문서 또는 회사 내부 문서를 포함하지 않습니다.

개인 기술 PDF 문서는 오직 다음과 같은 로컬 디렉토리에만 저장해야 합니다:

```text
data/sample_private/
data/raw/
```
