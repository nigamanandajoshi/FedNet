# FedNet - Standalone Portal Applications

## Overview

This dashboard consists of **three completely independent portal applications** with no shared navigation. Each portal is accessed via direct URL and operates as a standalone application.

---

## Portal Access

### 🏥 Hospital Portal (Disease Checking)
**URL:** `http://localhost:3000/hospital-portal`

**Purpose:** Check patient CBC values and predict thalassemia conditions

**Users:** Hospital staff, clinicians

---

### 👨‍💼 Admin Portal (Training Monitor)
**URL:** `http://localhost:3000/admin-portal`

**Purpose:** Monitor federated learning training progression from local models to global model

**Users:** System administrators, ML engineers

---

### 📤 Data Upload Portal (Hospital Contribution)
**URL:** `http://localhost:3000/data-upload-portal`

**Purpose:** Upload patient data and train local models for federated learning

**Users:** Hospital data contributors

---

## Key Features

✅ **Completely Isolated** - No navigation links between portals  
✅ **Standalone Applications** - Each portal operates independently  
✅ **Direct URL Access** - Access each portal by navigating to its specific URL  
✅ **No Shared Navigation Bar** - Clean, focused interface for each portal

---

## Running the Dashboard

```bash
cd dashboard
npm run start
```

Then access each portal via its direct URL as listed above.

---

## Architecture

- **No Landing Page** - Users access portals directly via URL
- **No Shared Components** - Each portal is self-contained
- **Isolated Routing** - Portals don't link to each other
- **Dedicated UI** - Each portal has its own branding and layout
