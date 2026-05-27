---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
inclusion: manual
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## The Four Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully** — Don't skip past errors or warnings. Read stack traces completely. Note line numbers, file paths, error codes.

2. **Reproduce Consistently** — Can you trigger it reliably? What are the exact steps? If not reproducible → gather more data, don't guess.

3. **Check Recent Changes** — What changed that could cause this? Git diff, recent commits, new dependencies, config changes.

4. **Gather Evidence in Multi-Component Systems** — For each component boundary: log what data enters, log what exits, verify environment/config propagation. Run once to gather evidence showing WHERE it breaks, THEN analyze.

5. **Trace Data Flow** — Where does the bad value originate? What called this with the bad value? Keep tracing up until you find the source. Fix at source, not symptom.

### Phase 2: Pattern Analysis

1. **Find Working Examples** — Locate similar working code in same codebase.
2. **Compare Against References** — Read reference implementations COMPLETELY. Don't skim.
3. **Identify Differences** — List every difference, however small. Don't assume "that can't matter."
4. **Understand Dependencies** — What settings, config, environment does this need?

### Phase 3: Hypothesis and Testing

1. **Form Single Hypothesis** — State clearly: "I think X is the root cause because Y." Be specific.
2. **Test Minimally** — Make the SMALLEST possible change to test hypothesis. One variable at a time.
3. **Verify Before Continuing** — Did it work? Yes → Phase 4. Didn't work? Form NEW hypothesis. DON'T add more fixes on top.
4. **When You Don't Know** — Say "I don't understand X." Don't pretend to know.

### Phase 4: Implementation

1. **Create Failing Test Case** — Simplest possible reproduction. MUST have before fixing.
2. **Implement Single Fix** — Address the root cause identified. ONE change at a time. No "while I'm here" improvements.
3. **Verify Fix** — Test passes now? No other tests broken? Issue actually resolved?
4. **If Fix Doesn't Work** — STOP. Count fixes tried. If < 3: Return to Phase 1. **If ≥ 3: STOP and question the architecture.**

### If 3+ Fixes Failed: Question Architecture

**Pattern indicating architectural problem:**
- Each fix reveals new shared state/coupling/problem in different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

**STOP and question fundamentals** — discuss with your human partner before attempting more fixes.

## Red Flags — STOP and Follow Process

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)

**ALL of these mean: STOP. Return to Phase 1.**

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "One more fix attempt" (after 2+) | 3+ failures = architectural problem. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare | Identify differences |
| **3. Hypothesis** | Form theory, test minimally | Confirmed or new hypothesis |
| **4. Implementation** | Create test, fix, verify | Bug resolved, tests pass |
