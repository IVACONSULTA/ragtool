## 📝 Description

This PR focuses on cleaning up the repository, consolidating documentation, and finalizing the configuration for the Railway deployment of the IVA Consulta agent. It removes obsolete scripts and temporary fix files while organizing documentation into a coherent structure.

## 🎯 What does this PR do?

- [ ] Feature addition
- [ ] Bug fix
- [x] Documentation update
- [x] Code refactoring
- [x] Other: Repository Cleanup & Organization

## 🔍 Changes Made

### 🧹 Cleanup & Removal

- Removed broken/obsolete `complete_workflow.py` script.
- Removed temporary fix documentation (`CLOUD_RUN_PORT_FIX.md`, `DATABASE_LOCATION_FIX.md`, etc.) from the root directory.
- Removed backup and temporary environment files (`.env.backup`, `.env_example`).
- Removed unused/deprecated agent config files (`sap_agents.yaml`, `sap_tasks.yaml`).

### 📚 Documentation Consolidation

- Renamed and moved various guides to the `docs/` directory for better organization:
  - `Adding_manual_content.md` (was `MANUAL_CONTENT_GUIDE.md`)
  - `Google_Cloud_DB_rebuild_guide.md` (was `DATABASE_REBUILD_GUIDE.md`)
  - `Local_setup_Configuration_Guide.md` (was `Configuration_Guide.md`)
  - `RagTool_files_management.md` (was `Files_Management.md`)
  - `Ragtool_Api.md` (was `IVA_CONSULTA_API.md`)

### 🛠️ Code & Configuration

- Updated `agents/crewai/crew_agent_server_with_guard_rails.py` for improved stability.
- Enhanced `security/security_logger.py` and updated security documentation.

## 🧪 Testing

- [x] I have tested this locally
- [ ] All tests pass
- [x] No breaking changes

## 📸 Screenshots (if applicable)

N/A

## 📋 Checklist

- [x] Code follows project style guidelines
- [x] Self-review completed
- [x] Code is commented where necessary
- [x] Documentation updated (if needed)

## 🚀 Deployment Notes

- Ensure `AGENT_ROLE` is set correctly (default: `vat_agent`).
- No new environment variables are required, but the repository structure is now cleaner for deployment.

## 📞 Additional Notes

This PR significantly reduces clutter in the root directory and ensures that documentation is easy to find and follow in the `docs/` folder.
