# 🚀 LaunchPad — AI-Powered Startup Ecosystem Platform

> Built at the AI & Software Hackathon — Space42 Arena, Abu Dhabi 2026

LaunchPad is a full-stack web platform that connects founders and investors through
AI-powered startup evaluations, pitch deck analysis, and ecosystem networking.
Founders get instant AI feedback on their startups. Investors discover and evaluate
opportunities faster. Everyone connects through events and networking.

---

## 📸 Platform Overview

| Role | Key Features |
|---|---|
| **Founder** | Create startup profile, AI evaluation, pitch deck upload & analysis, founder networking |
| **Investor** | Browse startups with AI scores, manage investor profile, discover opportunities |
| **Both** | Create and attend events, JWT-secured access, role-based permissions |

---

## 🧠 AI Features

### 1. Startup Evaluation
Triggered by the founder with one click. Sends startup details to OpenAI GPT-3.5-Turbo
and returns a structured evaluation saved to the database.

**Output:**
- Score out of 100
- Key strengths
- Key weaknesses  
- Actionable improvement suggestions

### 2. Pitch Deck Analysis
Founder uploads a PDF pitch deck. The system extracts text page by page using PyPDF2,
sends it to OpenAI, and returns a detailed analysis.

**Output:**
- Score out of 100
- Overall analysis
- Key insights
- Specific improvements

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND                            │
│         HTML + CSS + Vanilla JavaScript                 │
│   index  signup  login  founder_dashboard               │
│   investor_dashboard  events                            │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP REST API
                      │ Bearer JWT Token
┌─────────────────────▼───────────────────────────────────┐
│                     BACKEND                             │
│                   FastAPI (Python)                      │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   Routers   │  │  Services   │  │      Auth       │ │
│  │  auth       │  │ ai_evaluator│  │  jwt_handler    │ │
│  │  startups   │  │pitch_analyze│  │  dependencies   │ │
│  │  investors  │  │pdf_extractor│  │  RBAC           │ │
│  │  evaluations│  └─────────────┘  └─────────────────┘ │
│  │  pitch_decks│                                        │
│  │  events     │  ┌─────────────────────────────────┐  │
│  │  connections│  │         OpenAI API               │  │
│  └─────────────┘  │      GPT-3.5-Turbo              │  │
│                   └─────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────┘
                      │ SQLAlchemy ORM
┌─────────────────────▼───────────────────────────────────┐
│                    DATABASE                             │
│                  SQLite (app.db)                        │
│                                                         │
│  users → startups → evaluations                        │
│       ↘ investors   pitch_decks                        │
│       ↘ events                                         │
│       ↘ connections                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema
```
users
├── id (PK)
├── name
├── email (unique)
├── hashed_password
├── role (founder | investor)
└── created_at

startups
├── id (PK)
├── name
├── description
├── industry
├── stage
├── website
├── founder_id (FK → users.id)
└── created_at

investors
├── id (PK)
├── firm_name
├── focus_areas
├── ticket_size
├── bio
├── user_id (FK → users.id)
└── created_at

evaluations
├── id (PK)
├── startup_id (FK → startups.id)
├── score
├── strengths
├── weaknesses
├── suggestions
└── created_at

pitch_decks
├── id (PK)
├── startup_id (FK → startups.id)
├── file_path
├── extracted_text
├── analysis
├── score
└── created_at

events
├── id (PK)
├── title
├── description
├── event_date
├── location
├── created_by (FK → users.id)
└── created_at

connections
├── id (PK)
├── requester_id (FK → users.id)
├── receiver_id (FK → users.id)
├── status (pending | accepted | rejected)
└── created_at
```

---

## 🔐 Authentication & RBAC

JWT-based authentication with role-based access control enforced at the API level.
```
POST /auth/signup  →  Hash password (bcrypt) → Save user → Return user info
POST /auth/login   →  Verify password → Create JWT (user_id + role + expiry)
                   →  Frontend saves token to localStorage
                   →  Every request sends: Authorization: Bearer <token>
                   →  Backend verifies token → checks role → allows or blocks
```

