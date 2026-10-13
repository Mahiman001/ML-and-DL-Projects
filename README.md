# Big Five Personality Classifier

A machine learning web application that predicts Big Five (OCEAN) personality trait scores from a 50-question questionnaire. Built with Python, Scikit-learn, FastAPI, Streamlit, and Docker.

## Live Demo

- **Website:** [https://personality-frontend.onrender.com/](https://personality-frontend.onrender.com/)
- **Backend API:** [https://personality-api-010l.onrender.com/](https://personality-api-010l.onrender.com/)
- **API Documentation:** [https://personality-api-010l.onrender.com/docs](https://personality-api-010l.onrender.com/docs)

## Features

- 50-question personality questionnaire with ratings from 1 to 5.
- Prediction of five personality trait scores.
- Interactive Streamlit interface.
- FastAPI prediction endpoint with input validation.
- Trained model loaded using Joblib.
- SQLite-based questionnaire progress storage.
- Dockerized frontend and backend.
- Cloud deployment using Render.

## Tech Stack

- **Language:** Python
- **Machine Learning:** Scikit-learn, NumPy, Pandas
- **Backend:** FastAPI, Uvicorn, Pydantic
- **Frontend:** Streamlit
- **Model Serialization:** Joblib
- **Database:** SQLite
- **Containerization:** Docker, Docker Compose
- **Deployment:** Render
- **Version Control:** Git and GitHub

## Big Five Personality Traits

- **Openness:** Curiosity and openness to new experiences.
- **Conscientiousness:** Organization and self-discipline.
- **Extraversion:** Sociability and outgoing behavior.
- **Agreeableness:** Cooperation and consideration for others.
- **Neuroticism:** Tendency toward negative emotional responses.

These scores are simplified personality indicators, not psychological diagnoses.

## Machine Learning Approach

This project uses a **multi-output Linear Regression model** to estimate the five Big Five (OCEAN) trait scores from 50 questionnaire responses.

### Pipeline

1. **Questionnaire preprocessing:** Reverse-score 25 reverse-keyed items using `6 - response`.
2. **Target construction:** Calculate the mean score for Extraversion (E), Agreeableness (A), Conscientiousness (C), and Openness (O). Neuroticism (N) is derived by reverse-scoring the Emotional Stability (ES) score.
3. **Missing-value handling:** Use `SimpleImputer(strategy="median")` to fill missing input values.
4. **Model training:** Train `LinearRegression()` to predict all five target scores.
5. **Evaluation:** Split the dataset into 80% training and 20% testing data, using `random_state=42`.

### Important Evaluation Limitation

The target scores are calculated from the same questionnaire responses supplied as model inputs. Therefore, the model learns to approximate an existing scoring formula. Strong test performance does not independently validate personality prediction or establish psychological validity.

### Input Features

- 50 questionnaire features.
- Each response is rated from 1 to 5.
- Feature names follow the questionnaire's trait-based naming convention, such as `EXT1`, `EST1`, `AGR1`, `CSN1`, and `OPN1`.

### Prediction Targets

The model predicts five continuous trait scores:

- Extraversion (E)
- Neuroticism (N)
- Agreeableness (A)
- Conscientiousness (C)
- Openness (O)

### Implementation

1. Load and inspect the personality dataset.
2. Clean and prepare questionnaire features and target values.
3. Split the data into training and testing sets.
4. Train a regression model to predict the five trait scores.
5. Evaluate predictions using regression metrics.
6. Serialize the trained model using Joblib.
7. Load the saved model in the prediction module.
8. Use the model to generate predictions through the FastAPI backend.

The deployed application loads the saved model from `MODELS/personality_baseline.joblib`, avoiding model training every time the API starts.

> **Note:** The exact estimator configuration, preprocessing steps, and evaluation results should be documented from the actual training code and evaluation outputs. Model quality should be verified for data leakage before reporting performance metrics.

## Architecture

```text
User
 |
 v
Streamlit Frontend
 |
 | HTTP POST /predict
 v
FastAPI Backend
 |
 v
Pydantic Request Validation
 |
 v
Prediction Module
 |
 v
Saved ML Model
(personality_baseline.joblib)
 |
 v
Five Personality Trait Scores
 |
 v
Results in Streamlit
```

The frontend and backend run as separate services. The frontend sends questionnaire answers to the backend through the `API_URL` environment variable.

## Project Structure

## Project Structure

```text
Personality-Prediction-ML/
├── app/
│   ├── main.py
│   └── streamlit_app.py
├── DATA/
│   ├── raw/
│   └── processed/
├── MODELS/
│   └── personality_baseline.joblib
├── notebooks/
│   ├── 01_dataset_inspection_and_cleaning.ipynb
│   └── 02_model_training.ipynb
├── src/
│   ├── __init__.py
│   ├── data.py
│   └── predict.py
├── .gitignore
├── Dockerfile.backend
├── Dockerfile.frontend
├── compose.yaml
├── requirements.txt
└── README.md
```

## Run Locally with Docker

### Prerequisites

- Git
- Docker Desktop with Docker Compose

### 1. Clone the repository

```bash

git clone https://github.com/Mahiman001/Personality-Prediction-ML.git
cd Personality-Prediction-ML

```

### 2. Start the application

```bash
docker compose up --build -d
```

### 3. Access the services

- Frontend: [http://localhost:8501](http://localhost:8501)
- Backend: [http://localhost:8000](http://localhost:8000)
- API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Stop the services

```bash
docker compose down
```

## API Reference

### `POST /predict`

Accepts 50 questionnaire answers and returns predicted OCEAN trait scores with interpretations.

**Endpoint:** `https://personality-api-010l.onrender.com/predict`

**Request validation**

- Requires an `answers` object containing exactly the 50 expected questionnaire fields.
- Each answer must be a number between 1 and 5.
- Missing fields, unexpected fields, and invalid values are rejected.
- Invalid requests return HTTP `422` through FastAPI validation.

**Example request**

```json
{
  "answers": {
    "EXT1": 3,
    "EXT2": 4,
    "EXT3": 2
  }
}
```

The example above is abbreviated. A valid request must include all 50 fields.

**Response format**

```json
{
  "personality_scores": {
    "E": 3.2,
    "A": 3.5,
    "C": 3.8,
    "O": 4.0,
    "N": 2.7
  },
  "interpretations": {
    "E": "Moderate",
    "A": "Moderate",
    "C": "Moderate",
    "O": "High",
    "N": "Moderate"
  }
}
```

_The numerical scores and interpretations above are illustrative, not actual API output._

**Interactive API documentation:** [Open Swagger UI](https://personality-api-010l.onrender.com/docs)

Use Swagger UI to inspect the full request schema and test the endpoint.

## Deployment

The application is deployed on Render using two separate Docker services:

- **Backend:** FastAPI serves prediction requests.
- **Frontend:** Streamlit provides the questionnaire and displays results.

The frontend connects to the backend through the `API_URL` environment variable.

```text
API_URL=https://personality-api-010l.onrender.com/predict
```

Free-tier services may sleep after inactivity, causing slower initial responses. Local SQLite data should not be considered permanently persistent on an ephemeral deployment.

## Limitations

- Predictions are estimates, not psychological diagnoses.
- Model performance should be validated carefully before drawing conclusions about accuracy.
- Results depend on the questionnaire and the quality of the training data.
- The free deployment is intended for demonstration and learning, not for handling sensitive personal information.

## Future Improvements

### 1. Master Streamlit

- Build reusable UI components and improve application structure.
- Master session state, forms, callbacks, and multipage navigation.
- Improve questionnaire progress persistence and error handling.
- Add interactive charts and clearer personality score visualizations.
- Learn caching, performance optimization, and efficient data loading.
- Improve responsive layouts and user experience.

### 2. Master FastAPI

- Build structured request and response schemas with Pydantic.
- Organize routes, services, and prediction logic into maintainable modules.
- Implement centralized exception handling and structured logging.
- Add automated API tests using Pytest and FastAPI's test client.
- Learn dependency injection, middleware, authentication, and API versioning.
- Improve input validation, API reliability, and response consistency.

### 3. Master Docker

- Understand Dockerfiles, image layers, caching, and build contexts.
- Learn multi-stage builds and smaller, more efficient images.
- Master Docker Compose networking, service discovery, and volumes.
- Add container health checks and improve startup reliability.
- Learn environment configuration, logging, and container troubleshooting.
- Understand image tagging, versioning, and secure container practices.

### 4. Production Deployment

- Improve deployment reliability on Render.
- Learn environment-specific configuration and secrets management.
- Add CI/CD workflows using GitHub Actions.
- Implement health checks, monitoring, and structured logs.
- Understand persistent databases, backups, and production data management.
- Learn how to diagnose cold starts, API timeouts, and failed deployments.

### 5. Machine Learning Engineering

- Verify preprocessing and evaluation to prevent data leakage.
- Compare suitable regression algorithms using reliable validation methods.
- Document MAE, RMSE, and R² for each target trait.
- Build reproducible training and evaluation pipelines.
- Add model versioning and prediction monitoring.
- Separate model training, evaluation, and inference cleanly.

### 6. Testing and Code Quality

- Add unit tests for preprocessing and prediction functions.
- Test valid requests, missing fields, and out-of-range answers.
- Add integration tests for the frontend-to-backend prediction flow.
- Use formatting, linting, and automated checks.
- Document setup, troubleshooting, and deployment procedures.

## Author

**Mahiman Sharma**

B.Tech — Computer Science and Engineering (AI & Data Science)

GitHub: [Mahiman001](https://github.com/Mahiman001)

---

Built to practice machine learning, API development, containerization, and cloud deployment.
