## 📝 Description

This PR introduces **IP and privacy safeguards** for agents, extends the **VAT/IGIC agent and tasks** with a structured 4-step methodology, and enhances the **RAG system** to automatically detect, download, and process PDF documents from official links in `dossier_fuentes.json`. Agents are explicitly instructed never to request or collect personal information (including IP addresses). The VAT consultation flow is aligned with a legal-operational methodology (identify scope → tax classification → RAG retrieval → legal reasoning). The RAG pipeline gains comprehensive official links for all normativas and intelligent PDF detection with fallback mechanisms for BOE, EUR-Lex, and other government sources.

## 🎯 What does this PR do?

- [x] Feature addition
- [x] Bug fix (privacy: prevent agents from requesting IP/personal data)
- [x] Documentation update
- [x] Code refactoring
- [ ] Other: **\*\*\_\*\***

## 🔍 Changes Made

### 🔒 IP & Privacy

- **Explicit privacy instructions** in both **IVA Consulta** and **SAP** agents (`agents.yaml`):
  - Agents **never request, collect, or ask for** personal information: IP addresses, email, phone numbers, physical addresses, names, or any other identifying information
  - Consultation is provided solely from the question asked, without requiring user data
- **Control questions** (`data/processed/control_questions.txt`): Removed language/locale tags from question text (e.g. "(French)", "(German)") to reduce metadata exposure and support privacy-aware evaluation
- **Excluded-info questions** updated accordingly

### 🤖 Agent & Task Enhancements (VAT Deep Methodology)

- **IVA Consulta agent** (`agents/crewai/agents.yaml`): Extended with:
  - **4-step methodology**: (1) Identify scope (territory: IVA/IGIC/EU), (2) Tax classification, (3) RAG retrieval with filters (`nivel`, `impuesto`, `conceptos_clave`, `tipo_norma`), (4) Legal reasoning with norm hierarchy
  - Explicit **knowledge base** list (LIVA, IGIC, SII, VeriFactu, TicketBAI, Crea y Crece, EU directives, dossier_fuentes)
  - **Critical errors to avoid** (e.g. never mix IVA/IGIC, never invent articles, correct 8th/13th Directive use)
  - **Response format** for complex queries (marco normativo, análisis, obligaciones formales, conclusión)
- **VAT consultation task** (`agents/crewai/tasks.yaml`): Rewritten to mirror the 4-step flow, RAG filters, validation checks, and structured expected output (simple vs complex query format)
- **New** `agents/crewai/instrunctions_vat_deep.txt`: Internal methodology and reasoning rules for VAT/IGIC (scope, classification, retrieval, legal reasoning, norm prioritization)
- **Backup files** added: `agents_backup.yaml`, `tasks_backup.yaml` for previous agent/task definitions

### 🔗 Official Links Addition

#### Enhanced `dossier_fuentes.json`

- **Added `enlaces_oficiales` field to all 22 normativas** in the JSON file
- **43 official links added** covering:
  - **BOE (Boletín Oficial del Estado)** links for Spanish regulations
  - **EUR-Lex** links for European Union directives and regulations
  - **AEAT (Agencia Tributaria)** portal links for tax forms and guides
  - **Canarias Government** links for IGIC regulations
  - **Euskadi/TicketBAI** links for Basque Country tax system
- **Link types include**:
  - Original act links (`act.php`)
  - Consolidated version links (`doc.php`)
  - Portal and guide pages
  - Model forms and technical specifications

### 🤖 PDF Detection & Processing Enhancement

#### Intelligent PDF Detection (`_is_pdf_url`)

- **Multi-layered PDF detection**:
  - File extension check (`.pdf`)
  - Content-Type header verification (`application/pdf`)
  - PDF magic number verification (`%PDF` in first bytes)
  - Final URL check after redirects
- **User-Agent headers** added to avoid bot blocking
- **Handles redirects** properly to detect PDFs behind redirect chains

#### PDF Download Functionality (`_download_pdf`)

- **Downloads PDFs from URLs** to temporary files
- **Validates PDF content** before saving (magic number check)
- **Streaming download** for large files
- **Proper cleanup** of temporary files after processing
- **Error handling** with informative messages

#### URL Type Detection (`_detect_url_type`)