| Action | Founder | Investor |
|---|---|---|
| Create / edit startup | ✅ | ❌ 403 |
| Create / edit investor profile | ❌ 403 | ✅ |
| Trigger AI evaluation | ✅ own only | ❌ 403 |
| View all startups & evaluations | ✅ | ✅ |
| Upload & analyze pitch deck | ✅ own only | ❌ 403 |
| Create events | ✅ | ✅ |
| Send connection requests | ✅ | ❌ 403 |

---

## 📡 API Reference

### Authentication
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/auth/signup` | Public | Register new account |
| POST | `/auth/login` | Public | Login and receive JWT token |
| GET | `/auth/me` | Any | Get current user info |

### Startups
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/startups/` | Founder | Create startup profile |
| GET | `/startups/` | Any | Get all startups |
| GET | `/startups/{id}` | Any | Get single startup |
| PUT | `/startups/{id}` | Founder (owner) | Update startup |
| DELETE | `/startups/{id}` | Founder (owner) | Delete startup |

### Investors
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/investors/` | Investor | Create investor profile |
| GET | `/investors/` | Any | Get all investors |
| GET | `/investors/{id}` | Any | Get single investor |
| PUT | `/investors/{id}` | Investor (owner) | Update profile |
| DELETE | `/investors/{id}` | Investor (owner) | Delete profile |

### AI Evaluation
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/startups/{id}/evaluate` | Founder (owner) | Trigger AI evaluation |
| GET | `/startups/{id}/evaluation` | Any | Get latest evaluation |
| GET | `/startups/{id}/evaluations` | Any | Get all evaluations |

### Pitch Decks
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/startups/{id}/upload-pitch-deck` | Founder (owner) | Upload PDF |
| POST | `/startups/{id}/analyze-pitch-deck` | Founder (owner) | Trigger AI analysis |
| GET | `/startups/{id}/pitch-deck` | Any | Get analysis result |

### Events
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/events/` | Any | Create event |
| GET | `/events/` | Any | Get all events |
| GET | `/events/{id}` | Any | Get single event |
| PUT | `/events/{id}` | Creator only | Update event |
| DELETE | `/events/{id}` | Creator only | Delete event |

