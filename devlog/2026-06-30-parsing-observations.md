\# PDF Parsing Observations



\## English



\## 1. Purpose of This Note



This note summarizes the issues discovered during the first PDF parsing experiments for the JEDEC Local RAG project.



The goal of this experiment was not to build a perfect parser immediately.  

The goal was to observe how technical PDF pages break when parsed with a basic PDF parser such as `pdfplumber`.



\## 2. Key Discovery



A PDF page that looks readable to humans is not always readable to a PDF parser.



In several test cases, the page visually contained text, tables, figures, and captions, but the extracted result did not preserve the original structure correctly.



This means that a RAG system for technical documents should not blindly trust extracted text.



\## 3. PDF Preprocessing Matters



The same visible PDF page produced different parsing results depending on how the PDF was split or exported.



For example:



\- A PDF split with a web-based PDF splitter

\- A PDF split using the print-to-PDF function



These two files may look identical to humans, but they can have different internal PDF structures.



Possible differences include:



\- Text layer preservation

\- Image-based rendering

\- Font objects

\- Vector graphics

\- Crop box or media box settings

\- Table line objects

\- Page rotation metadata



Therefore, PDF preprocessing should be treated as part of the RAG pipeline.



The system should record how a PDF was prepared before parsing.



\## 4. Visible Text Is Not Always Extractable Text



One important issue was that some pages visually contained text, but `pdfplumber.extract\_text()` returned an empty string.



This means that the page may be image-based, scanned, or internally represented in a way that the parser cannot extract as text.



Important lesson:



```text

No extracted text does not always mean no information.

```



A page with zero extracted text may still contain important information in the rendered page image.



\## 5. Figure Reference vs Figure Caption



The initial page classifier incorrectly classified some normal text pages as diagram pages.



The reason was that the text contained phrases such as:



```text

Figure 6 illustrates ...

Figure 7 the usage of ...

```



These are figure references inside normal prose, not standalone figure captions.



A real figure caption usually looks like:



```text

Figure 7 — Initialization Sequence with Channel Disable

```



Important lesson:



```text

Mentioning a figure is not the same as being a figure page.

```



The classifier must distinguish between:



\- Figure references in prose

\- Standalone figure captions

\- Actual diagram-heavy pages



\## 6. Single-Label Page Classification Is Too Limited



The early classifier tried to force each page into one label:



```text

normal\_text

table\_page

diagram\_page

unknown

```



This turned out to be too simple.



Some JEDEC pages contain both explanatory text and important diagrams.  

For example, timing sequence pages may include:



\- Paragraph text

\- Signal names

\- Timing parameters

\- Figure captions

\- Timing diagrams



Such pages are not purely text pages and not purely diagram pages.



A better approach is to use multiple content tags instead of a single page type.



Example:



```json

{

&#x20; "primary\_type": "mixed",

&#x20; "content\_tags": \["text", "figure", "timing\_diagram"],

&#x20; "routing": {

&#x20;   "use\_text\_index": true,

&#x20;   "use\_table\_index": false,

&#x20;   "save\_page\_image": true,

&#x20;   "requires\_visual\_context": true,

&#x20;   "use\_vision\_fallback": true

&#x20; }

}

```



\## 7. Table Extraction Is Unstable



Some pages contained tables that were visually clear in the PDF, but the extracted Markdown tables were imperfect.



Observed problems:



\- Merged cells were not preserved correctly.

\- Row and column relationships were sometimes broken.

\- Watermark text was mixed into table cells.

\- Long descriptions inside table cells were flattened.

\- Some tables were split into multiple incorrect fragments.



This is dangerous for JEDEC-style documents because many critical values are stored in tables.



A table extraction result should not be trusted blindly.



\## 8. Diagrams and Timing Figures Need Visual Context



Timing diagrams and layout figures cannot be fully represented by plain extracted text.



The parser may extract signal names and timing labels, but it cannot reliably preserve:



\- Signal waveform shape

\- Horizontal timing relationships

\- Arrows

\- Visual alignment

\- Highlighted regions

\- Spatial relationships



