# CX-FP — Customer Expeience Feedback Platform

CX-FP is a kiosk-based multilingual feedback platform designed for private or public-sector environments.

The system supports centrally managed touchscreen kiosks, configurable questionnaires, multilingual operation, 
offline response collection, analytics, RBAC, and accessibility-oriented UI

## Current Version

v1.2

## v1.2 Highlights

- Role-based access control (RBAC)
  - pt_admin
  - eu_admin
  - eu_manager
- Multilingual questionnaires
- Branching questionnaire logic
- Kiosk attract/screensaver mode
- Improved kiosk UX for 15" touchscreen devices
- Analytics dashboard (few analytics functions at present)
- CSV & XLSX export of raw responses
- Offline-ready kiosk response queueing
- Central kiosk/questionnaire management
- Accessibility-oriented kiosk UI

## Architecture

Backend:
- FastAPI
- SQLAlchemy
- SQLite

Frontend:
- HTML/CSS/JavaScript kiosk UI
- HTML/CSS/JavaScript admin UI

Deployment:
- Linux
- systemd
- nginx reverse proxy

## Repository Structure

/backend
    FastAPI backend
/kiosk-ui
    Public kiosk touchscreen interface
/admin-ui
    Administrative interface
	
	## Next version to feature

- Single-question kiosk survey flow
- PDF analytics reporting
- Heartbeat monitoring
- Essentia anti-gaming logic
- UI/UX polish and branding
- Device monitoring dashboard