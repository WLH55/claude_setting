# Google Ads API Documentation Index

## Document Catalog

### Core Concepts

| Document | Topics | Search Keywords |
|----------|--------|-----------------|
| `00-overview.md` | API overview, navigation, document mapping | overview, getting started, introduction, docs |
| `01-api-structure.md` | Resources, services, object hierarchy | resource, service, hierarchy, customer, campaign, adgroup |
| `02-call-structure.md` | Request headers, authentication, calling methods | auth, authentication, header, oauth, token, developer-token, login-customer-id |
| `03-changing-objects.md` | Mutate operations, batch operations, create/update/remove | mutate, create, update, delete, remove, batch, operation |
| `04-retrieving-objects.md` | GAQL, Search/SearchStream, segments | query, gaql, search, searchstream, retrieve, fetch, segment |

### Best Practices

| Document | Topics | Search Keywords |
|----------|--------|-----------------|
| `06-best-practices-overview.md` | Optimization, error handling, batching | best practice, optimization, batch, token reuse |
| `07-quotas-limits.md` | API operation quotas, rate limits | quota, limit, rate, operations per day, resource exhausted |
| `08-system-limits.md` | Account limits, resource limits | system limit, account limit, max accounts, max campaigns |
| `09-troubleshooting.md` | Troubleshooting flow, debugging | troubleshoot, debug, error, issue, problem |
| `10-error-types.md` | Error classification (auth, retryable, validation, sync) | error type, authentication error, retryable, validation, sync |
| `11-understand-api-errors.md` | gRPC status codes, error model | grpc, status code, error model, internal, unavailable |

## Common Question Mappings

### Authentication & Access
- **How to authenticate?** → `02-call-structure.md`
- **What is developer token?** → `02-call-structure.md`
- **What is login-customer-id?** → `02-call-structure.md`

### Operations
- **How to create a campaign?** → `03-changing-objects.md`
- **How to query data?** → `04-retrieving-objects.md`
- **What is GAQL?** → `04-retrieving-objects.md`
- **Search vs SearchStream?** → `04-retrieving-objects.md`

### Quotas & Limits
- **What is the daily quota?** → `07-quotas-limits.md`
- **How many operations per request?** → `07-quotas-limits.md`
- **Max campaigns per account?** → `08-system-limits.md`

### Errors
- **RESOURCE_EXHAUSTED error?** → `07-quotas-limits.md`, `10-error-types.md`
- **How to handle errors?** → `09-troubleshooting.md`, `10-error-types.md`
- **What is INTERNAL_ERROR?** → `10-error-types.md`, `11-understand-api-errors.md`
- **Retry strategy?** → `06-best-practices-overview.md`, `10-error-types.md`

### Best Practices
- **How to optimize API calls?** → `06-best-practices-overview.md`
- **Batch operations?** → `06-best-practices-overview.md`, `03-changing-objects.md`
- **Error handling patterns?** → `06-best-practices-overview.md`, `11-understand-api-errors.md`

## Grep Patterns

For complex searches, use these patterns:

```
# Authentication
"oauth|token|developer-token|login-customer-id"

# Operations
"mutate|create|update|remove|batch"

# Queries
"gaql|search|searchstream|query|segment"

# Quotas
"quota|limit|operations per day|resource exhausted"

# Errors
"error|exception|retry|validation|internal"
```

## File Paths

```
D:\workspace\coding\google_ads\docs\google-ads-api\
├── 00-overview.md
├── 01-api-structure.md
├── 02-call-structure.md
├── 03-changing-objects.md
├── 04-retrieving-objects.md
├── 06-best-practices-overview.md
├── 07-quotas-limits.md
├── 08-system-limits.md
├── 09-troubleshooting.md
├── 10-error-types.md
├── 11-understand-api-errors.md
└── README.md (index and reading order)
```
