# Variance Report — `llm_driven_learning`

Phase 3 of `plans/sota_agents_pipeline/sota_agents_pipeline.plan.v2.md`.
Three eval-runner agents each ran the skill against one eval prompt from
`evals/evals.json`, in a separate workspace, and graded the result. This
report is written from the three result JSONs only.

Sources: `results/eval_1_result.json`, `results/eval_2_result.json`,
`results/eval_3_result.json`. All three carry an `overall_pass` field; none
is unresolved.

---

## 1. Pass/fail summary

| Eval | Scenario | Expectations | Failed | `validate_outputs.py` | Overall |
|------|----------|--------------|--------|----------------------|---------|
| 1 | Cold scan of a rough pipeline run — "what should have reviewed this?" | 9 | 0 | exit 0 | **PASS** |
| 2 | Narrow scan of one known defect — raw JSON shipped as lesson body | 6 | 0 | exit 0 | **PASS** |
| 3 | Refresh a stale prior scan, report sources that no longer hold up | 6 | 0 | exit 0 | **PASS** |

**21 of 21 expectations passed. No expectation failed in any eval.**

Every eval independently confirmed the two contract-level gates: the
validator exited zero on the output directory, and the grading agent
re-checked citation-to-verification traceability *without* relying on the
validator. Evals 1 and 2 both went further than the validator does and
checked ISO-8601 timestamp ordering — that every cited URL's keep-decision
`web_fetch_verify` predates the `write_file` of the artifact citing it —
with zero violations in either run.

---

## 2. Variance across runs

### Methodology held steady

The three runs differ in topic, in prompt shape, and in nearly every source
they chose. The methodology did not vary:

- **Ground before you search — 3/3, and by a wide margin.** Every run's
  fixture reads occupy the earliest log indices and the first `web_search`
  comes much later (eval 1: reads 0–3, first search 14; eval 2: reads 0–6
  and 10–11, first search 13, a 52-second gap by wall clock; eval 3: reads
  0–5, first search 21). No run leaked a search before the fixture was read.
- **QA report read last — 3/3.** All three read the four lesson documents
  *before* the fixture's own QA report, which is the stricter ordering
  SKILL.md Step 1 asks for. This is the rule that pays: all three runs
  produced defects the QA report does not contain, so no run was merely
  reflecting the fixture's framing back.
- **Fetch before you cite — 3/3, with live catches in every run.** Eval 1
  logged 9 correction/discard/failure entries and caught two snippets
  asserting claims their papers do not make. Eval 2 discarded 3 of 12
  fetches, two because the fetched page contradicted the snippet. Eval 3
  re-verified all 16 prior-scan URLs against *the specific claim each was
  cited for*, not liveness, and demoted four.
- **Retry ladder — used and effective wherever fetches failed.** Eval 1
  recovered two undecodable PDFs via alternate arXiv/ERIC forms; eval 2
  recovered `arXiv:2606.05405` via `abs → html` and that recovery supplied
  the scan's most load-bearing quote; eval 3 recovered waxell.ai via the
  publisher's dev.to cross-post.
- **Honest thinness over padding — 3/3.** Eval 1's rendering thread
  declared its own thinness in-file (2 sources vs 4 elsewhere) rather than
  padding. Eval 2 stated outright that no published source studies its
  exact defect. Eval 3 reported a prior citation's own attribution error
  rather than quietly fixing it.
- **Output contract shape — 3/3 conformant.** Thread counts 7 / 6 / 8 all
  sit inside the stated 5–8 band; exactly one `sota_agents.v<N>.json` and
  one `action_log.jsonl` per directory; all threads carry the four required
  sections in contract order.

### Convergent evidence that grounding is real, not performed

Evals 1 and 3 ran independently, in different workspaces, against different
prompts, and **both found the same defect the fixture's QA report misses**:
`L03` and `L04` each set `next_lab_link` to a nonexistent `L05`. Eval 3 got
far enough to promote it to a standalone thread and a sixth recommended
agent. Two independent runs converging on an unstated defect is the
strongest single signal in this eval set that Step 1 is doing work rather
than producing plausible-looking prose.

### Where runs legitimately differ

Differing papers and URLs per run are expected and are **not** a finding.
The following differences are real but benign:

- **Recommendation counts: 6 / 4 / 6.** Eval 2's lower count is the
  "keep the recommendation count honest" guidance working — its threads 5
  and 6 did not justify standalone agents, and it said so. Counts track
  prompt scope, not run-to-run noise.
- **Thread-to-agent ratio varies** (eval 1 folded a commercial thread into
  two other agents; eval 3's extra agent is entirely the new
  sequence-coherence thread). Both are defensible editorial calls.

### One genuine methodology divergence

