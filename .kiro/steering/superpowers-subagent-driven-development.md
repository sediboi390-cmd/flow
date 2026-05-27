---
name: subagent-driven-development
description: Use when executing implementation plans with independent tasks in the current session
inclusion: manual
---

# Subagent-Driven Development

Execute plan by dispatching fresh subagent per task, with two-stage review after each: spec compliance review first, then code quality review.

**Why subagents:** You delegate tasks to specialized agents with isolated context. By precisely crafting their instructions and context, you ensure they stay focused. They should never inherit your session's context — you construct exactly what they need.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration

**Continuous execution:** Do not pause to check in with your human partner between tasks. Execute all tasks from the plan without stopping. The only reasons to stop are: BLOCKED status you cannot resolve, ambiguity that genuinely prevents progress, or all tasks complete.

## The Process

### Setup
1. Read plan file once, extract ALL tasks with full text and context
2. Note overall context (project, tech stack, goals)
3. Create task list with all tasks

### Per Task Loop

For each task:

1. **Dispatch implementer subagent** with:
   - Full task text (don't make them read the plan)
   - Overall project context (scene-setting)
   - Relevant file contents

2. **Handle implementer status:**
   - **DONE:** Proceed to spec compliance review
   - **DONE_WITH_CONCERNS:** Read concerns, address if about correctness, then review
   - **NEEDS_CONTEXT:** Provide missing context and re-dispatch
   - **BLOCKED:** Assess blocker, provide context/use more capable model/break into smaller pieces/escalate

3. **Dispatch spec compliance reviewer** — does code match spec?
   - ✅ Pass → proceed to code quality review
   - ❌ Fail → implementer fixes gaps → re-review

4. **Dispatch code quality reviewer** — is code well-built?
   - ✅ Approved → mark task complete
   - ❌ Issues → implementer fixes → re-review

5. **Mark task complete**, move to next task

### After All Tasks

1. Dispatch final code reviewer for entire implementation
2. Use finishing-a-development-branch skill

## Model Selection

Use the least powerful model that can handle each role:

- **Mechanical tasks** (isolated functions, clear specs, 1-2 files): fast/cheap model
- **Integration tasks** (multi-file, pattern matching, debugging): standard model
- **Architecture/review tasks**: most capable model

## Red Flags

**Never:**
- Start implementation on main/master branch without explicit user consent
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed issues
- Start code quality review before spec compliance is ✅
- Move to next task while either review has open issues
- Let implementer self-review replace actual review

**If reviewer finds issues:**
- Implementer fixes them
- Reviewer reviews again
- Repeat until approved
- Don't skip the re-review

## Integration

- **Before:** Use writing-plans to create the plan
- **Workspace:** Use using-git-worktrees to ensure isolated workspace
- **After all tasks:** Use finishing-a-development-branch
- **Subagents should use:** test-driven-development
