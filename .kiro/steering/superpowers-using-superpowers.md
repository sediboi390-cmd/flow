---
name: using-superpowers
description: Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions
inclusion: always
---

# Using Superpowers

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## Instruction Priority

Superpowers skills override default system prompt behavior, but **user instructions always take precedence**:

1. **User's explicit instructions** (direct requests) — highest priority
2. **Superpowers skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

## Available Skills

The following Superpowers skills are available as steering files in `.kiro/steering/`:

| Skill | File | When to Use |
|-------|------|-------------|
| brainstorming | `superpowers-brainstorming.md` | Before any creative work, features, or modifications |
| writing-plans | `superpowers-writing-plans.md` | After brainstorming, before touching code |
| executing-plans | `superpowers-executing-plans.md` | When executing a written implementation plan |
| subagent-driven-development | `superpowers-subagent-driven-development.md` | When executing plans with independent tasks |
| test-driven-development | `superpowers-test-driven-development.md` | Before writing any implementation code |
| systematic-debugging | `superpowers-systematic-debugging.md` | When encountering any bug or unexpected behavior |
| verification-before-completion | `superpowers-verification-before-completion.md` | Before claiming work is complete |
| requesting-code-review | `superpowers-requesting-code-review.md` | After completing tasks or major features |
| receiving-code-review | `superpowers-receiving-code-review.md` | When receiving code review feedback |
| finishing-a-development-branch | `superpowers-finishing-a-development-branch.md` | When implementation is complete and ready to integrate |
| using-git-worktrees | `superpowers-using-git-worktrees.md` | When starting feature work needing isolation |
| writing-skills | `superpowers-writing-skills.md` | When creating or editing skills |

## How to Use Skills

When a skill applies, **read the corresponding steering file** and follow its instructions exactly.

## The Rule

**Apply relevant skills BEFORE any response or action.** Even a 1% chance a skill might apply means you should check it.

### Red Flags — STOP, you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |

## Skill Priority

When multiple skills could apply:

1. **Process skills first** (brainstorming, debugging) — determine HOW to approach the task
2. **Implementation skills second** — guide execution

- "Let's build X" → brainstorming first, then implementation skills
- "Fix this bug" → systematic-debugging first, then domain-specific skills
