# Morphiq Skills Pipeline

## Overview

The four Morphiq skills form a sequential pipeline. Each skill produces structured JSON output that the next skill consumes as input. This document defines the exact data contracts between them.

```
morphiq-scan → morphiq-rank → morphiq-build → morphiq-track
                  ↑                                    │
                  └────────────────────────────────────┘
```

---

## 1. morphiq-scan → morphiq-rank

### Contract: Scan Report

morphiq-scan produces a **scan report** — a full AI visibility audit of one domain. morphiq-rank consumes this report to prioritize issues.

```json
{
  "schema_version": "1.0",
  "generated_at": "2025-03-25T14:30:00Z",
  "domain": "example.com",
  "pages_scanned": 12,
  "overall_score": 62,
  "scores": {
    "agentic_readiness": 26,
    "content_quality": 14,
    "chunking_retrieval": 10,
    "query_fanout": 6,
    "policy_files": 6
  },
  "scores_max": {
    "agentic_readiness": 45,
    "content_quality": 20,
    "chunking_retrieval": 15,
    "query_fanout": 10,
    "policy_files": 10
  },
  "pages": [
    {
      "url": "https://example.com/product",
      "page_type": "product",
      "title": "Example Product — Best Widget for Teams",
      "score": 58,
      "issues": [
        {
          "id": "agentic-missing-product-schema",
          "category": "agentic_readiness",
          "severity": "high",
          "summary": "No Product schema detected",
          "detail": "This product page has no JSON-LD Product markup. LLMs cannot extract structured product attributes.",
          "affected_element": null,
          "remediation_hint": "Add Product schema with name, description, offers, and aggregateRating"
        },
        {
          "id": "content-thin-faq",
          "category": "content_quality",
          "severity": "medium",
          "summary": "No FAQ section found",
          "detail": "Product page has no FAQ content. AI agents frequently look for Q&A pairs when answering comparison queries.",
          "affected_element": null,
          "remediation_hint": "Add 5-8 FAQs covering common purchase/comparison questions"
        }
      ],
      "schema_detected": ["Organization"],
      "schema_missing": ["Product", "FAQPage", "BreadcrumbList"],
      "meta": {
        "title_length": 42,
        "description_length": 148,
        "og_image": true,
        "canonical": "https://example.com/product",
        "h1_count": 1,
        "heading_hierarchy_valid": true,
        "word_count": 620
      }
    }
  ],
  "policy_files": {
    "robots_txt": {
      "exists": true,
      "allows_ai_crawlers": false,
      "blocked_agents": ["GPTBot", "Google-Extended"],
      "issues": [
        {
          "id": "policy-blocks-gptbot",
          "category": "policy_files",
          "severity": "high",
          "summary": "robots.txt blocks GPTBot",
          "detail": "GPTBot is disallowed. Content will not be indexed by ChatGPT.",
          "remediation_hint": "Remove GPTBot disallow rule or add targeted allow rules"
        }
      ]
    },
    "llms_txt": {
      "exists": false,
      "valid": false,
      "issues": [
        {
          "id": "policy-no-llms-txt",
          "category": "policy_files",
          "severity": "high",
          "summary": "No llms.txt file found",
          "detail": "No llms.txt file at /llms.txt. AI agents that support this standard have no structured entry point.",
          "remediation_hint": "Create llms.txt with site summary, key pages, and structured navigation"
        }
      ]
    }
  },
  "query_fanout": {
    "simulated_queries": [
      "What does Example Company do?",
      "Example Company pricing",
      "Example Company vs competitors",
      "Is Example Company good for enterprise?",
      "Example Company reviews"
    ],
    "coverage_score": 6,
    "gaps": [
      "No pricing page or structured pricing content found",
      "No comparison content addressing competitor queries"
    ]
  }
}
```

