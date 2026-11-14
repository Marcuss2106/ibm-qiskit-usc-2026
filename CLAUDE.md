# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this project.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:46cd31e7 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/core-concepts/sync-concepts.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   bd dolt push
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->


## Build & Test

Start with `docs/DEVELOPMENT.md` (plan, invariants, current findings).

```bash
python -m venv qiskit-env && source qiskit-env/bin/activate
pip install -r requirements.txt
python -m pytest -q tests           # offline, synthetic data
python -m qemcmc.data [--refresh]   # prices -> data/instances.npz (--refresh re-downloads)
python -m qemcmc.objective          # answer key -> results/answer_key_*.csv
python -m qemcmc.landscape          # local optima -> results/landscape_*.csv
```

### Getting the beads (first time)

Beads are not visible on GitHub; load them with the `bd` CLI.

```bash
curl -sSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
bd bootstrap        # in the repo root: clones the shared beads from origin
bd ready            # available work; bd show <id> for details and notes
```

Already set up: `bd dolt pull`. Pull before claiming (`bd update <id> --claim`) so two
people don't take the same bead; `bd dolt push` after changes (needs repo write access).
`.beads/issues.jsonl` in git may be stale; trust `bd`, not that file.

## Architecture Overview

Package `qemcmc/`: `data.py` (prices, 64 quarterly windows of mu and Sigma),
`states.py` (numbering of valid portfolios, swap neighbors, Qiskit bit order),
`objective.py` (score and answer key), `landscape.py` (local optima). Outputs in
`data/` and `results/`; one-off studies in `experiments/`. Details in
`docs/DEVELOPMENT.md` §10.

## Conventions & Patterns

- Reuse `StateSpace` ranks for anything indexed by portfolio (proposal tables, chains).
- Log attempts, score evaluations, shots and wall-clock time as separate fields.
- Tests must not use the network.
