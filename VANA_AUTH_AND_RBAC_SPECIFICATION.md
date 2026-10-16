# VANA / FIN Backend Authentication & Role-Based Access Control (RBAC) Specification

**Document Version:** 1.0.0  
**Target Audience:** Frontend Team, Integration Leads, Security & Governance Auditors  
**Technical Leads:** Ansh (Governance & Security Lead), Mohit (Integration Lead)  
**System Status:** **ONLINE & VERIFIED** (7/7 Validation Stages Passing)  

---

## 1. Executive Summary

This document specifies the backend authentication, JSON Web Token (JWT) bearer format, role mapping, and Role-Based Access Control (RBAC) enforcement implemented for the **VANA Environmental Intelligence Platform**.

The backend bridges the frontend roles (`admin`, `participant`, `judge`, `steward`) with the constitutional MasterDB governance roles (`PLATFORM_ADMIN`, `APPROVED_CONSUMER`, `AUDITOR`, `GOVERNANCE_STEWARD`), enabling immediate, seamless integration with `hackaverse-frontend` and any custom client.

---

## 2. Pre-Seeded Test Credentials (Ready to Use)

The backend SQLite database (`vana_masterdb.sqlite`) has been initialized with **pre-seeded test accounts** across all roles. The frontend can immediately authenticate using these credentials without any manual database setup:

| Role (Frontend) | Governance Role (MasterDB) | Email | Password | Permissions & Access Scope |
| :--- | :--- | :--- | :--- | :--- |
| **`admin`** | `PLATFORM_ADMIN` | `admin@vana.bhiv` | `Admin@123` | Full administrative control, TANTRA execution (`/vana/execute`), policy modifications, user management. |
| **`participant`** | `APPROVED_CONSUMER` | `researcher@vana.bhiv`<br>*(alias: `participant@vana.bhiv`)* | `User@123` | Access real observation datasets, spatial GIS vector layers, carbon analytics, weather observations. |
| **`judge`** | `AUDITOR` | `judge@vana.bhiv` | `Judge@123` | Inspect full governance audit logs (`/api/v1/governance/audit-log`), provenance records, verify carbon models. |
| **`steward`** | `GOVERNANCE_STEWARD` | `steward@vana.bhiv` | `Steward@123` | MasterDB data classification, evaluate 6-tuple governance, authorize dataset access requests. |

---

## 3. Authentication Endpoints

Base URL: `http://localhost:8000` (or your deployed API gateway URL)

### 3.1 User Login
- **Method:** `POST`
- **Paths:** `/api/v1/auth/login` *(and alias `/auth/login` for frontend compatibility)*
- **Headers:** `Content-Type: application/json`

#### Request Body
```json
{
  "email": "admin@vana.bhiv",
  "password": "Admin@123"
}
```

#### Successful Response (`HTTP 200 OK`)
```json
{
  "success": true,
  "message": "Authentication successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "ref-9b2f6e7a12c4...",
  "token_type": "bearer",
  "expires_in_hours": 24,
  "user": {
    "id": "usr-admin-001",
    "user_id": "usr-admin-001",
    "email": "admin@vana.bhiv",
    "name": "VANA Platform Administrator",
    "role": "admin",
    "governance_role": "PLATFORM_ADMIN",
    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=admin@vana.bhiv",
    "permissions": {
      "view_all_datasets": true,
      "view_observations": true,
      "view_carbon_analytics": true,
      "view_spatial_layers": true,
      "view_audit_logs": true,
      "execute_tantra_pipeline": true,
      "manage_users": true,
      "evaluate_governance": true,
      "modify_policies": true
    },
    "created_at": "2026-10-12T09:47:00Z"
  },
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "ref-9b2f6e7a12c4...",
    "token_type": "bearer",
    "user": { ... }
  }
}
```

---

### 3.2 User Registration
- **Method:** `POST`
- **Paths:** `/api/v1/auth/register` *(and alias `/auth/register`)*
- **Headers:** `Content-Type: application/json`

