---
name: git-commit-multi-mission-push
description: "This skill should be used when the user wants to split workspace changes into multiple isolated commits grouped by mission/task and push them. Triggers on /git-commit-multi-mission-push or when user asks to organize changes into separate commits and push. Analyzes all staged/unstaged changes, groups them by logical mission (UI, API, bugfix, etc.), plans Conventional Commits for each group, and generates a single copy-paste bash command block that commits each group separately then pushes to the current branch."
---

# Git Commit Multi-Mission Push

Automate splitting workspace changes into isolated commits by mission and push to the current branch.

## When to Use

- User invokes `/git-commit-multi-mission-push`
- User asks to organize changes into separate commits grouped by task/mission
- User wants to commit and push multiple independent changes without lumping them into one commit

## Workflow

### Step 0: If project has 'git-workflow' skill, load them

### Step 1: Gather Workspace State

Run these commands to collect all necessary information:

```bash
git status
git diff --name-only
git diff --cached --name-only
git diff --stat
git branch --show-current
```

Also read the content of changed files when needed to understand the nature of changes.

### Step 2: Analyze and Group Changes by Mission

Examine every changed file (staged, unstaged, and untracked) and classify each into a logical mission group. Common groupings:

| Group Type | Examples |
|------------|----------|
| `feat` | New feature files, new UI components, new API endpoints |
| `fix` | Bug fixes, error handling corrections |
| `refactor` | Code restructuring without behavior change |
| `docs` | Documentation, README, comments |
| `style` | Formatting, linting, whitespace |
| `chore` | Config files, build scripts, dependency updates |
| `test` | Test files, test utilities |
| `ci` | CI/CD pipeline changes |
| `build` | Build system, packaging changes |
| `perf` | Performance improvements |

**Critical rule**: NEVER combine unrelated changes into a single commit. Each commit must represent one coherent, independent mission. If a file contributes to multiple missions, note this and handle it carefully (stage specific hunks if needed).

### Step 3: Plan Commits

For each mission group, determine:
1. The exact list of files to `git add`
2. A Conventional Commits message: `<type>[optional scope]: <description>`
3. The order of commits (dependencies first, features last)

Commit message rules (from git-workflow skill conventions):
- Use imperative mood, present tense ("add" not "added")
- Keep subject under 72 characters
- Be specific and concise
- Add scope when it clarifies context: `feat(auth):`, `fix(api):`

### Step 4: Present Summary in Vietnamese

Before generating the command block, present a clear summary table in Vietnamese:

```
## Ke hoach Commit

| # | Type | Files | Message |
|---|------|-------|---------|
| 1 | feat | file1.ts, file2.ts | feat(ui): add login form component |
| 2 | fix  | api.ts | fix(api): handle null response in user endpoint |
| 3 | chore | package.json | chore: update dependencies |
```

Wait for user confirmation or adjustment before proceeding.

### Step 5: Generate Executable Command Block

Produce a single, clean bash code block that:
- Uses `git add <specific files>` for each group (NEVER use `git add .` or `git add -A`)
- Chains commands with `&&` so execution stops on any failure
- Ends with `git push` (or `git push -u origin <branch>` if no upstream is set)
- Uses HEREDOC syntax for multi-line commit messages when a body is needed
- Is ready to copy-paste directly into the terminal

Template:

```bash
git add <file1> <file2> && \
git commit -m "<type>: <description 1>" && \
git add <file3> && \
git commit -m "<type>: <description 2>" && \
git push
```

For commits needing a body:

```bash
git add <files> && \
git commit -m "$(cat <<'EOF'
<type>: <description>

<body explaining why>

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)" && \
```

### Step 6: Execute

After user confirms the plan, execute the generated command block. If the user prefers to run it themselves, provide the clean command block for copy-paste.

## Safety Rules

### Protected Branch Warning

Before executing, check if the current branch is a protected branch (`main`, `master`, `develop`, `release/*`). If so, display a warning:

```
WARNING: Dang o nhanh bao ve `<branch>`. Push truc tiep co the bi tu choi.
Can tao nhanh feature truoc khi commit? (Y/n)
```

### Conflict Detection

If `git status` shows merge conflicts or rebase in progress, stop and warn the user before proceeding.

### Untracked Files

Include untracked files in the analysis. Ask the user whether to include or ignore them if their intent is ambiguous.

### No Destructive Operations

- Never run `git reset --hard`, `git checkout -- .`, or `git clean -f`
- Never use `--force` or `--no-verify` flags
- Never amend existing commits unless explicitly requested

## Output Format Rules

1. **Summary first**: Always show the Vietnamese commit plan table before any command
2. **Clean command block**: The bash block must contain ONLY executable commands - no comments, no explanations mixed in
3. **One block**: All commands in a single code block, connected by `&&`
4. **Specific file paths**: Always use explicit file paths in `git add`, never wildcards or `.`
