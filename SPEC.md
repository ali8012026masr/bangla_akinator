# Project Specification: Bangla Akinator (বাংলা জ্বিন)

## 1. Product Overview
Bangla Akinator is an intelligent 20-questions style guessing game tailored specifically for Bengali culture and Bangladeshi public figures (writers, cricketers, musicians, actors, politicians, and historical icons).

The game engine operates on:
1. **Categorical Likelihood Model & Bayesian Updating:** Computes character posteriors via log-scores to avoid numerical underflow.
2. **Shannon Entropy & Expected Information Gain:** Selects questions that maximize expected uncertainty reduction across all 5 user answers.
3. **Session Persistence:** State saved in MongoDB with TTL expiry.
4. **Moderated Self-Learning Loop:** Failed guesses allow users to suggest personalities into a `pending_review` pipeline.

## 2. Supported Platforms
- **Android:** Primary production deployment target.
- **Flutter Web:** Secondary target for development, rapid testing, and admin verification.

## 3. Answer Values & Model
Users have 5 possible answers:
- `YES`: হ্যাঁ
- `PROBABLY_YES`: সম্ভবত হ্যাঁ
- `UNKNOWN`: জানি না
- `PROBABLY_NO`: সম্ভবত না
- `NO`: না

Character facts in database are verified boolean values (`true`, `false`) or unknown/missing (`None`).

## 4. API Specification Summary

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/ready` | Readiness check including MongoDB connection status |
| `POST` | `/api/start-game` | Initiates game session & returns first question |
| `POST` | `/api/answer` | Submits answer, evaluates likelihoods, returns next question or guess |
| `POST` | `/api/guess-feedback` | Confirms if Genie's guess was correct (`won`) or wrong (`asking` / `defeated`) |
| `POST` | `/api/contributions` | Submits missing character after defeat for moderation review |
| `GET` | `/api/game-state` | Optional session state recovery |
| `POST` | `/api/game/abandon` | Explicit session cleanup |

## 5. Game State Machine

```
READY
  -> ASKING
  -> GUESS_PENDING
       -> WON (user confirms correct guess)
       -> ASKING (user rejects guess, useful questions remain)
       -> DEFEATED (user rejects guess, hard limits/questions exhausted)
  -> CONTRIBUTION_PENDING (user submits name after defeat)
  -> FINISHED
```

## 6. Data Integrity & Content Rules
- Launch with 10–20 thoroughly curated and verified characters during development.
- Expand to 100–150 verified characters for V1.
- All characters must be unique by `normalized_name`.
- Any crowdsourced submissions are marked `status: "pending_review"` and must be audited before publication.
