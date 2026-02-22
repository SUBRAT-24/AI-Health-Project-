# AI Health Assistant – Admin & Full Functionality Implementation Plan

## Executive Summary

This plan adds a dedicated **Admin Panel** with separate login, user management, report moderation, and platform oversight. It also ensures all existing functionality works end-to-end.

---

## Phase 1: Database & Auth Updates

### 1.1 Add Admin Role to User Model

**File:** `backend/flask_app/models/__init__.py`

- Add `role` column: `db.Column(db.String(20), default='user')` — values: `'user'` | `'admin'`
- Add `is_active` column: `db.Column(db.Boolean, default=True)` — for soft delete / suspend
- Update `to_dict()` to include `role`, `is_active`

### 1.2 Create Initial Admin User

- Add migration or seed script to create admin user (e.g. `admin@healthassistant.com`)
- Or add a CLI command: `python -m flask create-admin --email admin@example.com`

### 1.3 Admin Login Flow

**Option A – Same login, different redirect**
- Keep existing `POST /api/auth/login`
- Include `role` in login response
- Frontend redirects to admin dashboard if `role === 'admin'`

**Option B – Separate admin login page**
- Add `POST /api/auth/admin-login` (optional; can reuse same endpoint with role check)
- Admin uses `pages/admin-login.html` instead of `pages/login.html`

---

## Phase 2: Backend Admin API

### 2.1 Admin Decorator

**File:** `backend/flask_app/utils/admin_decorator.py` (new)

```python
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper
```

### 2.2 Admin Routes

**File:** `backend/flask_app/routes/admin.py`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/stats` | GET | Platform stats (user count, reports, appointments) |
| `/api/admin/users` | GET | List all users (with pagination) |
| `/api/admin/users/<id>` | GET | User details + health records count, appointments, reports |
| `/api/admin/users/<id>/deactivate` | POST | Set `is_active=False` (soft remove) |
| `/api/admin/users/<id>/activate` | POST | Set `is_active=True` |
| `/api/admin/users/<id>/delete` | DELETE | Hard delete user (optional; use carefully) |
| `/api/admin/reports` | GET | List all reports (across users) |
| `/api/admin/reports/<id>` | GET | Report details |
| `/api/admin/reports/<id>/approve` | POST | Approve report (e.g. set status) |
| `/api/admin/reports/<id>/reject` | POST | Reject report (optionally remove file) |
| `/api/admin/reports/<id>/delete` | DELETE | Delete report |
| `/api/admin/appointments` | GET | List all appointments |
| `/api/admin/appointments/<id>/reject` | POST | Cancel/reject appointment |

### 2.3 Report Status

**File:** `backend/flask_app/models/__init__.py` (Report model)

- Extend `status`: `uploaded` | `pending_review` | `approved` | `rejected`
- New uploads default to `pending_review` if you want moderation, or `uploaded` if not

---

## Phase 3: Admin Frontend

### 3.1 Admin Login Page

**File:** `frontend/pages/admin-login.html` (new)

- Same layout as `login.html` but:
  - Title: "Admin Login"
  - Form posts to same `/api/auth/login`
  - On success, check `response.role === 'admin'` → redirect to `admin-dashboard.html`
  - If role is `user`, show error: "Admin access required"

### 3.2 Admin Dashboard

**File:** `frontend/pages/admin-dashboard.html` (new)

- Navbar: Admin logo, "Admin Panel", Logout
- Sidebar or tabs:
  - Overview (stats cards)
  - Users
  - Reports
  - Appointments
  - System Health

### 3.3 Admin Sections

#### Overview
- Cards: Total Users, Total Reports, Pending Reports, Total Appointments, Scheduled vs Completed

#### Users
- Table: ID, Name, Email, Role, Status (active/inactive), Registered Date
- Actions: View Details, Deactivate, Activate, Delete
- Search / filter by email or name

#### Reports
- Table: ID, User, Description, Type, Status, Upload Date
- Actions: View, Approve, Reject, Delete
- Filter by status: pending / approved / rejected

#### Appointments
- Table: User, Doctor, Date, Status
- Actions: View, Reject/Cancel

### 3.4 Home / Landing Page

**File:** `frontend/index.html`

- Add link: "Admin Login" (e.g. in navbar or footer)
- Link to `pages/admin-login.html`

---

## Phase 4: Existing Functionality Verification

### 4.1 Ensure All Features Work

| Feature | Frontend | Backend | Status |
|---------|----------|---------|--------|
| Signup | signup.html | POST /auth/signup | ✓ |
| Login | login.html | POST /auth/login | ✓ |
| Dashboard | dashboard.html | JWT protected | ✓ |
| Health Tracking | health-tracking.html | POST /health/update | ✓ |
| Appointments | appointments.html | /appointments/* | ✓ |
| Reports Upload | reports.html | POST /reports/upload | ✓ |
| Diet | diet-suggestions.html | POST /diet/recommendations | ✓ |
| Exercise | exercise.html | POST /exercise/recommendations | ✓ |
| Chatbot | dashboard / widget | POST /chatbot/message | ✓ |

### 4.2 Fixes if Needed

- Verify `main.js` has all API helpers: `getReports`, `uploadReport`, etc.
- Ensure report upload uses `FormData` and `multipart/form-data` for file upload
- Test CORS for `http://127.0.0.1:5000` and frontend origin

