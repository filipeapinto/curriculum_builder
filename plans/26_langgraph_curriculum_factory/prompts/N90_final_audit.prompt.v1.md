# GOAL

Execute `N90_FINAL_AUDIT` after N50 and N60. Independently audit the frozen Plan
26 spec, implementation graph, QA criteria, all node results/hashes, production
call graph, dependency environment, tests, and live proof status.

Do not edit production code in this node. Classify every finding under exactly
one `rework_edges` key and owning node. Rework invalidates that node and all
descendants, after which the runner resumes graph scheduling and later returns
to a fresh N90 audit.

# TEST

1. Every normative spec requirement maps to passing implementation evidence.
2. All graph nodes/results and declared artifacts/hashes are current and valid.
3. Exactly one compiled LangGraph production path exists; no LangChain wrapper or fallback.
4. Eight-job, authority, denominator, repair, persistence, resume, terminal, and CLI invariants pass.
5. Full adversarial/regression evidence is complete with no waived test.
6. `ACTIVATED` is allowed only when N60 has valid authorized live unit and full-release proof.
7. `IMPLEMENTED_NOT_ACTIVATED` is allowed only when N50 passed and N60 is
   `NOT_AVAILABLE` solely for recorded external prerequisites.

Write `results/N90_FINAL_AUDIT.result.v1.md` with finding-to-owner dispositions,
all hashes, and exactly one verdict: `ACTIVATED`,
`IMPLEMENTED_NOT_ACTIVATED`, or `BLOCKED`.

# LOOP

If a blocking finding exists, emit its single rework key and owning node; do not
repair it here. The runner may traverse the same finding/root-cause rework edge
twice. A third occurrence, ambiguous ownership, missing evidence, or impossible
legal frontier produces `BLOCKED`. Never upgrade a verdict beyond its evidence.