- **Automatic detection** of PDF vs web page URLs
- **Special handling** for BOE and EUR-Lex URLs (many redirect to PDFs)
- **Non-destructive checking** (doesn't consume stream)

### 🔄 Enhanced JSON Processing

#### Extended `validate_web_page_links`

- **Supports `dossier_fuentes.json` structure**:
  - Detects `{"normativa": [{"enlaces_oficiales": [...]}]}` format
  - Extracts all links from `enlaces_oficiales` arrays
  - Automatically detects PDF vs web page for each link
  - Maintains backward compatibility with legacy format
- **Enhanced validation** with detailed error reporting
- **Metadata extraction** (normativa ID and title) for better tracking

#### Improved `process_json_file`

- **Dual processing mode**:
  - PDFs: Download → Process → Cleanup
  - Web pages: Direct processing with PDF fallback
- **Automatic PDF fallback**: If web page processing fails, attempts to download as PDF
- **Comprehensive error handling** with retry logic
- **Metadata tracking** for processed URLs

### 🛠️ Web Page Processing Improvements

#### Enhanced `add_document` in `ragtool.py`

- **Direct URL support** using `RagTool.add()` for web pages
- **Fallback to `WebBaseLoader`** if direct method fails
- **Proper error handling** for different URL types
- **Support for both local files and URLs**

### 📦 Dependencies

- **Added `requests>=2.31.0`** to `requirements.txt` for HTTP requests and PDF downloads

### 🧹 Code Quality

- **Removed JSON comments** that caused parsing errors (lines 106, 164, 242)
- **Improved error messages** with context
- **Better logging** for debugging URL processing issues
- **Code organization** with clear separation of concerns

## 📁 Files Modified/Created

**IP & privacy / agents & tasks**
- ✅ `agents/crewai/agents.yaml` - Privacy instructions for IVA Consulta & SAP; IVA Consulta extended with 4-step methodology and knowledge base
- ✅ `agents/crewai/tasks.yaml` - VAT consultation task rewritten with 4-step flow, RAG filters, validation checks
- ✅ `agents/crewai/instrunctions_vat_deep.txt` - New methodology and reasoning rules for VAT/IGIC
- ✅ `agents/crewai/agents_backup.yaml`, `tasks_backup.yaml` - Backups of previous definitions
- ✅ `data/processed/control_questions.txt`, `control_questions_randomized.txt` - Privacy-aware question set (language tags removed)
- ✅ `data/processed/excluded_info_questions.txt` - Updated exclusions

**RAG & data**
- ✅ `data/raw/dossier_fuentes.json` - Added `enlaces_oficiales` to all 22 normativas, removed invalid JSON comments
- ✅ `data/raw_txt/dossier_fuentes_old.json` - Backup/legacy version of sources
- ✅ `data/processed/enlaces_normativas.md` - Added
- ✅ `data/processed/processed_files.json` - Updated
- ✅ `agents/rag/files_ragtool.py` - PDF detection, download, and processing
- ✅ `agents/rag/ragtool.py` - Enhanced `add_document` for web page URLs
- ✅ `agents/utils/config.py` - Embedding model set to `gemini-embedding-001`

**Docs & deps**
- ✅ `docs/RagTool_files_management.md` - Extended RAG file management documentation
- ✅ `docs/Ragtool_Api.md` - Extended RAG API documentation
- ✅ `requirements.txt` - Added `requests>=2.31.0`

## 🧪 Testing

- [x] I have tested this locally
- [x] Agent privacy instructions: agents do not request IP or personal data
- [x] VAT task and agent methodology align (4-step flow, RAG filters)
- [x] JSON file validates correctly (no syntax errors)
- [x] PDF detection works for various URL patterns
- [x] Fallback mechanism tested with BOE URLs
- [x] Error handling verified for failed downloads
- [x] Temporary file cleanup confirmed
- [x] No breaking changes to existing functionality

## 📸 Screenshots (if applicable)

N/A

## 📋 Checklist

- [x] Code follows project style guidelines
- [x] Self-review completed
- [x] Code is commented where necessary
- [x] Documentation updated (if needed)
- [x] Error handling implemented
- [x] Resource cleanup (temporary files) implemented
- [x] Backward compatibility maintained

## 🚀 Deployment Notes

- **New dependency**: `requests>=2.31.0` must be installed
- **Config**: Embedding model set to `gemini-embedding-001` in `agents/utils/config.py` (if using default RAG config)
- **No new environment variables** required
- **Database rebuild recommended**: Process `dossier_fuentes.json` to add all official links to the knowledge base
- **Network access required**: System needs internet access to download PDFs from official sources

## 📞 Additional Notes

**Privacy & compliance**
- Agents (IVA Consulta and SAP) are explicitly instructed **not** to request or collect IP addresses or other personal data; consultation is based only on the question.
- Control and evaluation question sets are adjusted to avoid unnecessary metadata in text (supporting privacy-aware evaluation).

**Agent & methodology**
- VAT consultation follows a **structured 4-step methodology** (scope → classification → RAG retrieval with metadata filters → legal reasoning) so answers stay territory- and norm-consistent (IVA vs IGIC, EU directives, etc.).
- Task and agent definitions are aligned with `instrunctions_vat_deep.txt` for consistent behavior and easier maintenance.

**RAG & knowledge base**
- **Automatic PDF processing**: No manual download needed for official documents; intelligent detection and fallback for BOE/EUR-Lex style URLs.
- **Comprehensive coverage**: All 22 normativas have official links; the RAG pipeline can download, validate, and index PDFs from these sources.
- Handles **redirects**, **bot protection** (User-Agent), **streaming** for large files, and **error recovery** with PDF fallback when web page processing fails.

Together, these changes improve privacy posture, consultation consistency, and the ability to build and maintain the legal knowledge base from official sources.
