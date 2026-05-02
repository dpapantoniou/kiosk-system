# Kiosk System v1.0

## Overview

The Kiosk System is a multilingual feedback collection platform designed
for kiosk/tablet deployment in public-facing environments such as
courts, service centers, government offices, and customer interaction
points.

The system currently consists of:

-   Kiosk frontend UI
-   Admin UI
-   FastAPI backend
-   SQLite database
-   Multilingual questionnaire support
-   Offline response buffering
-   CSV export functionality
-   Admin authentication

Version: `v1.0` Git Tag: `v1.0`

# Core Features

## 1. Multilingual Kiosk UI

The kiosk frontend supports multilingual operation.

Currently implemented languages:

-   English
-   Greek
-   Turkish

Each questionnaire question supports localized text versions.

The kiosk interface dynamically adapts to the selected language.

## 2. Questionnaire Management

The Admin UI supports creation and management of questionnaires.

Features:

-   Questionnaire code
-   Questionnaire name
-   Active/inactive status
-   Dynamic question creation
-   Question ordering
-   Multiple question types

Supported question types:

-   Rating
-   Text

Each question supports:

-   English text
-   Greek text
-   Turkish text
-   Required flag

## 3. Kiosk Management

The system supports multiple kiosks.

Each kiosk has:

-   Unique kiosk code
-   Name
-   Location
-   Questionnaire assignment

Example:

-   NICOSIA-01
-   LIMASSOL-01

Questionnaires can be assigned dynamically from the Admin UI.

## 4. Response Collection

The system records questionnaire responses with:

-   Timestamp
-   Kiosk identifier
-   Language
-   Question/answer payload

Responses are stored centrally in the backend database.

## 5. Offline Mode Support

The kiosk frontend supports temporary offline operation.

If backend connectivity is unavailable:

-   Responses are buffered locally
-   Synchronization occurs automatically once connectivity is restored

This improves reliability in unstable network environments.

## 6. CSV Export

The Admin UI supports CSV export of collected responses.

Export includes:

-   Timestamp
-   Kiosk
-   Language
-   Answers

Useful for:

-   Reporting
-   Analytics
-   BI ingestion
-   Excel processing

## 7. Admin Authentication

Version v1 introduces authenticated admin access.

Implemented components:

-   Admin user model
-   Password hashing/security layer
-   Admin login page
-   Session-based authentication

Utility scripts:

-   create_admin_user.py
-   change_admin_password.py
-   inspect_admins.py

# Technical Stack

## Backend

-   Python
-   FastAPI
-   SQLAlchemy
-   SQLite

## Frontend

-   HTML
-   CSS
-   Vanilla JavaScript

## Deployment

-   Linux server
-   systemd service
-   nginx reverse proxy

# Repository Structure

    backend/
     ├── app/
     │    ├── api/
     │    ├── models/
     │    ├── schemas/
     │    └── security.py
     │
     ├── create_admin_user.py
     ├── change_admin_password.py
     ├── inspect_admins.py
     └── index.html

    frontend-kiosk/
     └── index.html

# Git Workflow

Current repository structure:

-   `master` → stable baseline
-   `feature/admin-ui` → active development branch

Stable release tag:

    git tag v1.0

# Current Operational Features

## Admin UI

Current Admin UI supports:

-   Create questionnaire
-   Add questions dynamically
-   View questionnaires
-   View kiosks
-   Assign questionnaires to kiosks
-   View responses
-   Export CSV
-   Admin login/logout

# Planned Enhancements

## Near-term roadmap

### Admin UI improvements

-   Tabbed UI
-   Create kiosk from UI
-   Edit kiosk
-   Branding support
-   Better response viewer
-   Response sorting/filtering

### Branding

Planned fields:

-   logo_url
-   primary_color
-   background_image
-   welcome_message

### Deployment improvements

-   Deployment script
-   Automated static file deployment
-   Improved configuration management

# Deployment Notes

Example deployment locations:

    /opt/kiosk-admin/
    /opt/kiosk-frontend/

Suggested deployment workflow:

1.  Edit source-controlled files
2.  Commit to git
3.  Copy deployed files to runtime locations
4.  Restart services if required

# Recommended Future Architecture

As the system grows, the following separation is recommended:

    backend/
     ├── index.html
     ├── admin.js
     └── admin.css

and:

    frontend-kiosk/
     ├── index.html
     ├── kiosk.js
     └── kiosk.css

This will improve maintainability and future extensibility.

# Summary

Kiosk System v1.0 delivers a stable multilingual kiosk feedback platform
with:

-   Multi-kiosk support
-   Multilingual questionnaires
-   Offline resilience
-   Admin authentication
-   CSV export
-   Operational admin UI
-   Production-ready deployment baseline