Therefore, pages with timing diagrams or layout figures should save the original page image for future multimodal processing.



\## 9. Updated Design Decision



The parser should not only extract text and tables.



It should also generate page-level metadata for routing.



The updated parsing pipeline should do the following:



```text

PDF page

&#x20; ↓

Extract text

Extract tables

Save page image

Analyze content signals

&#x20; ↓

Generate metadata

&#x20; ↓

Route to text index, table index, or vision fallback

```



The new parser should store:



\- Extracted text

\- Extracted tables

\- Page image path

\- Content tags

\- Primary page type

\- Routing flags

\- Reasons for classification



\## 10. Routing Strategy



The page analysis should decide how each page will be used later.



Example routing fields:



```json

{

&#x20; "use\_text\_index": true,

&#x20; "use\_table\_index": true,

&#x20; "save\_page\_image": true,

&#x20; "requires\_visual\_context": true,

&#x20; "use\_vision\_fallback": true,

&#x20; "safe\_for\_text\_chunking": true

}

```



This is more flexible than forcing each page into only one category.



\## 11. Important Project Direction Change



The project started as a text/table-aware local RAG system.



However, the parsing experiment showed that JEDEC-style technical PDFs often contain visual information that text extraction alone cannot preserve.



Therefore, the project should be designed as:



```text

Text RAG

\+ Table-aware RAG

\+ Page image preservation

\+ Future multimodal fallback

```



This does not mean every page must be processed by a vision model.



Instead:



\- Text-heavy questions should use text retrieval.

\- Table-heavy questions should use table-aware retrieval.

\- Diagram-heavy questions should retrieve the relevant page and use the saved page image as visual context.



\## 12. Current Decision



The next parser version should:



\- Save page images for all pages.

\- Analyze pages with multiple content tags.

\- Avoid relying on a single page type.

\- Keep text chunks when extractable text exists.

\- Keep table chunks when table extraction is reliable.

\- Mark visually important pages for future vision fallback.

\- Record parsing problems in metadata instead of hiding them.



\## 13. Lessons Learned



The quality of a RAG answer depends heavily on PDF preprocessing and parsing quality.



The pipeline is not simply:



```text

PDF → Text → Embedding → LLM

```



For technical PDFs, the pipeline should be closer to:



```text

PDF

→ preprocessing check

→ text/table/image extraction

→ page analysis

→ metadata routing

→ retrieval

→ answer generation with citations

```



The main lesson from this experiment is:



```text

Do not trust extracted text blindly.

Preserve the original page image.

Record uncertainty in metadata.

```



\---



\## Korean Translation



\## 1. 이 문서의 목적



이 문서는 JEDEC Local RAG 프로젝트의 첫 PDF 파싱 실험에서 발견한 문제들을 정리하기 위한 문서다.



이번 실험의 목적은 처음부터 완벽한 파서를 만드는 것이 아니었다.  

목적은 `pdfplumber`와 같은 기본 PDF 파서를 사용할 때 기술 PDF 페이지가 어떻게 깨지는지 관찰하는 것이었다.



\## 2. 핵심 발견



사람 눈에 읽을 수 있는 PDF 페이지가 항상 PDF 파서에게도 읽을 수 있는 것은 아니다.



여러 테스트에서 페이지는 시각적으로 텍스트, 표, 그림, 캡션을 포함하고 있었지만, 추출 결과는 원래 구조를 제대로 보존하지 못했다.



즉, 기술 문서용 RAG 시스템은 추출된 텍스트를 무조건 신뢰하면 안 된다.



\## 3. PDF 전처리 방식이 중요하다



겉으로 동일하게 보이는 PDF 페이지라도, 어떤 방식으로 분할하거나 내보냈는지에 따라 파싱 결과가 달라졌다.



예를 들면:



\- 웹 기반 PDF 분할 도구로 나눈 PDF

\- PDF 인쇄 기능을 이용해 만든 PDF



이 두 파일은 사람 눈에는 같아 보일 수 있지만, 내부 PDF 구조는 다를 수 있다.



