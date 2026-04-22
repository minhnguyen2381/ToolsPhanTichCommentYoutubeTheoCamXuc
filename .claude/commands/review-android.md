---
allowed-tools: Bash(git diff:*), Bash(git log:*), Bash(git show:*), Bash(git rev-parse:*), Bash(git rev-list:*), Read, Glob, Grep
description: Review Android code from a commit hash to HEAD as a Senior Android Developer
user-intent: intent

---

# Android Code Review

Review all Android code changes from commit `$ARGUMENTS` to HEAD.

## Context

- Commit range: `$ARGUMENTS`..HEAD
- Commits in range: !`git log --oneline $ARGUMENTS..HEAD`
- Files changed: !`git diff --name-only $ARGUMENTS..HEAD -- '*.kt' '*.java' '*.xml'`
- Diff stats: !`git diff --stat $ARGUMENTS..HEAD`

## Instructions

1. Load the skill `android-code-review` and follow its workflow precisely
2. The starting commit hash is: `$ARGUMENTS`
3. Review all changes from that commit to HEAD
4. Read the full content of each changed file for context (not just the diff)
5. Load `references/android-review-checklist.md` from the android-code-review skill for detailed review criteria
6. Produce the review report in the format specified in the skill
7. Be thorough - check every dimension for every file
8. Write the review in Vietnamese
