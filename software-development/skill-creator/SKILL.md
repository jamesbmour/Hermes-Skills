---
name: skill-creator
description: "Use when creating, improving, or evaluating Hermes Agent skills. Triggers on requests to create a new skill from scratch, edit or optimize an existing skill, run evaluations on a skill, benchmark skill performance, or optimize a skill description for better triggering accuracy. Use this whenever the user mentions skills, skill creation, skill improvement, or skill evaluation — even if they don't explicitly ask for the 'skill-creator'."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, authoring, evaluation, optimization, skill-creator]
    related_skills: [hermes-agent-skill-authoring, plan]
---

# Skill Creator

## Overview

A skill for creating new Hermes Agent skills and iteratively improving them. This skill guides you through the full lifecycle: capturing intent, drafting, testing with parallel subagents, evaluating results with the user, and iterating until the skill is solid.

The core loop:

- Decide what the skill should do and roughly how
- Write a draft SKILL.md
- Create test prompts and run them (with-skill vs without-skill)
- Have the user evaluate the results
- Improve the skill based on feedback
- Repeat until satisfied
- Optionally optimize the description for better triggering

Your job is to figure out where the user is in this process and jump in. Some users come with a draft already written — go straight to testing. Others say "I want a skill for X" — you guide them through the whole loop. Be flexible: if the user says "just vibe with me, no evals," accommodate that.

## When to Use

- User asks to create a new skill
- User wants to improve or optimize an existing skill
- User mentions skill evaluation, benchmarking, or testing
- User says "turn this workflow into a skill"
- User asks about description optimization for triggering
- User asks to export, share, transfer, or move a skill to another Hermes install

**Don't use for:** simple one-off skill edits (use `skill_manage(action='patch')` directly), or for in-repo skills (use `hermes-agent-skill-authoring` and `write_file`).

## Communicating with the User

Skill creators will be used by people across a wide range of familiarity with AI agent tooling. Pay attention to context cues:

- "evaluation" and "benchmark" are borderline — OK for most users
- "JSON" and "assertion" — watch for cues that the user knows these terms; briefly define if unsure
- "subagent" and "delegate_task" — explain on first use: "I'll spawn independent agent processes that each complete one test case"

When in doubt, give a short definition. It costs little and prevents confusion.

---

## Creating a Skill

### Step 1: Capture Intent

Start by understanding what the user wants. If the conversation already contains a workflow they want to capture ("turn this into a skill"), extract answers from conversation history: tools used, step sequence, corrections made, input/output formats.

Clarify these questions:

1. **What should this skill enable Hermes to do?**
2. **When should it trigger?** (what user phrases/contexts)
3. **What's the expected output format?**
4. **Should we set up test cases?** Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflows) benefit from test cases. Skills with subjective outputs (writing style, creative work) often don't need them. Suggest the appropriate default, but let the user decide.

Get the user to confirm before proceeding to drafting.

### Step 2: Interview and Research

Probe edge cases, input/output formats, example files, success criteria, and dependencies. Use `session_search` to recall related past work. Check for similar existing skills with `skills_list` that might inform or overlap with this one. Come prepared with context to reduce burden on the user.

### Step 3: Write the SKILL.md

Create the skill at `~/.hermes/skills/<category>/<name>/SKILL.md` using `skill_manage(action='create')`.

Every Hermes skill requires this frontmatter:

```yaml
---
name: my-skill-name               # lowercase, hyphens, ≤64 chars
description: "Use when <trigger>. <one-line behavior>."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [tag1, tag2, tag3]
    related_skills: [other-skill]
---
```

**Critical rules:**
- First bytes MUST be `---` (no leading blank line)
- `name` and `description` are required
- Description ≤ 1024 chars, starts with "Use when ..."
- Body after `---` closing must be non-empty
- Full file ≤ 100,000 chars (aim for 5-15k)

**Description field:** This is the primary triggering mechanism. Include both what the skill does AND contexts for when to use it. Be a little "pushy" — Hermes tends to undertrigger skills. Instead of "How to build a dashboard," write "Use when the user wants a dashboard, data visualization, internal metrics, or to display any kind of data — even if they don't explicitly ask for a 'dashboard.'"

---

## Skill Writing Guide

### Hermes Skill Anatomy

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) — always in context
2. **SKILL.md body** — loaded when skill triggers (<500 lines ideal)
3. **Bundled resources** — loaded on demand

**Key patterns:**
- Keep SKILL.md under 500 lines; add hierarchy with clear pointers if approaching this limit
- Reference files clearly: "see `references/api.md` for full schema"
- For large references (>300 lines), include a table of contents

### Peer-Matched Structure

Follow the structure used by peer skills:

