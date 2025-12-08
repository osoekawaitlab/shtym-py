# ADR 0013: Rename Filter to Processor

## Status

Accepted

## Date

2025-12-06

## Context

The term "Filter" was introduced in ADR-0007 to represent output transformation logic. While the name was reasonable at the time, it has become apparent that "Filter" carries a strong connotation of **removal or reduction** (like coffee filters, air filters, or UNIX grep).

However, shtym's transformation capabilities include:
- **Reducing**: Long output → summary (fits "filter" metaphor)
- **Expanding**: Error messages → detailed explanations (does not fit "filter" metaphor)
- **Converting**: JSON → human-readable format (does not fit "filter" metaphor)
- **Translating**: English → Japanese (does not fit "filter" metaphor)

The term "Filter" emphasizes only the reduction aspect, which misrepresents the abstraction's full purpose.

## Decision

Rename "Filter" to "Processor" throughout the codebase.

- `Filter` Protocol → `Processor` Protocol
- `PassThroughFilter` → `PassThroughProcessor`
- `LLMFilter` → `LLMProcessor`

## Rationale

**"Processor" is more accurate:**
- Neutral term that covers transformation, conversion, expansion, and reduction
- Commonly used in software (data processors, text processors, image processors)
- Does not imply a specific type of operation

**Precedent in similar tools:**
- Text processors (word processors transform text)
- Data processors (ETL tools transform data)
- Stream processors (transform streaming data)

**Better alignment with user mental model:**
- Users configure "how to process output", not "how to filter output"
- Processing includes both simplification and enrichment

## Implications

### Positive Implications

- More accurate terminology that reflects actual capabilities
- Easier to explain future features (translation, format conversion)
- Aligns with common software engineering vocabulary

### Concerns

- Breaking change for any external documentation or tutorials (mitigation: no public API yet, only internal usage)
- Existing ADRs use "Filter" terminology (mitigation: amendment sections will clarify the rename)

## Alternatives

### Keep "Filter" and expand its definition

**Pros**: No renaming needed, term already established in ADRs

**Cons**: Fighting against common understanding of "filter"; confusing to new contributors

**Reason for rejection**: Misleading terminology is worse than a one-time rename

### Use "Transformer"

**Pros**: Clear transformation intent

**Cons**: Overloaded term (ML transformers, electrical transformers, design pattern)

**Reason for rejection**: "Processor" is less ambiguous

## References

- [ADR-0007: Introduce Filter Abstraction for Output Processing](./0007-introduce-filter-abstraction-for-output-processing.md) (uses "Filter" terminology)
- [ADR-0009: Silent Fallback to PassThrough Filter](./0009-silent-fallback-to-passthrough-filter.md) (uses "Filter" terminology)
