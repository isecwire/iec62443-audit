# Changelog

## [1.0.0] - 2026-04-03
### Added
- Stable release, production-ready
- PDF report generation via WeasyPrint (optional dependency)
- Assessment templates — pre-filled assessments for common system types (PLC, HMI, Gateway, SCADA Server)
- Bulk assessment import from Excel/CSV with automatic SR matching
- Assessment audit trail — track who assessed what and when
- REST API mode for integration with GRC platforms (--serve)
- Multi-language support for report generation (EN, DE, FR)
### Changed
- Scoring algorithm handles partial implementations (0.5 increments)
- HTML report includes interactive JavaScript charts
- Action plan now estimates cost ranges per remediation item
### Fixed
- Comparison view crash when assessments have different standard versions
- Spider chart rendering for FRs with zero SRs assessed
- Zone aggregation incorrect when mixing 3-3 and 4-2 standards

## [0.2.0] - 2026-02-15
### Added
- IEC 62443-4-2 component-level requirements (60+ CRs)
- Cross-standard mapping (NIST CSF, ISO 27001, CIS, EU CRA, NIS2, GDPR)
- Multi-zone/conduit assessment with site aggregation
- Action plan generator with effort estimates and priority scoring
- Evidence collection framework
- Maturity model (5 levels per SR)
- Optional Textual TUI (--tui)
- Rich CLI with spider charts, heatmaps, compliance bars
- CSV/Markdown export and CSV import

## [0.1.0] - 2025-12-25
### Added
- Initial release
- Full IEC 62443-3-3 foundational requirements (7 FRs, 51 SRs)
- Interactive CLI assessment with rich prompts
- SL-Achieved calculation (minimum of SRs per FR)
- Gap analysis (SL-Target vs SL-Achieved)
- Compliance percentage per FR
- Assessment comparison for progress tracking
- JSON export/import of assessments
- HTML report generation with Jinja2 templates