### Field Definitions

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Always `"1.0"` for this version |
| `generated_at` | ISO 8601 | yes | When the scan ran |
| `domain` | string | yes | Root domain scanned |
| `pages_scanned` | integer | yes | Total pages analyzed |
| `overall_score` | integer (0-100) | yes | Aggregate score per scoring rubric |
| `scores` | object | yes | Category breakdown — keys match `scores_max` |
| `scores_max` | object | yes | Maximum possible points per category |
| `pages[]` | array | yes | Per-page audit results |
| `pages[].url` | string | yes | Full URL |
| `pages[].page_type` | string | yes | Detected type: `homepage`, `product`, `pricing`, `blog`, `about`, `contact`, `docs`, `landing`, `comparison`, `case-study`, `careers`, `legal`, `other` |
| `pages[].score` | integer (0-100) | yes | Page-level score |
| `pages[].issues[]` | array | yes | Issues found on this page |
| `pages[].issues[].id` | string | yes | Unique issue identifier (kebab-case) |
| `pages[].issues[].category` | string | yes | Must match a key in `scores` |
| `pages[].issues[].severity` | enum | yes | `critical`, `high`, `medium`, `low` |
| `pages[].issues[].summary` | string | yes | One-line human-readable summary |
| `pages[].issues[].detail` | string | yes | Full explanation |
| `pages[].issues[].affected_element` | string/null | no | CSS selector or element reference if applicable |
| `pages[].issues[].remediation_hint` | string | yes | What to do about it |
| `pages[].schema_detected` | string\[\] | yes | Schema types found on page |
| `pages[].schema_missing` | string\[\] | yes | Schema types expected but absent for this page type |
| `pages[].meta` | object | yes | Page metadata extracted |
| `policy_files` | object | yes | robots.txt and llms.txt audit |
| `query_fanout` | object | yes | Simulated AI query coverage analysis |
| `query_fanout.simulated_queries` | string\[\] | yes | The sub-questions an LLM would generate |
| `query_fanout.coverage_score` | integer (0-10) | yes | How well the site answers these |
| `query_fanout.gaps` | string\[\] | yes | Queries the site cannot answer |

### Issue ID Convention

Issue IDs follow the pattern: `{category}-{specific-problem}`

Examples:

- `agentic-missing-product-schema` — Product schema not found
- `agentic-no-canonical` — Missing canonical tag
- `agentic-no-breadcrumb` — No BreadcrumbList for navigation
- `agentic-broken-heading-hierarchy` — Invalid heading structure
- `content-thin-faq` — No or insufficient FAQ content
- `policy-blocks-gptbot` — robots.txt blocks GPTBot
- `chunking-long-paragraphs` — Paragraphs exceed retrieval-friendly length

---

## 2. morphiq-rank → morphiq-build

### Contract: Prioritized Roadmap

morphiq-rank consumes the scan report and produces a **prioritized roadmap** — issues organized into progressive discovery tiers, ranked by impact and effort.

```json
{
  "schema_version": "1.0",
  "generated_at": "2025-03-25T14:35:00Z",
  "domain": "example.com",
  "source_scan_score": 62,
  "total_issues": 24,
  "tiers": [
    {
      "tier": 1,
      "name": "Foundation — Crawlability & Policy",
      "description": "Ensure AI crawlers can access and understand the site at all",
      "estimated_impact": "high",
      "actions": [
        {
          "priority": 1,
          "issue_id": "policy-blocks-gptbot",
          "category": "policy_files",
          "severity": "high",
          "impact_score": 95,
          "effort": "low",
          "summary": "robots.txt blocks GPTBot",
          "remediation": "Remove GPTBot disallow rule from robots.txt",
          "affected_urls": ["https://example.com/robots.txt"],
          "page_type": null,
          "depends_on": []
        },
        {
          "priority": 2,
          "issue_id": "policy-no-llms-txt",
          "category": "policy_files",
          "severity": "high",
          "impact_score": 90,
          "effort": "medium",
          "summary": "No llms.txt file found",
          "remediation": "Create llms.txt with site summary, key pages, and structured navigation aids",
          "affected_urls": [],
          "page_type": null,
          "depends_on": []
        }
      ]
    },
    {
      "tier": 2,
      "name": "Structure — Schema & Metadata",
      "description": "Add machine-readable structure so AI can extract facts",
      "estimated_impact": "high",
      "actions": [
        {
          "priority": 3,
          "issue_id": "agentic-missing-product-schema",
          "category": "agentic_readiness",
          "severity": "high",
          "impact_score": 85,
          "effort": "medium",
          "summary": "No Product schema on product page",
          "remediation": "Add JSON-LD Product schema with name, description, offers, aggregateRating",
          "affected_urls": ["https://example.com/product"],
          "page_type": "product",
          "depends_on": []
        }
      ]
    },
    {
      "tier": 3,
      "name": "Content — Depth & Coverage",
      "description": "Fill content gaps that prevent AI from citing the site",
      "estimated_impact": "medium",
      "actions": [
        {
          "priority": 4,
          "issue_id": "content-thin-faq",
          "category": "content_quality",
          "severity": "medium",
          "impact_score": 70,
          "effort": "medium",
          "summary": "No FAQ section on product page",
          "remediation": "Add 5-8 FAQs covering common purchase and comparison questions",
          "affected_urls": ["https://example.com/product"],
          "page_type": "product",
          "depends_on": ["agentic-missing-product-schema"]
        }
      ]
    },
    {
      "tier": 4,
      "name": "Optimization — Retrieval & Citation Quality",
      "description": "Fine-tune content for LLM chunking and citation patterns",
      "estimated_impact": "low",
      "actions": []
    }
  ]
}
```