```
# <Title>

## Overview
One or two paragraphs: what and why.

## When to Use
- Bulleted triggers
- Counter-triggers: "Don't use for..."

## <Topic sections specific to the skill>
- Quick-reference tables
- Code blocks with exact commands
- Hermes-specific recipes

## Common Pitfalls
Numbered list of mistakes and their fixes.

## Verification Checklist
- [ ] Checkbox list of post-action verifications
```

### Writing Style

- Prefer imperative form ("Read the file" not "You should read the file")
- Explain **why** things matter, not just what to do. Today's LLMs have good theory of mind — they perform better when they understand the reasoning.
- If you find yourself writing "ALWAYS" or "NEVER" in all caps, or using rigid structures, that's a yellow flag — reframe and explain the reasoning.
- Use concrete examples:
  ```markdown
  ## Output format
  **Example:**
  Input: Added user authentication with JWT tokens
  Output: feat(auth): implement JWT-based authentication
  ```
- Avoid overfitting to specific examples. Write general instructions that work across many prompts.

---

## Running Test Cases

This is a continuous sequence — don't stop partway through.

### Workspace Setup

Create a workspace for results: `~/.hermes/workspaces/<skill-name>/iteration-<N>/`

For each test case, create a subdirectory with a descriptive name (not just "eval-0" — use names like "basic-translation", "error-handling", "large-file"):

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

Save this as `eval_metadata.json` in each eval directory.

### Step 1: Spawn all runs in parallel

For each test case, spawn TWO `delegate_task` subagents in the same turn — one with the skill, one without. Launch everything at once.

**With-skill run:**

```
delegate_task(
    goal="Execute the following task using the skill named '<skill-name>'.",
    context="First, load the skill with skill_view(name='<skill-name>'). Then follow its instructions to complete the task below. Save all outputs to <workspace>/iteration-<N>/<eval-name>/with_skill/outputs/ using write_file.

Task: <eval prompt>
Input files (if any): <list or 'none'>
Save outputs: <what to save — e.g., 'the generated Python file', 'the final CSV'>",
    toolsets=["terminal", "file", "skills"]
)
```

**Without-skill (baseline) run:**

```
delegate_task(
    goal="Execute the following task WITHOUT using any specialized skill.",
    context="Do NOT load any skill for this task. Complete it using only your general knowledge and available tools. Save all outputs to <workspace>/iteration-<N>/<eval-name>/without_skill/outputs/ using write_file.

Task: <eval prompt>
Input files (if any): <list or 'none'>
Save outputs: <same as with-skill>",
    toolsets=["terminal", "file"]
)
```

**For improving an existing skill:** snapshot the current version first:
```bash
cp -r ~/.hermes/skills/<category>/<skill-name> <workspace>/skill-snapshot/
```
Then point the baseline subagent at the snapshot by inlining the old SKILL.md in its context. Name the directory `old_skill/outputs/`.

### Step 2: While runs are in progress, draft assertions

Don't just wait. Draft quantitative assertions for each test case and explain them to the user. Good assertions:
- Are objectively verifiable (file exists, output contains specific string, exit code is 0)
- Have descriptive names that read clearly in results
- Can be checked programmatically (write a script rather than eyeballing)

Subjective skills (writing style, design) are better evaluated qualitatively — don't force assertions.

