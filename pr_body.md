## 📝 Description

This PR expands the VAT questions dataset from 50 to 100 questions, creates a new excluded information questions file, and reorganizes questions by country. It enhances the testing and evaluation capabilities of the IVA Consulta agent with a more comprehensive question set covering multiple European countries and languages.

## 🎯 What does this PR do?

- [x] Feature addition
- [ ] Bug fix
- [x] Documentation update
- [x] Code refactoring
- [ ] Other: Repository Cleanup & Organization

## 🔍 Changes Made

### 📊 VAT Questions Expansion

#### Control Questions (`control_questions.txt`)

- **Expanded from 50 to 100 questions**
  - **70 questions about Spain** (distributed across Spanish, English, French, German, Portuguese)
  - **30 questions about other countries** covering:
    - France (5), Germany (5), Italy (4), Portugal (4)
    - Finland (3), Lithuania (3), Romania (3), Belgium (3), Netherlands (3), Austria (2)
- **Language distribution**: Questions are now in Spanish, English, French, German, and Portuguese regardless of country context, providing better multilingual testing coverage

#### Excluded Information Questions (`excluded_info_questions.txt`)

- **Created new file with 100 questions** covering VAT topics NOT included in raw documents
  - **70 questions about Spain** (topics not covered in raw data)
  - **30 questions about other countries** (Austria, Netherlands, Poland, Sweden, Denmark, Ireland, Greece, Czech Republic, Hungary, Bulgaria, Croatia, Cyprus, Estonia, Latvia, Malta, Norway, United Kingdom)
- **Purpose**: Enables testing of the agent's ability to identify when information is not available in the knowledge base

#### Randomized Questions (`control_questions_randomized.txt`)

- **Rebuilt with all 100 questions grouped by country** (instead of by language)
- Maintains same question set but organized for country-based evaluation
- All languages mixed within each country section

### 📁 Files Modified/Created

- ✅ `data/processed/control_questions.txt` - Expanded to 100 questions
- ✅ `data/processed/excluded_info_questions.txt` - New file with 100 excluded info questions
- ✅ `data/processed/control_questions_randomized.txt` - Rebuilt with country grouping

## 🧪 Testing

- [x] I have tested this locally
- [x] Question counts verified (70 Spain + 30 other countries = 100 total)
- [x] Language distribution verified across all countries
- [x] No breaking changes

## 📸 Screenshots (if applicable)

N/A

## 📋 Checklist

- [x] Code follows project style guidelines
- [x] Self-review completed
- [x] Code is commented where necessary
- [x] Documentation updated (if needed)
- [x] Question counts verified
- [x] Language distribution verified

## 🚀 Deployment Notes

- No environment variables or configuration changes required
- New question files are ready for use in agent evaluation and testing
- Questions cover multiple European countries and languages for comprehensive testing

## 📞 Additional Notes

This PR significantly enhances the testing dataset for the IVA Consulta agent:

- **Doubled the question set** from 50 to 100 questions
- **Added excluded information questions** to test agent's ability to identify missing information
- **Improved language diversity** with questions in 5 languages across all countries
- **Better organization** with country-based grouping for easier evaluation

The expanded dataset will enable more thorough testing of the agent's VAT knowledge across different countries and languages, as well as its ability to handle queries about information not present in the knowledge base.
