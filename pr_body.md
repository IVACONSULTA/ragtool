## 📝 Description

Small maintenance PR on the `fear/update-docs` branch that tidies the evaluation question set and resets the RAG processing-state file.

Two minor data-only changes:

1. **Remove the reverse-charge French control question** from `control_questions_randomized.txt` to keep the randomized evaluation set aligned with the curated source list.
2. **Reset `processed_files.json`** so a fresh RAG ingestion run starts from a clean state (no stale `last_updated` timestamp).

No code, agent, task, dependency or infrastructure changes.

## 🎯 What does this PR do?

- [ ] Feature addition
- [ ] Bug fix
- [x] Documentation / data update
- [ ] Code refactoring
- [ ] Other

## 🔍 Changes Made

### 1. `data/processed/control_questions_randomized.txt`

- Removed the question  
  *"Comment s'applique le mécanisme d'autoliquidation (reverse charge) en Espagne pour les services fournis par des non-résidents?"*  
  from the randomized evaluation set. The slot is left as blank lines to preserve surrounding ordering.

### 2. `data/processed/processed_files.json`

- Reset `last_updated` from a previous timestamp (`"2026-02-11T08:20:00.282363"`) to `null`, so the next ingestion run records a clean baseline.

```json
{
  "processed_files": {},
  "last_updated": null
}
```

## 📁 Files Modified

- ✏️ `data/processed/control_questions_randomized.txt` — one question removed.
- ✏️ `data/processed/processed_files.json` — `last_updated` reset to `null`.

## 🧪 Testing

- [x] Randomized control-questions file still parses line-by-line as expected by the evaluation runner.
- [x] `processed_files.json` is valid JSON and is accepted by the RAG ingestion pipeline on next start (treated as a cold start).
- [x] No other files touched; no runtime behaviour change beyond the next ingestion run recomputing its own `last_updated`.

## 📋 Checklist

- [x] Self-review completed
- [x] No code changes (data-only)
- [x] No new dependencies
- [x] No environment variable changes
- [x] Backward compatible

## 🚀 Deployment Notes

- No new env vars or dependencies.
- On next RAG ingestion run, `processed_files.json` will be repopulated — expected side effect of this PR.
- The removed French control question is not referenced elsewhere; evaluation scripts that iterate over the file will simply see one fewer question.

## 📞 Additional Notes

This is a small housekeeping change; consider squash-merging the single `Update docs` commit.