Save assertions to `eval_metadata.json` and also maintain an `evals/evals.json` at the workspace root:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "assertions": [
        {"name": "output file exists", "check": "..."},
        {"name": "contains expected header", "check": "..."}
      ],
      "files": []
    }
  ]
}
```

### Step 3: Grade and present results

Once all runs complete:

1. **Read each subagent's outputs** from the workspace directories
2. **Grade each run** against the assertions. For programmatic checks, write and run a script:
   ```python
   from hermes_tools import read_file
   # Check if output file exists and contains expected content
   ```
3. **Present results to the user** in the chat. For each test case, show:
   - The prompt
   - With-skill output summary
   - Without-skill output summary
   - Which assertions passed/failed
   - Your observations about what worked and what didn't

Say something like: "Here are the results for each test case. Take a look — what do you think works well, and what needs improvement?"

### Step 4: Collect feedback

Ask the user for specific feedback on each test case. What worked? What didn't? What should the skill do differently? Record their feedback and use it to guide the next iteration.

---

## Improving the Skill

This is the heart of the loop. After the user reviews results:

### How to think about improvements

1. **Generalize from feedback.** The user is looking at a few examples, but the skill will be used thousands of times. Don't overfit — if a stubborn issue persists, try different metaphors or patterns of working rather than adding fiddly constraints.

2. **Keep the prompt lean.** Read the subagent transcripts, not just final outputs. Remove parts of the skill that waste time or cause unproductive behavior.

3. **Explain the why.** Try hard to explain the reasoning behind every instruction. LLMs perform better when they understand the rationale, not just the rule.

4. **Look for repeated work across test cases.** If all 3 subagents independently wrote similar helper scripts, the skill should bundle that script. Put it in `scripts/` and tell the skill to use it. Use `skill_manage(action='write_file', file_path='scripts/my_script.py')`.

### The iteration loop

1. Apply improvements to the skill using `skill_manage(action='patch')` or `skill_manage(action='edit')`
2. Create a new `iteration-<N+1>/` workspace
3. Rerun all test cases (with-skill and baseline)
4. Present results, comparing against previous iteration
5. Collect feedback, improve again

Keep going until:
- The user says they're satisfied
- All feedback is positive
- You're not making meaningful progress

---

## Description Optimization

After the skill is solid, offer to optimize the description for better triggering accuracy.

### How Hermes skill triggering works

Hermes sees all skills' `name` + `description` in its `available_skills` list. It decides whether to load a skill based on that description. Hermes only consults skills for tasks it can't easily handle on its own — simple one-off queries may not trigger a skill even with a perfect description. Complex, multi-step, or specialized queries reliably trigger skills when the description matches.

### The optimization process

1. **Generate trigger eval queries** — 15-20 realistic user prompts. Mix of should-trigger (8-10) and should-not-trigger (8-10). Focus on edge cases and near-misses:
   - Good should-trigger: varied phrasings, casual and formal, cases that need the skill but don't name it
   - Good should-not-trigger: adjacent domains, ambiguous phrasing where keywords overlap but the task is different
   - Bad should-not-trigger: obviously unrelated ("write fibonacci" for a PDF skill)

2. **Review with the user** — present the eval set and let them adjust

3. **Test the description** — for each query, spawn a `delegate_task` subagent that judges whether the skill would be triggered:
   ```
   delegate_task(
       goal="Given the skill name '<name>' and description '<description>', would you load this skill for the following user prompt? Answer YES or NO only.",
       context="User prompt: <query>",
       toolsets=[]
   )
   ```
   Run each query 3 times for reliability.

4. **Iterate** — based on false negatives (should trigger but didn't) and false positives (shouldn't trigger but did), refine the description. Repeat until satisfied.

5. **Apply** — update the skill's description with `skill_manage(action='patch')`. Show the user before/after.

---

## Common Pitfalls

1. **Creating a skill that's too narrow.** The skill should work for a class of tasks, not just the test cases. Look at the transcripts — if the subagent followed instructions mechanically without understanding, the skill is too rigid.

2. **Over-testing subjective skills.** If the skill produces writing, designs, or creative output, skip quantitative assertions. Focus on qualitative feedback from the user.

3. **Forgetting to snapshot old skill on improvement.** Always copy the current skill before editing, so the baseline subagent can run against the old version.

4. **Not reading subagent transcripts.** The final output tells you whether it worked. The transcript tells you why. Always read transcripts to find wasted steps, misinterpretations, and opportunities to streamline.

5. **Using `skill_manage(action='create')` expecting it to go in-repo.** It writes to `~/.hermes/skills/`. For in-repo skills, use `write_file` and follow the `hermes-agent-skill-authoring` skill.

6. **Description too vague or too long.** "Use when debugging" is too generic. A description that's 1000+ chars will be truncated. Include trigger contexts but stay under 1024 chars.

7. **Not following peer structure.** Every shipped Hermes skill follows `## Overview` → `## When to Use` → body → `## Common Pitfalls` → `## Verification Checklist`. Deviate and your skill will feel out of place.

8. **Running test cases one at a time.** Spawn all `delegate_task` calls in the same turn so they run in parallel. Serial execution doubles the wait time.

## Sharing & Exporting Skills

To transfer a locally-created skill to another Hermes install, there are
four mechanisms ranging from tarball to publishing to a GitHub registry.
Key gotchas: `hermes skills snapshot export` only captures hub-installed
skills (not local ones), `hermes skills install` requires a directory
path (not a bare `SKILL.md` file), `hermes skills publish` may fail with
"GitHub token lacks permission to fork repos" (workaround: manual `gh`
push), and some local skills are symlinks to `~/.agents/skills/` so use
`cp -RL` or resolve the real path when copying. Full details in
`references/skill-sharing.md`.

---

## Verification Checklist

- [ ] Skill has valid YAML frontmatter: `---` at byte 0, `name` + `description` present
- [ ] Description ≤ 1024 chars, starts with "Use when ..."
- [ ] Name ≤ 64 chars, lowercase + hyphens
- [ ] Body is non-empty, structured with `## Overview` + `## When to Use`
- [ ] Workspace created at `~/.hermes/workspaces/<skill-name>/`
- [ ] Test cases have descriptive names, not just "eval-0"
- [ ] Both with-skill and without-skill runs spawned for each test case
- [ ] Subagent transcripts read, not just final outputs
- [ ] User feedback collected and used to guide improvements
- [ ] Skill improved based on feedback, not just test-case patched
- [ ] No hardcoded paths or environment-specific assumptions in the skill
- [ ] `related_skills` references real, existing skills
