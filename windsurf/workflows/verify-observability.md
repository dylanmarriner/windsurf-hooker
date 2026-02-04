# /verify-observability
Validate observability compliance for a changed flow.

## Prerequisites
- observability/ pack present

## Inputs
- Service name
- Changed endpoints/jobs

## Steps
1) Confirm structured logs in changed paths
   - Ensure required fields per logging_schema.md exist

2) Confirm correlation propagation
   - Entry generates request_id if missing
   - Downstream logs include same request_id

3) Confirm redaction
   - No denylisted keys appear in emitted logs or traces
   - Tests exist that enforce redaction behavior

4) Confirm metrics
   - RED/USE metrics exist where appropriate
   - Labels are low-cardinality and documented

## Success Criteria
- Logs match schema expectations
- Correlation and redaction are verified
- Metrics are stable and safe