가능한 차이는 다음과 같다.



\- 텍스트 레이어 보존 여부

\- 이미지 기반 렌더링 여부

\- 폰트 객체

\- 벡터 그래픽

\- crop box 또는 media box 설정

\- 표 선 객체

\- 페이지 회전 메타데이터



따라서 PDF 전처리 방식도 RAG 파이프라인의 일부로 다뤄야 한다.



시스템은 PDF가 어떤 방식으로 준비되었는지 기록해야 한다.



\## 4. 보이는 텍스트가 항상 추출 가능한 텍스트는 아니다



중요한 문제 중 하나는, 어떤 페이지는 눈으로 보면 텍스트가 있지만 `pdfplumber.extract\_text()` 결과가 빈 문자열로 나왔다는 점이다.



이는 해당 페이지가 이미지 기반이거나, 스캔된 페이지이거나, 파서가 텍스트로 추출할 수 없는 내부 구조로 표현되어 있을 수 있음을 의미한다.



중요한 교훈:



```text

추출된 텍스트가 없다는 것이 정보가 없다는 뜻은 아니다.

```



추출 텍스트가 0인 페이지도 렌더링된 페이지 이미지 안에는 중요한 정보를 포함할 수 있다.



\## 5. Figure 참조와 Figure 캡션은 다르다



초기 페이지 classifier는 일부 정상 본문 페이지를 diagram page로 잘못 분류했다.



원인은 본문 안에 다음과 같은 문장이 있었기 때문이다.



```text

Figure 6 illustrates ...

Figure 7 the usage of ...

```



이 문장들은 일반 본문 안에서 Figure를 참조하는 문장이지, 독립된 Figure 캡션이 아니다.



진짜 Figure 캡션은 보통 다음과 같은 형태다.



```text

Figure 7 — Initialization Sequence with Channel Disable

```



중요한 교훈:



```text

Figure를 언급하는 것과 Figure 페이지인 것은 다르다.

```



classifier는 다음을 구분해야 한다.



\- 본문 안의 Figure 참조

\- 독립된 Figure 캡션

\- 실제 diagram 중심 페이지



\## 6. 단일 라벨 페이지 분류는 한계가 있다



초기 classifier는 각 페이지를 하나의 라벨로 강제 분류하려고 했다.



```text

normal\_text

table\_page

diagram\_page

unknown

```



하지만 이 방식은 너무 단순했다.



일부 JEDEC 페이지는 설명 본문과 중요한 diagram을 동시에 포함한다.  

예를 들어 timing sequence 페이지는 다음을 포함할 수 있다.



\- 문단 텍스트

\- 신호 이름

\- timing parameter

\- Figure 캡션

\- timing diagram



이런 페이지는 순수한 text page도 아니고 순수한 diagram page도 아니다.



따라서 하나의 page type 대신 여러 content tag를 사용하는 방식이 더 적절하다.



예시:



```json

{

&#x20; "primary\_type": "mixed",

&#x20; "content\_tags": \["text", "figure", "timing\_diagram"],

&#x20; "routing": {

&#x20;   "use\_text\_index": true,

&#x20;   "use\_table\_index": false,

&#x20;   "save\_page\_image": true,

&#x20;   "requires\_visual\_context": true,

&#x20;   "use\_vision\_fallback": true

&#x20; }

}

```



\## 7. 표 추출은 불안정하다



일부 페이지에는 PDF에서 시각적으로 명확한 표가 있었지만, 추출된 Markdown table은 완벽하지 않았다.



관찰된 문제는 다음과 같다.



\- 병합 셀이 제대로 보존되지 않았다.

\- 행과 열의 관계가 깨지는 경우가 있었다.

\- 워터마크 텍스트가 표 셀 안에 섞였다.

\- 표 셀 안의 긴 설명이 평탄화되었다.

\- 일부 표는 여러 개의 잘못된 조각으로 나뉘었다.



JEDEC 스타일 문서에서는 중요한 값들이 표에 많이 저장되어 있기 때문에 이는 위험하다.



표 추출 결과는 무조건 신뢰하면 안 된다.



