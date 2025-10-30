# Quick Reference: Manual Content Addition

## 🚀 Quick Start

1. **Copy content** from blocked websites into template files in `data/templates/`
2. **Save completed files** in `data/raw/` directory
3. **Run processing**: `./scripts/process_manual_content.sh`

## 📁 File Locations

- **Templates**: `data/templates/` (use these as starting points)
- **Raw content**: `data/raw/` (place your completed files here)
- **Processed data**: `data/processed/` (automatically generated)

## 🔗 Blocked URLs to Process

| URL                                                                                                                          | Template File                         | Save As                               |
| ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- | ------------------------------------- |
| https://www.sap.com/products/technology-platform.html                                                                        | `sap-btp-overview.txt`                | `sap-btp-overview.txt`                |
| https://www.taxtech500.com/featured-articles/from-banking-apps-to-sap-btp-the-new-era-of-embedded-tax                        | `taxtech500-embedded-tax.txt`         | `taxtech500-embedded-tax.txt`         |
| https://sapinsider.org/blogs/embracing-sap-btp-and-avalara-solutions-during-s4-migration-to-meet-tax-compliance-mandates     | `sapinsider-btp-avalara.txt`          | `sapinsider-btp-avalara.txt`          |
| https://www.sap.com/swiss/products/erp/partners/meridian-global-vat-services-limited-arco-tax-determination-for-sap-btp.html | `meridian-arco-tax-determination.txt` | `meridian-arco-tax-determination.txt` |

## ⚡ Commands

```bash
# Process all manual content
./scripts/process_manual_content.sh

# Process specific file
python3 files_manager_runner.py add-file data/raw/sap-btp-overview.txt

# Check processed files
python3 files_manager_runner.py list
```

## ✅ Success Indicators

- Files appear in `data/processed/processed_files.json`
- No error messages during processing
- Content is searchable in your RAG system

## 🆘 Common Issues

- **File not found**: Check file is in `data/raw/` directory
- **Permission denied**: Run `chmod +x scripts/process_manual_content.sh`
- **Processing errors**: Check file format and content quality
