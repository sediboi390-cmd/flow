---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
inclusion: manual
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for the codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Save plans to:** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`

## Scope Check

If the spec covers multiple independent subsystems, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for:

- Design units with clear boundaries and well-defined interfaces
- Each file should have one clear responsibility
- Files that change together should live together
- In existing codebases, follow established patterns

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" — step
- "Run it to make sure it fails" — step
- "Implement the minimal code to make the test pass" — step
- "Run the tests and make sure they pass" — step
- "Commit" — step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

Each task follows this format:

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**
  [Complete test code here]

- [ ] **Step 2: Run test to verify it fails**
  Run: `<exact command>`
  Expected: FAIL with "[expected message]"

- [ ] **Step 3: Write minimal implementation**
  [Complete implementation code here]

- [ ] **Step 4: Run test to verify it passes**
  Run: `<exact command>`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add <files>
  git commit -m "feat: <description>"
  ```
````

## No Placeholders

Every step must contain the actual content an engineer needs. These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code)
- Steps that describe what to do without showing how

## Remember
- Exact file paths always
- Complete code in every step
- Exact commands with expected output
- DRY, YAGNI, TDD, frequent commits

## Self-Review

After writing the complete plan, check it against the spec:

1. **Spec coverage:** Can you point to a task for each requirement? List any gaps.
2. **Placeholder scan:** Search for red flags from the "No Placeholders" section.
3. **Type consistency:** Do method signatures in later tasks match what you defined in earlier tasks?

Fix issues inline. If you find a spec requirement with no task, add the task.

## Execution Handoff

After saving the plan, offer execution choice:

> "Plan complete and saved to `docs/superpowers/plans/<filename>.md`. Two execution options:
>
> **1. Subagent-Driven (recommended)** — Fresh subagent per task, review between tasks, fast iteration
>
> **2. Inline Execution** — Execute tasks in this session, batch execution with checkpoints
>
> Which approach?"

- **If Subagent-Driven chosen:** Use the subagent-driven-development skill
- **If Inline Execution chosen:** Use the executing-plans skill