### Networking
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/connections/` | Founder | Send connection request |
| GET | `/connections/me` | Any | Get my connections |
| GET | `/connections/pending` | Any | Get pending requests |
| PUT | `/connections/{id}/respond` | Receiver | Accept or reject |
| GET | `/connections/all` | Any | Get all accepted connections |
| DELETE | `/connections/{id}` | Requester | Cancel request |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend Framework | FastAPI (Python) | REST API with auto Swagger docs |
| Database | SQLite + SQLAlchemy | Persistent storage with ORM |
| Authentication | JWT (python-jose) | Stateless token-based auth |
| Password Security | bcrypt (passlib) | Secure password hashing |
| AI / LLM | OpenAI GPT-3.5-Turbo | Startup evaluation + pitch analysis |
| PDF Processing | PyPDF2 | Extract text from pitch deck PDFs |
| Frontend | HTML + CSS + JavaScript | Lightweight, no framework needed |
| API Testing | Swagger UI (built-in) | Interactive endpoint testing |
| Environment | python-dotenv | Secure config management |

---

## 📁 Project Structure
```
hackathon-mvp/
│
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # SQLite connection and session factory
│   ├── models.py                # All 7 SQLAlchemy table definitions
│   ├── schemas.py               # All Pydantic request/response schemas
│   │
│   ├── auth/
│   │   ├── jwt_handler.py       # JWT creation and verification
│   │   └── dependencies.py      # Route protection and RBAC enforcement
│   │
│   ├── routers/
│   │   ├── auth.py              # Signup and login endpoints
│   │   ├── startups.py          # Startup CRUD endpoints
│   │   ├── investors.py         # Investor CRUD endpoints
│   │   ├── evaluations.py       # AI evaluation endpoints
│   │   ├── pitch_decks.py       # PDF upload and analysis endpoints
│   │   ├── events.py            # Events CRUD endpoints
│   │   └── connections.py       # Founder networking endpoints
│   │
│   ├── services/
│   │   ├── ai_evaluator.py      # OpenAI startup evaluation logic
│   │   ├── pitch_analyzer.py    # OpenAI pitch deck analysis logic
│   │   └── pdf_extractor.py     # PyPDF2 text extraction utility
│   │
│   └── uploads/                 # Stored pitch deck PDF files
│
├── frontend/
│   ├── index.html               # Landing page
│   ├── signup.html              # Registration page
│   ├── login.html               # Login page
│   ├── founder_dashboard.html   # Founder workspace
│   ├── investor_dashboard.html  # Investor discovery page
│   ├── events.html              # Events and networking page
│   │
│   ├── css/
│   │   └── style.css            # Global stylesheet
│   │
│   └── js/
│       ├── auth.js              # Auth logic and JWT management
│       ├── startups.js          # Startup CRUD and investor list
│       ├── evaluations.js       # AI evaluation trigger and display
│       ├── pitch_decks.js       # PDF upload and analysis display
│       ├── investors.js         # Investor profile and startup discovery
│       ├── events.js            # Events CRUD
│       └── connections.js       # Founder networking logic
│
├── app.db                       # SQLite database (auto-created)
├── .env                         # Environment variables (not committed)
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- An OpenAI API key

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/hackathon-mvp.git
cd hackathon-mvp
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=supersecretjwtkey123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 5. Start the backend server
```bash
uvicorn app.main:app --reload
```

The server starts at `http://127.0.0.1:8000`

### 6. Open the frontend
Open `frontend/index.html` in your browser directly.

Or use VS Code Live Server extension for a better experience.

### 7. Explore the API docs
Visit `http://127.0.0.1:8000/docs` for interactive Swagger UI.

---

## 🧪 Testing the API

### Using Swagger UI
1. Go to `http://127.0.0.1:8000/docs`
2. Call `POST /auth/signup` to create an account
3. Call `POST /auth/login` to get your JWT token
4. Click the 🔒 **Authorize** button
5. Paste your token and click Authorize
6. All endpoints are now accessible

### Quick Demo Flow
```
1. Signup as founder   →  POST /auth/signup  (role: founder)
2. Signup as investor  →  POST /auth/signup  (role: investor)
3. Login as founder    →  POST /auth/login
4. Create startup      →  POST /startups/
5. Evaluate startup    →  POST /startups/1/evaluate
6. Upload pitch deck   →  POST /startups/1/upload-pitch-deck
7. Analyze pitch deck  →  POST /startups/1/analyze-pitch-deck
8. Login as investor   →  POST /auth/login
9. View startup scores →  GET /startups/
10. Create event       →  POST /events/
```

---

## 🔑 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `SECRET_KEY` | JWT signing secret | Required |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | 60 |

---

## 🚀 Future Improvements

- [ ] Migrate from SQLite to PostgreSQL for production
- [ ] Deploy backend on AWS EC2 or Railway
- [ ] Add email notifications for connection requests and evaluations
- [ ] Implement search and filter for startups by industry and stage
- [ ] Add a messaging system between founders and investors
- [ ] Integrate with LinkedIn for profile import
- [ ] Add support for multiple startup profiles per founder
- [ ] Implement refresh tokens for better session management
- [ ] Add file size validation and virus scanning for PDF uploads
- [ ] Build a mobile-responsive PWA version

---

## 👤 Author

Built with ❤️ at the **AI & Software Hackathon**
📍 IFAVH HUB — Space42 Arena, Abu Dhabi 2026

---

## 📄 License

This project is built for hackathon demonstration purposes.