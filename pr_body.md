## 📝 Description

This PR enhances the RAG system to automatically detect, download, and process PDF documents from official links in the `dossier_fuentes.json` file. It adds comprehensive official links to all normativas (regulations) and implements intelligent PDF detection with fallback mechanisms for URLs that redirect to PDFs. This significantly improves the knowledge base by enabling automatic processing of official legal documents from BOE, EUR-Lex, and other government sources.

## 🎯 What does this PR do?

- [x] Feature addition
- [ ] Bug fix
- [ ] Documentation update
- [x] Code refactoring
- [ ] Other: **\*\*\_\*\***

## 🔍 Changes Made

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

- ✅ `data/raw/dossier_fuentes.json` - Added `enlaces_oficiales` to all 22 normativas, removed invalid JSON comments
- ✅ `agents/rag/files_ragtool.py` - Added PDF detection, download, and processing functionality
- ✅ `agents/rag/ragtool.py` - Enhanced `add_document` to handle web page URLs properly
- ✅ `requirements.txt` - Added `requests>=2.31.0` dependency

## 🧪 Testing

- [x] I have tested this locally
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
- **No environment variables** or configuration changes required
- **Database rebuild recommended**: Process `dossier_fuentes.json` to add all official links to the knowledge base
- **Network access required**: System needs internet access to download PDFs from official sources

## 📞 Additional Notes

This PR significantly enhances the RAG system's capability to process official legal documents:

- **Automatic PDF processing**: No manual download needed for official documents
- **Intelligent detection**: System automatically identifies PDFs even when URLs don't have `.pdf` extension
- **Robust fallback**: If web page processing fails, automatically tries PDF download
- **Comprehensive coverage**: All 22 normativas now have official links for easy reference and processing
- **Better knowledge base**: Official legal documents can now be automatically indexed and searched

The implementation handles common challenges:

- **BOE URLs** that redirect to PDFs without `.pdf` in the URL
- **EUR-Lex** links that may serve PDFs or HTML
- **Bot protection** using proper User-Agent headers
- **Large files** using streaming downloads
- **Error recovery** with automatic fallback mechanisms

This enables the RAG system to automatically build a comprehensive knowledge base from official sources, significantly improving the quality and accuracy of legal information retrieval.
