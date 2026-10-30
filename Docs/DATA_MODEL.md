# Data Model: Bangla Akinator

Database: `bangla_akinator`

---

## 1. Collection: `characters`

Stores canonical and curated Bangla figures.

### Schema
```json
{
  "_id": "ObjectId",
  "name_bn": "সাকিব আল হাসান",
  "name_en": "Shakib Al Hasan",
  "normalized_name": "সাকিব আল হাসান",
  "aliases_bn": ["সাকিব"],
  "aliases_en": ["Shakib"],
  "categories": ["ক্রিকেটার", "ক্রীড়াবিদ"],
  "is_real_person": true,
  "is_alive": true,
  "answer_profile": {
    "q_is_real_person": {
      "value": true,
      "confidence": 1.0,
      "source": "editor_verified"
    },
    "q_is_cricketer": {
      "value": true,
      "confidence": 1.0,
      "source": "editor_verified"
    },
    "q_is_writer": {
      "value": false,
      "confidence": 1.0,
      "source": "editor_verified"
    }
  },
  "image_url": null,
  "image_attribution": null,
  "status": "published",
  "created_at": "ISODate",
  "updated_at": "ISODate",
  "times_played": 0,
  "times_guessed_correctly": 0
}
```

### Indexes
- `{ normalized_name: 1 }` (Unique for `status: "published"`)
- `{ status: 1 }`
- `{ categories: 1 }`

---

## 2. Collection: `questions`

Pool of questions used for entropy calculations.

### Schema
```json
{
  "_id": "ObjectId",
  "question_code": "q_is_cricketer",
  "text_bn": "এই ব্যক্তি কি ক্রিকেটার?",
  "text_en": "Is this person a cricketer?",
  "answer_type": "boolean",
  "active": true,
  "order": 10,
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

### Indexes
- `{ question_code: 1 }` (Unique)
- `{ active: 1 }`

---

## 3. Collection: `sessions`

Ephemeral active game sessions with automatic TTL expiry.

### Schema
```json
{
  "_id": "ObjectId",
  "session_id": "c1f7a4e8-8b9a-4e2e-bb97-2a4c1074e532",
  "status": "asking",
  "current_question_code": "q_is_cricketer",
  "asked_question_codes": ["q_is_real_person", "q_is_cricketer"],
  "answer_history": {
    "q_is_real_person": "YES"
  },
  "candidate_log_weights": {
    "67210e7b8c0e2a3b1d4e5f60": -0.10536
  },
  "rejected_character_ids": [],
  "question_count": 1,
  "created_at": "ISODate",
  "updated_at": "ISODate",
  "expires_at": "ISODate"
}
```

### Indexes
- `{ session_id: 1 }` (Unique)
- `{ expires_at: 1 }` (TTL index: `expireAfterSeconds: 0`)

---

## 4. Collection: `contributions`

Community proposed personalities submitted after a Genie defeat.

### Schema
```json
{
  "_id": "ObjectId",
  "session_id": "c1f7a4e8-8b9a-4e2e-bb97-2a4c1074e532",
  "name_bn": "তাশরিফ খান",
  "normalized_name": "তাশরিফ খান",
  "categories": ["সংগীতশিল্পী"],
  "answer_history": {
    "q_is_real_person": "YES",
    "q_is_musician": "YES"
  },
  "status": "pending_review",
  "reviewed_by": null,
  "reviewed_at": null,
  "created_at": "ISODate"
}
```

### Indexes
- `{ status: 1, created_at: -1 }`
- `{ normalized_name: 1 }`
