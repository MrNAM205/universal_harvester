# OmniVeroBrix Harvester Schema (v1.0)
*(This is the official schema for all harvested documents.)*

```json
{
  "id": "string",                     // UUIDv4
  "source": "string",                 // 'pdf', 'image', 'html', 'email', 'chat', 'screenshot', etc.
  "ingested_at": "ISO8601 timestamp",

  "metadata": {
    "filename": "string | null",
    "filepath": "string | null",
    "content_type": "string | null",  // mime type
    "detected_language": "string | null",
    "page_count": "number | null",
    "hash_sha256": "string"
  },

  "classification": {
    "document_type": "string",        // 'bill', 'statement', 'notice', 'letter', 'remittance_coupon', etc.
    "confidence": "number",           // 0–1
    "tags": ["string"]
  },

  "parties": {
    "sender": {
      "name": "string | null",
      "address": "string | null",
      "email": "string | null",
      "phone": "string | null"
    },
    "recipient": {
      "name": "string | null",
      "address": "string | null",
      "email": "string | null",
      "phone": "string | null"
    },
    "other_parties": [
      {
        "role": "string",
        "name": "string | null",
        "address": "string | null"
      }
    ]
  },

  "dates": {
    "document_date": "ISO8601 | null",
    "due_date": "ISO8601 | null",
    "statement_period_start": "ISO8601 | null",
    "statement_period_end": "ISO8601 | null",
    "extracted_dates": [
      {
        "label": "string",
        "value": "ISO8601"
      }
    ]
  },

  "financials": {
    "amount_due": "number | null",
    "previous_balance": "number | null",
    "new_charges": "number | null",
    "payments_received": "number | null",
    "line_items": [
      {
        "description": "string",
        "amount": "number | null",
        "date": "ISO8601 | null"
      }
    ]
  },

  "remittance": {
    "account_number": "string | null",
    "routing_number": "string | null",
    "coupon_code": "string | null",
    "payment_address": "string | null",
    "barcode_data": "string | null",
    "scanline": "string | null"
  },

  "entities": [
    {
      "type": "string",               // 'person', 'org', 'address', 'amount', 'date', etc.
      "value": "string",
      "context": "string | null",
      "page": "number | null"
    }
  ],

  "text_blocks": [
    {
      "page": "number",
      "text": "string",
      "bbox": [ "number", "number", "number", "number" ] | null
    }
  ],

  "full_text": "string",

  "timeline": [
    {
      "event": "string",
      "date": "ISO8601 | null",
      "confidence": "number"
    }
  ],

  "next_actions": [
    {
      "action": "string",
      "reason": "string",
      "confidence": "number"
    }
  ]
}
```

# Schema Philosophy (Why It’s Designed This Way)

### ✔ 1. Every document becomes a structured object
No matter the source — PDF, screenshot, HTML, email — the output is identical.

### ✔ 2. The Corpus Layer can map statutes to fields
Because dates, parties, amounts, and document types are normalized.

### ✔ 3. The Sovereign Thought Engine can reason over it
The schema includes:
- extracted entities
- timeline events
- next‑action hypotheses

### ✔ 4. The Remittance Engine can parse coupons
The `remittance` block is standardized across all bill types.

### ✔ 5. The Cockpit can display everything cleanly
The dashboard can show:
- parties
- dates
- amounts
- extracted text
- timeline
- next actions

without needing to re‑parse anything.