### Field Definitions

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Always `"1.0"` |
| `generated_at` | ISO 8601 | yes | When the ranking ran |
| `domain` | string | yes | Carried from scan report |
| `source_scan_score` | integer | yes | The overall_score from the scan |
| `total_issues` | integer | yes | Count of all issues across all tiers |
| `tiers[]` | array | yes | Ordered list of progressive discovery tiers |
| `tiers[].tier` | integer | yes | Tier number (1 = highest priority) |
| `tiers[].name` | string | yes | Human-readable tier name |
| `tiers[].description` | string | yes | What this tier accomplishes |
| `tiers[].estimated_impact` | enum | yes | `high`, `medium`, `low` |
| `tiers[].actions[]` | array | yes | Ordered actions within the tier |
| `actions[].priority` | integer | yes | Global priority rank (1 = do first) |
| `actions[].issue_id` | string | yes | Matches `issues[].id` from scan report |
| `actions[].category` | string | yes | Issue category |
| `actions[].severity` | enum | yes | `critical`, `high`, `medium`, `low` |
| `actions[].impact_score` | integer (0-100) | yes | Weighted AI visibility impact |
| `actions[].effort` | enum | yes | `low`, `medium`, `high` |
| `actions[].summary` | string | yes | One-line issue description |
| `actions[].remediation` | string | yes | What to do |
| `actions[].affected_urls` | string\[\] | yes | URLs where this issue appears |
| `actions[].page_type` | string/null | no | Page type if page-specific |
| `actions[].depends_on` | string\[\] | yes | Issue IDs that should be resolved first |

### Tier Definitions

| Tier | Name | Focus |
| --- | --- | --- |
| 1 | Foundation — Crawlability & Policy | robots.txt, llms.txt, basic accessibility |
| 2 | Structure — Schema & Metadata | JSON-LD, meta tags, OG, canonicals |
| 3 | Content — Depth & Coverage | FAQ, content gaps, query coverage |
| 4 | Optimization — Retrieval & Citation Quality | Chunking, heading hierarchy, E-E-A-T |

---

## 3. morphiq-build → morphiq-track

### Contract: Build Output

morphiq-build consumes the prioritized roadmap and produces **build artifacts** — the actual content, schema, and policy files created or rewritten.

morphiq-build has two entry points that converge to the same output format:

- **From prompt**: User describes what to create → pipeline generates it
- **From existing content**: Existing content ingested → analyzed → enriched → rewritten as final optimized output

```json
{
  "schema_version": "1.0",
  "generated_at": "2025-03-25T15:00:00Z",
  "domain": "example.com",
  "source_roadmap_score": 62,
  "entry_point": "existing_content",
  "artifacts": [
    {
      "artifact_id": "build-001",
      "type": "content",
      "action_ref": {
        "issue_id": "content-thin-faq",
        "priority": 4,
        "tier": 3
      },
      "target_url": "https://example.com/product",
      "page_type": "product",
      "title": "Product FAQ Section",
      "content": {
        "format": "html",
        "body": "<section class=\"faq\"><h2>Frequently Asked Questions</h2>..."
      },
      "placement": {
        "instruction": "Add after the product features section and before the CTA",
        "selector": "section.product-features"
      }
    },
    {
      "artifact_id": "build-002",
      "type": "schema",
      "action_ref": {
        "issue_id": "agentic-missing-product-schema",
        "priority": 3,
        "tier": 2
      },
      "target_url": "https://example.com/product",
      "page_type": "product",
      "title": "Product JSON-LD Schema",
      "content": {
        "format": "json-ld",
        "body": "{\"@context\":\"https://schema.org\",\"@type\":\"Product\",...}"
      },
      "placement": {
        "instruction": "Add to <head> as <script type=\"application/ld+json\">",
        "selector": "head"
      }
    },
    {
      "artifact_id": "build-003",
      "type": "policy_file",
      "action_ref": {
        "issue_id": "policy-no-llms-txt",
        "priority": 2,
        "tier": 1
      },
      "target_url": "https://example.com/llms.txt",
      "page_type": null,
      "title": "llms.txt",
      "content": {
        "format": "text",
        "body": "# example.com\n\n> Example Company builds widgets for teams...\n\n## Key Pages\n..."
      },
      "placement": {
        "instruction": "Create file at site root: /llms.txt",
        "selector": null
      }
    },
    {
      "artifact_id": "build-004",
      "type": "metadata",
      "action_ref": {
        "issue_id": "agentic-weak-meta-description",
        "priority": 6,
        "tier": 2
      },
      "target_url": "https://example.com/product",
      "page_type": "product",
      "title": "Optimized Meta Description",
      "content": {
        "format": "meta",
        "body": {
          "description": "Example Widget helps teams collaborate 3x faster. Compare features, pricing, and integrations.",
          "og_description": "Example Widget helps teams collaborate 3x faster.",
          "title": "Example Widget — Team Collaboration Tool | Example Company"
        }
      },
      "placement": {
        "instruction": "Replace existing meta description and OG tags in <head>",
        "selector": "head"
      }
    }
  ],
  "summary": {
    "total_artifacts": 4,
    "by_type": {
      "content": 1,
      "schema": 1,
      "policy_file": 1,
      "metadata": 1
    },
    "issues_addressed": ["content-thin-faq", "agentic-missing-product-schema", "policy-no-llms-txt", "agentic-weak-meta-description"],
    "tiers_covered": [1, 2, 3]
  }
}
```

