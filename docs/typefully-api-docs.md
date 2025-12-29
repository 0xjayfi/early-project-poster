# Typefully API Documentation

Source: https://typefully.com/docs/api

## Authentication

All requests require Bearer token authentication in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```

API keys are generated from https://typefully.com/settings/api and inherit user permissions.

---

## Endpoints

### Users

#### GET /v2/me
Retrieve authenticated user details including email, name, signup date, and profile image.

---

### Social Sets (Accounts)

#### GET /v2/social-sets
List all accessible accounts with pagination support.

**Response includes:**
- `results`: Array of social sets
- `count`: Total count
- `limit`, `offset`: Pagination info
- `next`, `previous`: Pagination URLs

#### GET /v2/social-sets/{social_set_id}/
Get detailed account info including all configured platforms (X, LinkedIn, Mastodon, Threads, Bluesky).

---

### Drafts Management

#### GET /v2/social-sets/{social_set_id}/drafts
List drafts with filtering and sorting (default: most recent first).

#### POST /v2/social-sets/{social_set_id}/drafts
Create a new draft with content for one or more social media platforms.

**Request Body:**
```json
{
  "platforms": {
    "x": {
      "enabled": true,
      "posts": [
        {"text": "Your tweet content here"}
      ]
    }
  },
  "publish_at": "2024-01-15T17:00:00+08:00",
  "draft_title": "Optional internal title",
  "tags": [],
  "share": false
}
```

**Parameters:**
- `platforms` (required) - Configuration object for each platform:
  - `x`: X/Twitter - requires `enabled: true` and `posts` array with text objects
  - `linkedin`: LinkedIn content
  - `mastodon`: Mastodon content
  - `threads`: Threads content
  - `bluesky`: Bluesky content
- `publish_at` (optional) - Publishing timing:
  - `"now"` - Publish immediately
  - `"next-free-slot"` - Auto-schedule to next available slot
  - ISO 8601 datetime with timezone (e.g., `"2024-01-15T17:00:00+08:00"`)
- `draft_title` (optional) - Internal organizational title only
- `tags` (optional) - Tag slugs for organization (must exist in social set)
- `share` (optional, default: false) - Generate public share URL

#### GET /v2/social-sets/{social_set_id}/drafts/{draft_id}
Retrieve specific draft details.

#### PATCH /v2/social-sets/{social_set_id}/drafts/{draft_id}
Update draft using partial semantics.

---

## Rate Limiting & Pagination

- Per-user and per-social-set rate limiting (429 response when exceeded)
- Pagination uses limit-offset with defaults: `limit=10` (max 50), `offset=0`
- Responses include: `results`, `count`, `limit`, `offset`, `next`, `previous` fields

---

## Compliance Notes

- Make sure to adhere to X automation rules and general X rules when scheduling content
- API is meant for personal automations and workflows, not for public app distribution

---

*Document updated: December 2024*
