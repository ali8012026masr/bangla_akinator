# API Contract: Bangla Akinator

Base URL (Dev): `http://localhost:8000`
Router Prefix: `/api`

All responses returning text must support UTF-8 encoded Bengali characters.

---

## 1. System Health

### GET `/health`
Simple liveness probe.
- **Response `200 OK`**:
  ```json
  {
    "status": "ok"
  }
  ```

### GET `/ready`
Readiness probe that checks connection to the MongoDB instance.
- **Response `200 OK`**:
  ```json
  {
    "status": "ready",
    "database": "connected"
  }
  ```
- **Response `503 Service Unavailable`**:
  ```json
  {
    "status": "unhealthy",
    "database": "disconnected"
  }
  ```

---

## 2. Game Endpoints

### POST `/api/start-game`
Creates a new game session in MongoDB and returns the first question determined by Expected Information Gain.

- **Request:** Empty body or `{}`
- **Response `201 Created`**:
  ```json
  {
    "session_id": "c1f7a4e8-8b9a-4e2e-bb97-2a4c1074e532",
    "status": "asking",
    "question": {
      "question_code": "q_is_real_person",
      "text_bn": "এই ব্যক্তি কি বাস্তব মানুষ?",
      "question_number": 1
    }
  }
  ```

---

### POST `/api/answer`
Submits an answer for the active question. Recomputes candidate log-weights.

- **Request Body**:
  ```json
  {
    "session_id": "c1f7a4e8-8b9a-4e2e-bb97-2a4c1074e532",
    "question_code": "q_is_real_person",
    "answer": "YES"
  }
  ```
  `answer` enum: `["YES", "PROBABLY_YES", "UNKNOWN", "PROBABLY_NO", "NO"]`

- **Response `200 OK` (Next Question)**:
  ```json
  {
    "status": "asking",
    "next_question": {
      "question_code": "q_is_cricketer",
      "text_bn": "এই ব্যক্তি কি ক্রিকেটার?",
      "question_number": 2
    },
    "guess": null
  }
  ```

- **Response `200 OK` (Guess Proposed)**:
  ```json
  {
    "status": "guess_pending",
    "next_question": null,
    "guess": {
      "character_id": "67210e7b8c0e2a3b1d4e5f60",
      "name_bn": "সাকিব আল হাসান",
      "categories": ["ক্রিকেটার", "ক্রীড়াবিদ"],
      "image_url": null,
      "score": 0.84
    }
  }
  ```

- **Response `200 OK` (Defeat / Exhausted)**:
  ```json
  {
    "status": "defeated",
    "next_question": null,
    "guess": null
  }
  ```

- **Error Responses**:
  - `404 Not Found`: Session does not exist or has expired.
  - `409 Conflict`: Question submitted out of sequence or session not in `asking` state.
  - `422 Unprocessable Entity`: Invalid answer enum value.

---

### POST `/api/guess-feedback`
User response when Genie presents a guess.

- **Request Body**:
  ```json
  {
    "session_id": "c1f7a4e8-8b9a-4e2e-bb97-2a4c1074e532",
    "feedback": "correct"
  }
  ```
  `feedback` enum: `["correct", "wrong"]`

- **Response `200 OK` (Guess was Correct)**:
  ```json
  {
    "status": "won",
    "message_bn": "জ্বিন জিতেছে! 🧞‍♂️"
  }
  ```

- **Response `200 OK` (Guess was Wrong, Game Continues)**:
  ```json
  {
    "status": "asking",
    "next_question": {
      "question_code": "q_is_writer",
      "text_bn": "এই ব্যক্তি কি লেখক বা সাহিত্যিক?",
      "question_number": 7
    },
    "guess": null
  }
  ```

- **Response `200 OK` (Guess was Wrong, No Questions Left)**:
  ```json
  {
    "status": "defeated",
    "message_bn": "আপনি জ্বিনকে হারিয়েছেন!"
  }
  ```

---

### POST `/api/contributions`
Submitted after defeat so users can suggest the personality they were thinking of.

- **Request Body**:
  ```json
  {
    "session_id": "c1f7a4e8-8b9a-4e2e-bb97-2a4c1074e532",
    "name_bn": "তাশরিফ খান",
    "categories": ["সংগীতশিল্পী"]
  }
  ```

- **Response `201 Created`**:
  ```json
  {
    "status": "pending_review",
    "contribution_id": "67210e7b8c0e2a3b1d4e5f61",
    "message_bn": "আপনার প্রস্তাবটি পর্যালোচনার জন্য জমা হয়েছে।"
  }
  ```