### Field Definitions

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Always `"1.0"` |
| `generated_at` | ISO 8601 | yes | When the build ran |
| `domain` | string | yes | Carried from roadmap |
| `source_roadmap_score` | integer | yes | The scan score from the roadmap |
| `entry_point` | enum | yes | `prompt` or `existing_content` |
| `artifacts[]` | array | yes | All generated artifacts |
| `artifacts[].artifact_id` | string | yes | Unique ID for this artifact (`build-NNN`) |
| `artifacts[].type` | enum | yes | `content`, `schema`, `policy_file`, `metadata`, `robots_txt_rule` |
| `artifacts[].action_ref` | object | yes | Links back to the roadmap action |
| `artifacts[].action_ref.issue_id` | string | yes | The issue this artifact addresses |
| `artifacts[].action_ref.priority` | integer | yes | Priority from roadmap |
| `artifacts[].action_ref.tier` | integer | yes | Tier from roadmap |
| `artifacts[].target_url` | string | yes | URL this artifact targets |
| `artifacts[].page_type` | string/null | no | Page type if applicable |
| `artifacts[].title` | string | yes | Human-readable artifact name |
| `artifacts[].content.format` | enum | yes | `html`, `json-ld`, `text`, `meta`, `markdown` |
| `artifacts[].content.body` | string/object | yes | The actual content (string for html/json-ld/text/markdown, object for meta) |
| `artifacts[].placement` | object | yes | Where and how to insert the artifact |
| `artifacts[].placement.instruction` | string | yes | Human/agent-readable placement instruction |
| `artifacts[].placement.selector` | string/null | no | CSS selector if applicable |
| `summary` | object | yes | Rollup of what was built |

---

## 4. morphiq-track → morphiq-rank (Loop)

### Contract: Delta Report

morphiq-track produces a **delta report** — a comparison between the current measurement run and the previous one, showing what changed in AI visibility.

This report loops back to morphiq-rank as supplementary input for re-prioritization.

```json
{
  "schema_version": "1.0",
  "generated_at": "2025-03-25T16:00:00Z",
  "domain": "example.com",
  "run_id": "track-2025-03-25",
  "previous_run_id": "track-2025-03-18",
  "is_baseline": false,
  "providers_queried": ["openai", "gemini", "perplexity", "anthropic"],
  "prompt_count": 25,
  "share_of_voice": {
    "current": 34.2,
    "previous": 28.6,
    "delta": 5.6,
    "breakdown": {
      "openai": { "current": 40.0, "previous": 32.0, "delta": 8.0 },
      "gemini": { "current": 30.0, "previous": 26.0, "delta": 4.0 },
      "perplexity": { "current": 38.0, "previous": 30.0, "delta": 8.0 },
      "anthropic": { "current": 28.8, "previous": 26.4, "delta": 2.4 }
    }
  },
  "citations": {
    "gained": [
      {
        "url": "https://example.com/product",
        "provider": "openai",
        "prompt": "best widgets for teams",
        "prompt_type": "category",
        "first_seen": "2025-03-25"
      }
    ],
    "lost": [],
    "stable": [
      {
        "url": "https://example.com/",
        "provider": "perplexity",
        "prompt": "what is Example Company",
        "prompt_type": "brand"
      }
    ]
  },
  "mentions": {
    "current_total": 41,
    "previous_total": 34,
    "delta": 7,
    "by_prompt_type": {
      "brand": { "current": 12, "previous": 10, "delta": 2 },
      "category": { "current": 8, "previous": 5, "delta": 3 },
      "comparison": { "current": 6, "previous": 6, "delta": 0 },
      "feature": { "current": 9, "previous": 8, "delta": 1 },
      "use_case": { "current": 6, "previous": 5, "delta": 1 }
    }
  },
  "competitor_mentions": [
    {
      "company": "Competitor A",
      "current_mentions": 52,
      "previous_mentions": 50,
      "delta": 2,
      "share_of_voice": 43.3
    }
  ],
  "flagged_actions": [
    {
      "type": "citation_opportunity",
      "summary": "Product page now cited by OpenAI for category queries — consider expanding comparison content to capture comparison queries too",
      "related_prompt_type": "comparison",
      "suggested_issue_id": "content-no-comparison"
    }
  ],
  "raw_results": {
    "storage": "morphiq-track/results/track-2025-03-25.json",
    "format": "Per-provider raw responses stored separately for audit"
  }
}
```

