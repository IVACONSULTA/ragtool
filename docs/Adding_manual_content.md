# Manual Content Addition Guide

This guide helps you add content from blocked websites to your RAG system.

## 🚫 Blocked Websites

The following websites are currently blocked and need manual content extraction:

1. **https://www.sap.com/products/technology-platform.html** - SAP BTP Overview
2. **https://www.taxtech500.com/featured-articles/from-banking-apps-to-sap-btp-the-new-era-of-embedded-tax** - TaxTech500 Article
3. **https://sapinsider.org/blogs/embracing-sap-btp-and-avalara-solutions-during-s4-migration-to-meet-tax-compliance-mandates** - SAP Insider Blog
4. **https://www.sap.com/swiss/products/erp/partners/meridian-global-vat-services-limited-arco-tax-determination-for-sap-btp.html** - Meridian ARCO

## 📝 Step-by-Step Process

### Method 1: Using Templates (Recommended)

1. **Open the template files** in `data/templates/`:

   - `sap-btp-overview.txt`
   - `taxtech500-embedded-tax.txt`
   - `sapinsider-btp-avalara.txt`
   - `meridian-arco-tax-determination.txt`

2. **Visit each blocked website** in your browser

3. **Copy the main content** from each website and paste it into the corresponding template

4. **Save the files** in `data/raw/` directory with descriptive names:

   - `sap-btp-overview.txt`
   - `taxtech500-embedded-tax.txt`
   - `sapinsider-btp-avalara.txt`
   - `meridian-arco-tax-determination.txt`

5. **Process the files** using your existing file processing system

### Method 2: Save as PDF

1. **Visit each website** in your browser
2. **Save as PDF** using your browser's print function
3. **Place PDFs** in `data/raw/` directory
4. **Process using** your file processing system

### Method 3: Browser Developer Tools

1. **Open Developer Tools** (F12) on each website
2. **Find the main content** in the HTML
3. **Copy the text content** and save as `.txt` files
4. **Place in** `data/raw/` directory

## 🔧 Processing Manual Content

Once you've saved the content, process it using:

```bash
# Process all files in data/raw/
python3 files_manager_runner.py process

# Or process specific files
python3 files_manager_runner.py add-file data/raw/sap-btp-overview.txt
```

## 📋 Content Extraction Tips

### For SAP Websites:

- Focus on the main product description
- Include key features and benefits
- Copy use cases and examples
- Include technical specifications if available

### For Articles/Blogs:

- Copy the main article content
- Include key points and insights
- Preserve any lists or structured information
- Include conclusions and recommendations

### For Partner Pages:

- Focus on product features
- Include integration details
- Copy benefits and use cases
- Include contact or implementation information

## ✅ Verification

After adding manual content:

1. **Check processed files**: Look at `data/processed/processed_files.json`
2. **Test search**: Try searching for content from the manually added sources
3. **Verify quality**: Ensure the content is complete and well-formatted

## 🎯 Expected Results

After manual content addition, you should have:

- 6 total sources (2 from successful web scraping + 4 from manual addition)
- Complete coverage of SAP BTP and tax technology topics
- Searchable content in your RAG system

## 🆘 Troubleshooting

If you encounter issues:

1. **Check file format**: Ensure files are properly formatted text or PDF
2. **Verify file location**: Files should be in `data/raw/` directory
3. **Check file permissions**: Ensure files are readable
4. **Review error messages**: Look for specific error details in the output

## 📞 Support

If you need help with manual content extraction:

1. Check the template files for guidance
2. Use browser developer tools for complex content
3. Consider using browser extensions for content saving
4. Contact website administrators for API access if needed
