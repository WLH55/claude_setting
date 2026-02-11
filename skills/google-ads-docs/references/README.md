# Google Ads API Documentation Index

## Document Catalog

### Core Concepts

| Document | Topics | Search Keywords |
|----------|--------|-----------------|
| `00-overview.md` | API overview, navigation, document mapping | overview, getting started, introduction |
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

### Python Client Library

| Document | Topics | Search Keywords |
|----------|--------|-----------------|
| `python-client/01-configuration.md` | YAML, env vars, dict config | config, yaml, environment, dict, load_from_storage |
| `python-client/02-authentication.md` | OAuth2, service account, gcloud CLI | auth, oauth, service account, adc, refresh token |
| `python-client/03-code-completion.md` | IDE autocomplete, direct imports | ide, autocomplete, code completion, pycharm, vscode |
| `python-client/04-proto-getters.md` | get_service, get_type, enums | getter, service, type, enum, version |
| `python-client/05-field-masks.md` | Update operations, field_mask | field mask, update, protobuf_helpers |
| `python-client/06-logging.md` | Log levels, configuration | log, logging, debug, info, warning |
| `python-client/07-resource-names.md` | Resource name paths | resource name, path, parse, campaign_path |
| `python-client/08-empty-message-fields.md` | Empty bidding strategies | empty message, manual_cpm, bidding strategy |
| `python-client/09-protobuf-messages.md` | proto-plus vs protobuf | proto-plus, protobuf, convert, marshaling |
| `python-client/10-timeouts.md` | Streaming and unary call timeouts | timeout, deadline, retry, search_stream |
| `python-client/11-dependencies.md` | Python version compatibility | dependencies, packages, protobuf, grpcio |
| `python-client/12-streaming-iterators.md` | Scope management | streaming, iterator, scope, channel |
| `python-client/13-proxy.md` | HTTP proxy configuration | proxy, http_proxy |
| `python-client/14-optional-request-headers.md` | validate_only, optional fields | validate_only, request header, optional |

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

## Quick Reference

### Quotas
| Access Level | Production | Test |
|--------------|------------|------|
| Explorer | 2,880/day | 15,000/day |
| Basic | 15,000/day | 15,000/day |

### Limits
| Item | Limit |
|------|-------|
| Mutate operations per request | 10,000 |
| Campaign name length | 256 chars |
| Shared budgets per account | 11,000 |

### Common Error Codes
| Code | Meaning |
|------|---------|
| `RESOURCE_EXHAUSTED` | Quota exceeded |
| `INTERNAL_ERROR` | Server error (retryable) |
| `UNAVAILABLE` | Service unavailable (retryable) |
| `INVALID_ARGUMENT` | Invalid input |
| `PERMISSION_DENIED` | No permission |