**The keep/discard threshold is not consistent between runs.** Evals 1 and
2 both fetched `blog.duolingo.com/how-duolingo-experts-work-with-ai`, both
correctly detected that the page does not support the review-gate workflow
its snippet implies — and then disposed of it differently. Eval 1 logged it
`CORRECTED` and cited it anyway as a primary vendor source with the
unsupported claim stripped. Eval 2 logged it `DISCARD` and confined it to
Discarded sections. Both are defensible; the skill does not say which is
correct. The detection rule is stable; the disposition rule is not.

A related divergence in verification *depth*: eval 1 verified every arXiv
source at abstract level and flagged in its own notes that several arguably
merited `PARTIALLY VERIFIED`; eval 3 fetched `/html/` full text when it
found the abstract page did not carry the claim it needed (`2604.04728`).
Same skill, two different depth policies, both passing.

---

## 3. Recurring failure modes

**None.** No expectation failed in any eval, so no expectation failed in
more than one — there is no skill-instruction gap of the kind this section
exists to catch.

What *does* recur is a set of tooling and guidance gaps the graders
surfaced in their notes. These did not cause a failure in these three runs,
but each is a way a future run could pass while being weaker than it looks:

1. **`validate_outputs.py` accepts `pending` as kept — 2 runs affected.**
   Confirmed against source: `scripts/validate_outputs.py:77` reads
   `if decision.startswith("keep") or decision.startswith("pending")`.
   A scan can log `pending` for a never-verified URL, cite it, and pass.
   Eval 2 hit this honestly with a mid-retry-ladder `pending` entry and
   closed it by appending an explicit `DISCARD`; the validator would not
   have caught it otherwise. **This is the one finding here that weakens
   the guarantee the skill advertises**, because the validator is what the
   contract leans on.
2. **Abstract-vs-full-text verification depth is unspecified — 2 runs
   diverged.** `references/source_verification.md` says an abstract
   suffices for most topical claims; eval 1 read that as license for
   abstract-only across the board, eval 3 escalated to full text when the
   abstract fell short. Two graders could reach different verdicts on the
   same log.
3. **`log_action.py` corrupts the log under zsh globbing — 1 run.** Eval 1
   carries 3 duplicated entries: a `&&`-joined chain of `log_action.py`
   calls aborted mid-chain when a URL containing `?`
   (`eric.ed.gov/?id=EJ1118467`) hit zsh `no matches found`, and the chain
   was re-run whole. The runner correctly refused to hand-edit the log, so
   the log is over-inclusive rather than falsified — but it is not a
   faithful action record.
4. **No guidance for tool failure vs empty result set — 1 run.** Eval 2 hit
   `Web search error: unavailable`; Step 3 tells you to log a failed search
   and refine the query, which is wrong advice for a tool outage.
5. **Version-numbering rule read two ways — 1 run.**
   `references/output_contracts.md` says pick the next unused `N` *in the
   directory*; eval 3 wrote `sota_agents.v2.json` into a fresh directory to
   keep numbering monotonic across the scan lineage, and logged the
   rationale. The validator accepts any `v<N>`, so this passed.

---

## 4. Verdict

**Fit to use as-is, with one named fix to schedule.**

Three independent runs, three different task shapes, 21/21 expectations,
zero methodology drift on the rules the skill actually advertises. Both
advertised rules earned their keep in every run: grounding produced defects
the fixture's QA report missed (and two runs converged on the same one
independently), and fetch-before-cite caught snippet-level
misrepresentations in all three — including, in eval 1, precisely the trap
SKILL.md warns about. The skill can be used on real work now.

The fix to schedule, in priority order:

1. **Close the `pending` loophole** (`scripts/validate_outputs.py:77`).
   Drop `pending` from `kept_urls()` so only decisions beginning `keep`
   count, and let a lingering `pending` fail the run. Every unresolved
   retry ladder must terminate in an explicit `keep` or `DISCARD`. This is
   the only item that affects the guarantee the contract makes, and eval 2
   demonstrated it is reachable in normal use.

Worth doing alongside it, none blocking:

2. **State the verification-depth rule** in
   `references/source_verification.md`: when an abstract suffices, when
   full text is required (proposed line: if the claim you are citing is not
   *in* the abstract, fetch the full text or downgrade to
   `PARTIALLY VERIFIED`). Removes the eval-1/eval-3 divergence.
3. **State the disposition rule** for a source whose page contradicts its
   snippet but is still useful for a narrower claim — cite-with-correction
   or discard. This is the only place the three runs' *methodology*
   genuinely diverged (the Duolingo page).
4. **Require quoting in `log_action.py` usage** — its own docstring example
   passes bare URLs, which is what broke eval 1's log. Quote the values in
   the docstring and note that `?` in a URL will glob under zsh.
5. **Add a tool-failure branch to Step 3**, distinct from "search returned
   nothing useful."
6. **Clarify version numbering** in `references/output_contracts.md` —
   per-directory or per-lineage.

None of items 2–6 would have changed any verdict in this eval set.