### Field Definitions

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Always `"1.0"` |
| `generated_at` | ISO 8601 | yes | When the tracking run completed |
| `domain` | string | yes | Domain being tracked |
| `run_id` | string | yes | Unique run identifier |
| `previous_run_id` | string/null | yes | Previous run for delta comparison (null if baseline) |
| `is_baseline` | boolean | yes | True if this is the first run (no delta) |
| `providers_queried` | string\[\] | yes | Which AI providers were queried |
| `prompt_count` | integer | yes | Total prompts fired |
| `share_of_voice` | object | yes | SoV calculation: (company mentions / total mentions) x 100 |
| `share_of_voice.current` | float | yes | Current run SoV percentage |
| `share_of_voice.previous` | float/null | yes | Previous run SoV (null if baseline) |
| `share_of_voice.delta` | float/null | yes | Change in SoV |
| `share_of_voice.breakdown` | object | yes | Per-provider SoV |
| `citations` | object | yes | URL-level citation tracking |
| `citations.gained[]` | array | yes | New citations since last run |
| `citations.lost[]` | array | yes | Citations that disappeared |
| `citations.stable[]` | array | yes | Citations maintained |
| `mentions` | object | yes | Mention count tracking |
| `mentions.by_prompt_type` | object | yes | Breakdown by prompt category |
| `competitor_mentions[]` | array | no | Competitor tracking if configured |
| `flagged_actions[]` | array | yes | Suggested next actions based on deltas |
| `flagged_actions[].type` | enum | yes | `citation_opportunity`, `citation_loss`, `sov_drop`, `competitor_gain` |
| `flagged_actions[].suggested_issue_id` | string | no | Issue ID format for feeding back to morphiq-rank |
| `raw_results` | object | yes | Pointer to raw provider response data |

### Baseline Run Behavior

On the first run (`is_baseline: true`):

- `previous_run_id` is `null`
- All `delta` fields are `null`
- `citations.gained` contains all found citations
- `citations.lost` and `citations.stable` are empty
- The report establishes the measurement baseline

### Loop Back to morphiq-rank

When morphiq-track output is fed back to morphiq-rank:

1. `flagged_actions` with `suggested_issue_id` are treated as new issues
2. Citation losses trigger severity escalation of related existing issues
3. SoV drops trigger re-prioritization of the affected prompt type categories
4. The rank skill merges these with any existing scan report issues

---

## Data Flow Summary

```
┌─────────────┐     Scan Report       ┌──────────────┐
│ morphiq-scan│  ──────────────────→  │ morphiq-rank │
└─────────────┘     (JSON, ~50KB)     └──────┬───────┘
                                             │
                                    Prioritized Roadmap
                                      (JSON, ~20KB)
                                             │
                                             ▼
                            ┌───────────────────────────────────┐
                            │          morphiq-build            │
                            │                                   │
                            │  Entry A: prompt → generate       │
                            │  Entry B: content → pipeline →    │
                            │           rewrite final output    │
                            └──────────────┬────────────────────┘
                                           │
                                     Build Output
                                    (JSON, ~100KB)
                                           │
                                           ▼
                            ┌───────────────────────────┐
                            │      morphiq-track        │
                            │                           │
                            │  Queries: OpenAI, Gemini, │
                            │  Perplexity, Anthropic    │
                            └──────────────┬────────────┘
                                           │
                                      Delta Report
                                     (JSON, ~30KB)
                                           │
                                           ▼
                                  Back to morphiq-rank
                                  (supplementary input)
```

## Versioning

All contracts use `schema_version: "1.0"`. When breaking changes are introduced:

1. Bump `schema_version`
2. Skills must check `schema_version` and fail with a clear message if incompatible
3. CHANGELOG.md tracks contract changes