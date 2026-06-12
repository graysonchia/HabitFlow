[README.md](https://github.com/user-attachments/files/28872726/README.md)
# HabitFlow 📊

A full-stack habit and mood tracking application built as a data analytics portfolio project. HabitFlow demonstrates end-to-end data engineering, backend development, and data science skills — from database design to machine learning.

---

## Project Overview

HabitFlow allows users to log daily habits and mood scores, track streaks, and receive insights about their behavioral patterns. The project was built primarily to generate a rich, realistic dataset suitable for advanced data analytics, machine learning, and business intelligence work.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Database | PostgreSQL 18 |
| ORM & Migrations | SQLAlchemy 2.0, Alembic |
| Authentication | JWT (python-jose, passlib) |
| Data Analysis | Pandas, NumPy, Matplotlib, Seaborn |
| Machine Learning | Scikit-learn (Logistic Regression, K-Means) |
| Seed Data | Faker, NumPy random distributions |
| Version Control | Git, GitHub |

---

## Project Structure

```
HabitFlow/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic v2 schemas
│   │   ├── routers/         # FastAPI route handlers
│   │   └── utils/           # Streak calculator logic
│   ├── alembic/             # Database migrations
│   ├── seed_data.py         # Synthetic data generator
│   └── requirements.txt
└── analytics/
    ├── habitflow_analysis.ipynb   # Full analytics notebook
    └── charts/                    # Exported visualisations
```

---

## Database Schema

Four relational tables designed for analytics performance:

```sql
users     → user profiles, age groups, premium status
habits    → habit definitions per user with categories
checkins  → daily completion logs with mood scores (main analytics table)
streaks   → consecutive completion sequences per habit
```

**Indexes** on `checkins(user_id, date)`, `checkins(habit_id, date)`, and `streaks(user_id)` optimise analytical query performance across 395,000+ rows.

---

## Dataset

The seed data generator (`seed_data.py`) produces a realistic synthetic dataset using statistically modelled behavioural patterns:

| Table | Rows |
|---|---|
| users | 500 |
| habits | 2,528 |
| checkins | 395,470 |
| streaks | 81,760 |

**Behavioural patterns modelled:**
- Weekday completion rate: 70%, weekend: 50%
- Mood scores normally distributed (μ=7.2 when completed, μ=5.1 when missed)
- 15% high performers (90% completion, mood avg 8+)
- 20% churners who stop between day 30–90 (simulates real user dropout)

---

## Analytics Notebook

`analytics/habitflow_analysis.ipynb` contains 8 sections demonstrating a full data analytics workflow:

### Section 1 — Database Connection & Data Loading
Connects directly to PostgreSQL via SQLAlchemy. Loads all 4 tables into pandas DataFrames.

### Section 2 — Exploratory Data Analysis
- User distribution by age group
- Habit distribution by category
- Mood score distribution with KDE
- Daily checkin volume over 180 days

### Section 3 — Cohort Retention Analysis
Weekly cohort heatmap showing retention at weeks 1, 2, 4, 8, and 12 post-signup.

![Cohort Retention Heatmap](analytics/charts/cohort_retention_heatmap.png)

### Section 4 — Habit-Mood Correlation
Scatter plot with regression line showing the relationship between habit completion rate and average mood score. Pearson r and p-value annotated.

![Habit Mood Correlation](analytics/charts/habit_mood_correlation.png)

### Section 5 — Streak Analysis
- Current streak length distribution
- Average streak by habit category
- Streak length vs mood score relationship

### Section 6 — Churn Prediction (Logistic Regression)
Binary classification model predicting user churn from behavioural features:
- Days since last checkin
- 30-day completion rate
- Average mood score
- Current streak length
- Total habits tracked

![Churn Confusion Matrix](analytics/charts/churn_confusion_matrix.png)
![Feature Importance](analytics/charts/churn_feature_importance.png)

### Section 7 — User Segmentation (K-Means Clustering)
K-Means clustering (k=3) with PCA dimensionality reduction identifies three user personas: Consistent Performers, Casual Users, and At-Risk Users.

![User Segmentation PCA](analytics/charts/user_segmentation_pca.png)

### Section 8 — Stakeholder Insights
Five plain-English insights written for a non-technical business audience.

---

## API Endpoints

The FastAPI backend exposes a full REST API with JWT authentication:

```
POST   /users/register        Create account, returns JWT token
POST   /users/login           Authenticate, returns JWT token
GET    /users/me              Current user profile

POST   /habits                Create a habit
GET    /habits                List all habits
PUT    /habits/{id}           Update a habit
DELETE /habits/{id}           Soft delete a habit

POST   /checkins              Log a daily checkin with mood score
GET    /checkins?days=30      Recent checkins
GET    /checkins/today        Today's habits and completion status
GET    /checkins/streak/{id}  Current streak for a habit
GET    /checkins/summary      Completion rate and mood summary
```

Interactive API documentation available at `/docs` (Swagger UI).

---

## Skills Demonstrated

**SQL & Database Design**
- Relational schema with foreign keys and constraints
- Performance indexes for analytical queries
- Alembic migrations with reversible upgrade/downgrade

**Python & Data Engineering**
- Async FastAPI backend with SQLAlchemy ORM
- Statistically modelled synthetic data generation
- Pandas data manipulation across 395,000+ rows

**Data Analysis & Visualisation**
- Cohort retention analysis
- Correlation analysis with statistical significance testing
- Time-series analysis of behavioural patterns

**Machine Learning**
- Binary classification (churn prediction) with Logistic Regression
- Unsupervised clustering (user segmentation) with K-Means
- PCA dimensionality reduction for visualisation
- Model evaluation with confusion matrix and classification report

**Software Engineering**
- RESTful API design with authentication
- Environment-based configuration management
- Git version control with clean commit history

---

## Running Locally

**Prerequisites:** Python 3.11+, PostgreSQL 18

```bash
# Clone the repository
git clone https://github.com/graysonchia/HabitFlow.git
cd HabitFlow

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
# Create backend/.env with your PostgreSQL credentials:
# DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/habitflow

# Run database migrations
alembic upgrade head

# Generate seed data
python seed_data.py

# Start the API server
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to explore the API.

For the analytics notebook:
```bash
cd ../analytics
jupyter notebook habitflow_analysis.ipynb
```

---

## Author

**Grayson Chia**  
Asia Pacific University of Technology and Innovation (APU)  
Built as a data analytics portfolio project for university applications and internship opportunities.