#### Request Body
```json
{
  "name": "Ansh Shrivastava",
  "email": "ansh@vana.bhiv",
  "password": "User@123",
  "role": "participant"
}
```
*Note: Accepted values for `role` are `admin`, `participant`, `judge`, `steward`.*

#### Successful Response (`HTTP 200 OK`)
Returns the newly created user object and active access token with the same structure as `/login`.

---

### 3.3 Get Current User Profile (`Me`)
- **Method:** `GET`
- **Paths:** `/api/v1/auth/me` *(and aliases `/auth/me`, `/user/profile`)*
- **Headers:** `Authorization: Bearer <access_token>`

#### Successful Response (`HTTP 200 OK`)
```json
{
  "success": true,
  "user": {
    "id": "usr-researcher-001",
    "user_id": "usr-researcher-001",
    "email": "researcher@vana.bhiv",
    "name": "Environmental Science Researcher",
    "role": "participant",
    "governance_role": "APPROVED_CONSUMER",
    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=researcher@vana.bhiv",
    "permissions": {
      "view_all_datasets": true,
      "view_observations": true,
      "view_carbon_analytics": true,
      "view_spatial_layers": true,
      "view_audit_logs": false,
      "execute_tantra_pipeline": false
    }
  }
}
```

---

### 3.4 Supported Roles & Permissions Matrix
- **Method:** `GET`
- **Path:** `/api/v1/auth/roles`

Returns all supported frontend and governance roles, their mapping, permissions, and test accounts.

---

### 3.5 Logout
- **Method:** `POST`
- **Paths:** `/api/v1/auth/logout` *(and alias `/auth/logout`)*
- **Headers:** `Authorization: Bearer <access_token>`

#### Successful Response (`HTTP 200 OK`)
```json
{
  "success": true,
  "message": "Session logged out successfully."
}
```

---

## 4. Role-Based Access Control (RBAC) Matrix

| Endpoint / Capability | Public / Guest | `participant` (`APPROVED_CONSUMER`) | `judge` (`AUDITOR`) | `admin` (`PLATFORM_ADMIN`) | `steward` (`GOVERNANCE_STEWARD`) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `GET /health` |  |  |  |  |  |
| `POST /api/v1/auth/login` |  |  |  |  |  |
| `POST /api/v1/auth/register` |  |  |  |  |  |
| `GET /api/v1/spatial/layers` |  |  |  |  |  |
| `GET /api/v1/carbon/summary` |  |  |  |  |  |
| `GET /api/v1/observations/real` |  |  |  |  |  |
| `GET /api/v1/carbon/maharashtra` |  |  |  |  |  |
| `GET /api/v1/carbon/thane-creek` |  |  |  |  |  |
| `POST /api/v1/governance/evaluate` |  |  |  |  |  |
| `GET /api/v1/governance/audit-log` | ❌ (403) | ❌ (403 Forbidden) |  |  |  |
| `POST /vana/execute` (TANTRA) | ❌ (403) | ❌ (403 Forbidden) | ❌ (403 Forbidden) |  | ❌ (403 Forbidden) |

### Error Codes:
- **`401 Unauthorized`**: Missing or invalid Bearer token / expired session.
- **`403 Forbidden`**: Valid token, but user role does not possess the required privileges.

---

## 5. Frontend Integration Snippet

### In `api.js` (Axios Interceptor):
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Automatic Bearer Token Attachment
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### In `AuthContext.jsx` (Login Handler):
```javascript
const login = async (email, password) => {
  const response = await api.post('/api/v1/auth/login', { email, password });
  const { access_token, user } = response.data;
  
  localStorage.setItem('authToken', access_token);
  localStorage.setItem('userData', JSON.stringify(user));
  
  setUser(user);
  setIsAuthenticated(true);
  return { success: true, user };
};
```
