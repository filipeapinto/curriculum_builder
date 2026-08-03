# Commercial content-platform schema governance

## Why this thread

The prior two threads draw on Kafka/microservice contract testing and a
general engineering blog pattern. This thread checks what a production
content platform — one whose entire product is authoring and versioning
structured content against an evolving schema, the closest commercial analogue
to `curricula/arduino_kit`'s domain files — actually does in its own
documentation, per this methodology's requirement to ground at least one
thread in commercial/production practice rather than academic work alone.

## Findings

**A commercial headless CMS treats "the schema changed" and "the content is
migrated" as two separate, explicitly-gated steps, and refuses to silently
paper over the gap.** Sanity's content-migration documentation states that
changing the schema does not automatically change or delete existing content,
"to prevent unintended breakage," and instructs authors to run
`sanity documents validate` to check the validation status of documents
*before* migrating, to write scripted migrations that default to a dry run,
and to back up the dataset first (Sanity, *Migrating your schema and
content*, sanity.io/docs/content-lake/schema-and-content-migrations).
Implication for this pipeline: the commercial answer to "the schema changed
out from under the content" is not a smarter generator — it's a mandatory
`validate`-before-`migrate` step that surfaces exactly which existing content
now fails the current schema, which is precisely what running
`verify_domain.py` against `l01`-`l04` by hand in this scan's grounding step
did manually, and precisely what nothing in this pipeline does automatically.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Sanity, *Migrating your schema and content*, Sanity Docs — https://www.sanity.io/docs/content-lake/schema-and-content-migrations

## Discarded

- https://www.datocms.com/features/schema-builder — DatoCMS product marketing page for its visual schema builder; describes the editing UI, not migration/validation governance, so not on point for this claim; not cited.
- https://www.enterprisecms.org/guides/versioning-strategies-for-enterprise-content-models, https://www.enterprisecms.org/guides/top-5-stages-of-an-enterprise-cms-migration-and-what-goes-wrong — generic guide-site content with no named vendor or checkable specifics behind the claims; below the source-quality bar, not fetched.
- https://www.linearloop.io/blog/why-enterprise-cms-migrations-fail-before-they-begin, https://naturaily.com/blog/smooth-cms-migration-checklist-is-going-headless-the-right-move, https://www.bignewsnetwork.com/news/279176722/the-headless-cms-migration-checklist-every-us-digital-publisher-needs-before-q3-2025 — agency/SEO content marketing, not primary vendor documentation; not fetched.
