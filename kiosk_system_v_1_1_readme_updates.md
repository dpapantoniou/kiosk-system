# Kiosk System V1.1 – Release Notes / README Addendum

## Overview

Version 1.1 introduces major improvements to the administration interface, kiosk management workflow, API usability, and deployment readiness.

The system has evolved from a proof-of-concept questionnaire platform into a more structured multi-kiosk deployment platform suitable for court-service and public-service feedback collection.

---

# New Features in V1.1

## 1. Kiosk Administration UI

A complete browser-based administration interface has been implemented.

### Features

- Secure administrator login/logout
- Session-cookie authentication
- Multi-tab administration interface
- Real-time kiosk refresh
- Questionnaire refresh
- Response viewing
- CSV export support

### Tabs

- Questionnaires
- Kiosks
- Responses

---

# 2. Kiosk Creation from Admin UI

Administrators can now create kiosks directly from the web interface.

### Supported Fields

- Kiosk Code
- Kiosk Name
- Location
- Active/Inactive State

### Notes

- Validation added for mandatory fields
- Immediate refresh after creation
- Backend persistence via SQLite

---

# 3. Kiosk Editing Support

A full kiosk editing workflow has been implemented.

### Editable Fields

- Kiosk Code
- Kiosk Name
- Location
- Active State

### Features

- Edit button in kiosk table
- Inline edit form
- Save/Cancel operations
- Automatic refresh after update
- Preservation of questionnaire assignments during edit

This resolved earlier operational issues where kiosk codes had to be modified manually through SQLite.

---

# 4. Questionnaire Assignment Improvements

Questionnaire assignment workflow was improved.

### Enhancements

- Human-readable questionnaire names in dropdowns
- Improved kiosk/questionnaire mapping logic
- Faster rendering using questionnaire lookup maps
- Cleaner success messages

---

# 5. Public Kiosk Retrieval API

A new public API endpoint has been added.

## Endpoint

```text
GET /kiosk/by-code/{code}
```

## Example

```text
GET /kiosk/by-code/01
```

## Returns

- kiosk metadata
- assigned questionnaire
- all associated questions
- multilingual text structures

This endpoint is now used by the kiosk frontend UI.

---

# 6. Dynamic Kiosk UI Loading

The kiosk frontend now dynamically loads questionnaires based on kiosk code.

## Example URL

```text
https://chatbot.performance.gr/kiosk-ui/?kiosk=01
```

### Behavior

- frontend extracts kiosk code from URL
- fetches kiosk configuration using REST API
- dynamically renders assigned questionnaire

This enables:

- one shared frontend for all kiosks
- centralized management
- easier deployment
- dynamic reassignment of questionnaires

---

# 7. Improved Response Viewer

Response management improvements include:

- newest responses displayed first
- cleaner JSON formatting
- CSV export support
- authentication enforcement

---

# 8. Authentication Improvements

Session-based authentication flow was stabilized.

### Improvements

- automatic reload on unauthorized access
- credential propagation in fetch requests
- authenticated API calls throughout admin UI

---

# 9. Frontend Stability Improvements

Several frontend issues were resolved.

### Resolved Issues

- malformed template literals
- broken async/await flows
- questionnaire rendering race conditions
- JavaScript parser corruption from malformed HTML fragments
- CR/LF encoding issues in JavaScript files

---

# 10. Git Version Control Initialization

The project is now maintained under Git version control.

### Repository Structure

```text
backend/
kiosk-admin/
kiosk-ui/
```

### Branching

Current working branch:

```text
feature/admin-ui
```

---

# Current Architecture

## Backend

- FastAPI
- SQLite
- REST API
- Session authentication

## Frontend

### kiosk-admin

Administrative interface for:

- kiosk management
- questionnaire management
- response export

### kiosk-ui

Public-facing questionnaire kiosk frontend.

---

# Deployment URLs

## Public Kiosk UI

```text
https://chatbot.performance.gr/kiosk-ui/
```

## Admin Interface

```text
https://chatbot.performance.gr/kiosk-admin/
```

## REST API Example

```text
https://chatbot.performance.gr/kiosk/by-code/01
```

---

# Suggested Next Steps

## Priority Features

1. Questionnaire editing
2. Questionnaire deletion
3. Kiosk deletion
4. Branding/logo support per kiosk
5. Touch-screen kiosk optimization
6. Offline caching support
7. Analytics dashboard
8. Multi-admin role support
9. Audit logging
10. PostgreSQL migration

---

# Recommended Version Tag

Recommended release tag:

```text
v1.1-admin-ui
```

---

# Summary

Version 1.1 represents a major operational milestone:

- dynamic kiosk/questionnaire architecture implemented
- browser-based administration completed
- public API structure stabilized
- multi-kiosk deployment model validated
- Git-based lifecycle management initiated

The system is now suitable for structured pilot deployment across multiple judicial or public-service locations.