\## 8. Diagram과 timing figure에는 시각적 맥락이 필요하다



Timing diagram과 layout figure는 단순 추출 텍스트만으로 완전히 표현할 수 없다.



파서는 신호 이름과 timing label 일부는 추출할 수 있지만, 다음 요소를 안정적으로 보존하지 못한다.



\- 신호 파형 모양

\- 수평 timing 관계

\- 화살표

\- 시각적 정렬

\- 강조 영역

\- 공간적 관계



따라서 timing diagram이나 layout figure가 있는 페이지는 나중의 멀티모달 처리를 위해 원본 페이지 이미지를 저장해야 한다.



\## 9. 변경된 설계 결정



파서는 텍스트와 표만 추출해서는 안 된다.



페이지 단위 metadata를 생성해서 이후 처리 경로를 결정해야 한다.



변경된 파싱 파이프라인은 다음과 같아야 한다.



```text

PDF page

&#x20; ↓

Extract text

Extract tables

Save page image

Analyze content signals

&#x20; ↓

Generate metadata

&#x20; ↓

Route to text index, table index, or vision fallback

```



새 parser는 다음 정보를 저장해야 한다.



\- 추출된 텍스트

\- 추출된 표

\- 페이지 이미지 경로

\- content tags

\- primary page type

\- routing flags

\- 분류 이유



\## 10. Routing 전략



페이지 분석 결과는 각 페이지가 나중에 어떻게 사용될지 결정해야 한다.



예시 routing field:



```json

{

&#x20; "use\_text\_index": true,

&#x20; "use\_table\_index": true,

&#x20; "save\_page\_image": true,

&#x20; "requires\_visual\_context": true,

&#x20; "use\_vision\_fallback": true,

&#x20; "safe\_for\_text\_chunking": true

}

```



이 방식은 각 페이지를 하나의 카테고리로 강제하는 것보다 훨씬 유연하다.



\## 11. 중요한 프로젝트 방향 변경



이 프로젝트는 처음에 text/table-aware local RAG 시스템으로 시작했다.



하지만 파싱 실험 결과, JEDEC 스타일 기술 PDF는 텍스트 추출만으로 보존할 수 없는 시각 정보가 많다는 것을 확인했다.



따라서 프로젝트는 다음 구조로 설계되어야 한다.



```text

Text RAG

\+ Table-aware RAG

\+ Page image preservation

\+ Future multimodal fallback

```



이 말은 모든 페이지를 vision model로 처리해야 한다는 뜻은 아니다.



대신:



\- 텍스트 중심 질문은 text retrieval을 사용한다.

\- 표 중심 질문은 table-aware retrieval을 사용한다.

\- diagram 중심 질문은 관련 페이지를 찾은 뒤 저장된 페이지 이미지를 시각적 맥락으로 사용한다.



\## 12. 현재 결정



다음 parser 버전은 다음을 수행해야 한다.



\- 모든 페이지 이미지를 저장한다.

\- 페이지를 여러 content tag로 분석한다.

\- 단일 page type에 의존하지 않는다.

\- 추출 가능한 텍스트가 있으면 text chunk로 보존한다.

\- 표 추출이 신뢰 가능하면 table chunk로 보존한다.

\- 시각적으로 중요한 페이지는 future vision fallback 대상으로 표시한다.

\- 파싱 문제를 숨기지 말고 metadata에 기록한다.



\## 13. 배운 점



RAG 답변 품질은 PDF 전처리와 파싱 품질에 크게 의존한다.



파이프라인은 단순히 다음과 같지 않다.



```text

PDF → Text → Embedding → LLM

```



기술 PDF에서는 다음에 더 가깝다.



```text

PDF

→ preprocessing check

→ text/table/image extraction

→ page analysis

→ metadata routing

→ retrieval

→ answer generation with citations

```



이번 실험의 핵심 교훈은 다음과 같다.



```text

추출 텍스트를 맹신하지 말 것.

원본 페이지 이미지를 보존할 것.

불확실성을 metadata에 기록할 것.

```