---

## Phase 5: File Structure Summary

```
frontend/
├── index.html                    # Add Admin Login link
├── pages/
│   ├── admin-login.html         # NEW
│   ├── admin-dashboard.html     # NEW
│   ├── admin-users.html         # NEW (or embedded in dashboard)
│   ├── admin-reports.html       # NEW
│   └── admin-appointments.html  # NEW (or embedded)
├── css/
│   └── admin.css                # NEW (optional; can reuse style.css)
└── js/
    ├── main.js                  # Add isAdmin, admin redirect logic
    └── admin.js                 # NEW: Admin API calls & UI logic

backend/flask_app/
├── models/__init__.py           # Add role, is_active to User
├── routes/
│   ├── auth.py                  # Include role in login response
│   └── admin.py                 # Extend with new endpoints
└── utils/
    └── admin_decorator.py       # NEW: @admin_required
```

---

## Phase 6: Implementation Order

1. **Database**: Add `role`, `is_active` to User; create admin user.
2. **Auth**: Include `role` in login response; add admin check.
3. **Admin API**: Apply `@admin_required` to existing admin routes; add new endpoints.
4. **Admin Frontend**: Admin login → admin dashboard → Users → Reports → Appointments.
5. **Testing**: Test admin flows, user deactivation, report approve/reject.
6. **Existing Features**: Run through all user flows; fix any issues.

---

## Phase 7: Security Considerations

- Admin routes protected with `@admin_required` (JWT + role check).
- Never expose admin endpoints to non-admin users.
- Log admin actions (user deactivation, report rejection, etc.) for audit.
- Use HTTPS in production.
- Store admin credentials securely; avoid hardcoded passwords.

---

## Phase 8: Quick Reference – Admin Capabilities

| Capability | Description | Endpoint / UI |
|------------|-------------|---------------|
| View user count | Total and active users | GET /admin/stats, Overview |
| View all users | List with details | GET /admin/users |
| Remove user | Deactivate or delete | POST /admin/users/<id>/deactivate |
| View reports | All user reports | GET /admin/reports |
| Approve report | Set status approved | POST /admin/reports/<id>/approve |
| Reject report | Set status rejected | POST /admin/reports/<id>/reject |
| Delete report | Remove report & file | DELETE /admin/reports/<id>/delete |
| View appointments | All appointments | GET /admin/appointments |
| Reject appointment | Cancel on behalf | POST /admin/appointments/<id>/reject |
| System health | API/DB status | GET /admin/system-health |

---

## Next Steps

1. Review and approve this plan.
2. Implement Phase 1 (DB + Auth).
3. Implement Phase 2 (Admin API).
4. Implement Phase 3 (Admin UI).
5. Test end-to-end and fix any issues.
