# ADR 0011: Silent Fallback on Profile Not Found

## Status

Accepted

## Date

2025-12-05

## Context

When a user specifies a nonexistent profile name, the application must decide whether to fail with an error or continue execution.

ADR-0009 established a pattern of silent fallback to PassThroughFilter when LLM models are unavailable.

## Decision

When the requested profile does not exist, silently fall back to PassThroughFilter without warnings or errors.

## Rationale

- **Consistency**: Follows ADR-0009's silent fallback pattern for unavailable resources
- **Graceful degradation**: User can continue work even with profile misconfiguration
- **Zero-configuration default**: Application works without profile setup

## Implications

### Positive Implications

- Application never fails due to profile configuration issues
- Consistent behavior across all unavailability scenarios (LLM, profiles)

### Concerns

- Silent errors hide configuration mistakes (mitigation: future `stym doctor` command will validate profile configuration)
- Unexpected behavior when user expects specific profile (mitigation: future `--verbose` flag will show fallback notifications)

## Alternatives

### Fail with Error

Exit with error message when profile not found.

**Pros**: User immediately aware of configuration issues

**Cons**: Breaks zero-configuration experience; requires manual intervention

**Reason for rejection**: Inconsistent with ADR-0009 graceful degradation philosophy

### Warn but Continue

Print warning to stderr, then fall back to PassThroughFilter.

**Pros**: User notified of fallback; still allows execution

**Cons**: Warning noise in logs; complicates testing

**Reason for rejection**: Consistent with ADR-0009 reasoning - defer notification mechanism to future enhancement

## Future Direction

Following ADR-0009 future direction:

- Add structured logging when profile not found
- Implement `--verbose` flag to show profile fallback notifications
- Implement `stym doctor` command to validate profile configuration

## References

- [Issue #10: Introduce default profile concept](https://github.com/osoekawaitlab/shtym-py/issues/10)
- [ADR-0009: Silent Fallback to PassThrough Filter on Model Unavailability](./0009-silent-fallback-to-passthrough-filter.md)
- [ADR-0010: Introduce Profile as Core Domain Object](./0010-introduce-profile-as-core-domain-object.md)
