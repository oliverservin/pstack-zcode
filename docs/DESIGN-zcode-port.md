# pstack → ZCode port: design

Date: 2026-08-20. Translated to English on 2026-09-21.
Source: [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) v0.14.1, MIT, by Lauren Tan (poteto).
A pristine baseline was committed before any change (see the git history).

## Goal

Ship the whole of pstack as a working ZCode plugin. That means 41 skills (about 20 workflow skills plus 21 `principle-*`), 22 playbooks routed by `/poteto-mode`, 2 subagents (`poteto-agent`, `comment-sicko`), the CLI scripts (orch and watch-pr, bun plus TypeScript), and the "benny" automation package.

## Chosen approach: fork with an adaptation layer

Copy the entire plugin and adapt everything Cursor-specific. Keep `.cursor-plugin/` untouched, so the fork still installs in Cursor. This is the same multi-harness pattern superpowers uses. Add `.zcode-plugin/plugin.json` and a root `marketplace.json` for installation through a local marketplace.

Rejected alternatives:

1. **Curated core** (poteto-mode plus the main skills only). Rejected because the request was the full plugin, and it would lose arena, swarm, interrogate, and reflect, which are pstack's parallelism machinery.
2. **Loose skills in `~/.agents/skills/`**. Rejected because without a plugin manifest there is no agent contribution (`poteto-agent` and `comment-sicko` become `subagent_type`s only through a plugin) and no install or update history.

## Cursor → ZCode concept mapping

| Cursor | ZCode |
|---|---|
| `Task` tool with `subagent_type` + `model` | `Agent` tool with `subagent_type` (no `model`) |
| Multi-model role routing (sol/grok/fable/opus) | Routing by **subagent type** plus varied prompts: `poteto-agent`, `comment-sicko`, `code-reviewer`, `code-architect`, `code-explorer`, `general-purpose`, `Explore` |
| `~/.cursor/rules/pstack-models.mdc` (an always-apply rule) | `~/.zcode/pstack-roles.md` (a file the skills read on demand, with an inline fallback) |
| `/setup-pstack` picks models | `/setup-pstack` picks the **subagent per role** and writes `~/.zcode/pstack-roles.md` |
| `AskQuestion` | `AskUserQuestion` |
| `/create-skill` (a Cursor built-in) | the official `skill-creator` plugin plus our own `authoring-a-skill` playbook |
| `cursor-team-kit`: `/deslop`, `control-cli`, `control-ui` | removed as hard dependencies. The `unslop` skill covers `/deslop`. UI control points at the `browser-use` plugin when present |
| bugbot / agentic security review | ZCode code review (`code-reviewer`) with the same skeptical posture. bugbot-triage stays as the generic bot-triage reference |
| `/loop` (Cursor) | ZCode scheduled automations (the Cron tools: CronCreate, CronUpdate, CronList, CronDelete) |
| `.cursor/automations/benny/` installed in the target repo | skills copied to `<repo>/.zcode/skills/` plus scheduling through Cron |
| `/add-plugin pstack` (Cursor marketplace) | a local marketplace. This repo is itself a marketplace (root `marketplace.json`); install through Settings → Plugin Management → Discover → **+** |
| `subagent_type: "Comment Sicko"` | `subagent_type: "comment-sicko"` (name normalized, because `subagent_type` accepts no space) |

### Assumed degradation: model diversity

ZCode exposes no per-subagent model choice. Multi-model panels (how critics, arena runners, interrogate reviewers, and so on) become **N parallel subagents on the same model**, differentiated by subagent type and prompt. Diversity survives as perspective (reviewer versus architect versus explorer), not as model family. "A second opinion is the same prompt against a different model" becomes "...against a different subagent type".

## Changes by area

1. **Manifests.** New `.zcode-plugin/plugin.json` (`name: pstack`, `skills: ./skills/`, `agents: ./agents/`, attribution to the original author). `.cursor-plugin/` untouched. `marketplace.json` at the root, listing the plugin with `source: "./"`.
2. **`skills/poteto-mode/SKILL.md`.** Subagents section rewritten (`Agent` call defaults: `run_in_background: true`, no `model`, role routing reads `~/.zcode/pstack-roles.md`). Cursor built-in references replaced with the ZCode equivalents. A note that Cursor's "mode" becomes a normally invokable skill.
3. **`skills/setup-pstack/SKILL.md`.** Full rewrite. It detects the subagent types available in the session (built-ins plus plugin-contributed), maps each role to a subagent, and writes `~/.zcode/pstack-roles.md` in a shape analogous to the original.
4. **Fan-out skills** (`how`, `why`, `arena`, `swarm`, `interrogate`, `reflect`, `architect`, `recall`, `no-comments`, `show-me-your-work`, `automate-me`, `create-verification-skill`, `maintain-verification-skill`). `Task`→`Agent`, the `model` field removed, panels become subagent lists, `AskQuestion`→`AskUserQuestion`, `~/.cursor/rules/...`→`~/.zcode/pstack-roles.md`.
5. **Playbooks** (babysit, shipping, autonomous-run, autopilot-*, orchestrate, authoring-a-skill, opening-a-pr, eval, pause-safely, session-pickup, worktree-cleanup, visual-parity, bug-fix). Same treatment. `/loop` becomes Cron. bugbot becomes generic bot review. control-cli and control-ui point at browser-use.
6. **TypeScript scripts.** `watch-pr`: the `CURSOR_AUTOMATION_ID` marker becomes `ZCODE_AUTOMATION_ID`, and bot-author detection accepts `zcode` in addition to `cursor`. The GraphQL pagination term "cursor" is a false positive and stays untouched. Tests updated. `orch`, `bootstrap`, and `worktree-audit.sh` did not reference the harness at 0.14.1.
7. **Benny.** `FOR_AGENTS.md` and `setup-benny` install into `<repo>/.zcode/skills/` and register the two automation prompts through CronCreate. `control-adapter.md` points at `browser-use`.
8. **docs/guide plus README.** Install and get-started rewritten for ZCode. The models section became the subagents section. Upstream attribution stays prominent (MIT).
9. **Frontmatter.** Cursor's extra fields (`icon`, `color`, `reminder`, `mode`, `disable-model-invocation`) are kept. They are harmless when ignored and preserve Cursor compatibility. `name:` normalized to kebab-case where needed (`Comment Sicko` → `comment-sicko`; `Poteto Mode` → `poteto-mode`).

## Known interactions

- `tdd` and `teach` already exist in the user's `~/.agents/skills/`. ZCode gives plugin skills the lowest precedence, so pstack's `tdd` and `teach` are shadowed when invoked by bare name. The behavior stays equivalent. For poteto's flavor, remove the old skills or invoke them qualified (`pstack:tdd`).
- About 41 skills plus 2 agents entered ZCode's global skill list at 0.14.1, the same footprint as superpowers. After the 0.15.2 sync the count is 47 skills.

## Installation (end user)

1. Settings → Plugin Management → Discover → **+** → add the git URL `https://github.com/oliverservin/pstack-zcode.git` (the repo root is a marketplace listing `pstack`), or point at a local clone of it.
2. Install **pstack**.
3. Optional: `/setup-pstack` to pick the subagent per role.
4. Use: `/poteto-mode <request>`.

## Verification

- `bun test` on the scripts (orch, watch-pr) passes.
- A post-port `grep` finds no prose or code Cursor-isms, except GraphQL pagination and deliberate historical mentions of upstream.
- The `.zcode-plugin/plugin.json` manifest validates against the format (name regex `^[a-z0-9][a-z0-9._-]{0,127}$`, `skills`/`agents` fields).
- Skill structure: every `skills/*/SKILL.md` has frontmatter `name` + `description`, and `name` equals its directory in kebab-case.

## Sync 0.15.2 (2026-09-21)

Upstream delta 0.14.1 → 0.15.2: 94 M, 5 A (`assets/logo.png`, `make-bot-ui`, `principle-attack-the-premise`, `principle-test-behavior-not-implementation`, `scripts/check-plan.mjs`), 3 D (`how/references/critic-prompt.md`, `critique-rubric.md`, `poteto-mode/references/plan.md`). Critique mode and plan.md are gone upstream. We followed the new shape and resurrected nothing.

Approach: a pure sync commit first, then the `adapt-phase1.py`/`adapt-phase2a.py` codemods, extended with about 30 new entries for 0.15.2 strings (control-ui, control-cli, `/loop`, `/goal`, the grok slug, create-skill, "model family" language), then a per-file three-way merge (base `3d2fea8`, port `295921e`, upstream 0.15.2) with manual resolution of the hotspots: poteto-mode's Subagents section, setup-pstack (the type-per-role design kept, with upstream's budget ask incorporated as a reasoning-preference record and no pretense of model rewriting), README, how, and the playbooks upstream rewrote (shipping, babysit, opening-a-pr, and autopilot-* now abstract the forge as "Origin"; the abstraction is harness-neutral and was kept, with cloud agent, deslop, and loop adapted). `make-bot-ui` was adapted with an honest split: a webhook backend (Cursor) versus a local JSONL log drained by a Cron automation (ZCode, which has no inbound webhook). `check-plan.mjs` markers were synchronized to the adapted skeleton, and it validates with 0 problems.

Audit fixes: `worktree-audit.sh` gains `PSTACK_TRANSCRIPTS_DIR`. Without it, LAST_CHAT reports "unknown" with a stderr note, and no path is invented. `create-skill` → `skill-creator` in automate-me and reflect/synthesizer. A "runtime prerequisites" section in the README (gh, bun, gt). A `gt` presence check in `orch.ts` (`frontier set`) before any shell-out, with a clear message. Version `0.15.2-zcode.1`; marketplace renamed `pstack-zcode` (owner oliderservin).

Post-sync (same date): the "model diversity does not survive" degradation is refined. The `Agent` tool picks no model, but dynamic workflows accept `subagent_model` per run (enumerate the choices with `ListModels`). `arena` gained the "Model bakeoff" variant: one workflow per contestant model, the same prompt, rubric, and paths, with normal pick and graft across runs. The type arena stays the default.

## Sync 0.15.13 (2026-10-05)

Upstream delta 0.15.2 → 0.15.13: 62 shared files (56 M, 6 A: `benchmark-checklist`, `correct`, `poteto-help` plus its two references, `principle-explain-the-number`), no upstream deletions. Waves: the 2026-09-23 skill updates with Opus 5.5/Grok 4.7 defaults and the 19-instruction cut (#414, #416, #419, #422), 0.15.6 (explain-the-number, benchmark-checklist, fresh subagents, the hourly autopilot tick, PR headings, the schema-first cast), `/correct` (#494), the architect agent-mistake red flags (#495), the bare performance mantras (#496), `/poteto-help` with its prompting references (#502, #506, #507), and the guide refresh (#508). Skill count after the sync: 51.

Approach: the 0.15.2 procedure again. A pure sync commit first (`c842740`, verbatim upstream at the 63 changed shared paths), then the codemods (84 mechanical replacements), then a per-file three-way merge (base `9f56434`) fanned out to three subagents over disjoint partitions (poteto-mode plus playbooks plus reflect, the other skills plus the new skills, README plus guide plus `poteto-agent.md`). Model panels became subagent-type panels throughout, and upstream's per-playbook role lines (`feature, refactoring`, `bug-fix`, `perf-issue`, `hillclimb`, `hardest tasks`, `judgment and prose`) survive with type values in `~/.zcode/pstack-roles.md`. `check-plan.mjs` markers were re-synchronized ("Ten background lanes at the PR head", installed-copy and hourly markers) and the extracted skeleton validates with 0 problems. Upstream's `cloud_base_branch` swarm line became "each worker creates its own git worktree", because subagents share the parent's checkout. The sync clobbered three deliberate fork additions and review restored them: the arena Model bakeoff variant, the fork's setup-pstack design, and the fork's ZCode MCP-discovery text in `why`. `poteto-help` is the heaviest new adaptation: marketplace install, the sticky-skill phrasing, honest attribution, and ZCode equivalents throughout its "Not in pstack" map. The guide's `/loop` and Cursor Projects sections became Cron automations and standing coordinator chats in separate workspaces.

Audit fixes during review: setup-pstack's example `why investigators` line changed from `Explore` to `general-purpose` (a read-only type strips MCP access), poteto-mode's hardest-changes sentence now names the `hardest tasks` role instead of the judgment role, "Cross-model review of the trail" became "Cross-type", an orchestrate verifier "different model family" leftover became "different subagent type", a duplicated Fresh-subagents paragraph was deduplicated, and six semicolon sentences were split per unslop. Version `0.15.13-zcode.1`.

## ZCode modernization (2026-10-05)

ZCode gained features since the adaptation layer was designed on 2026-09-21. This pass adopts them.

- **ReadSessionContext for prior-session reads.** `recall`, `automate-me`, `session-pickup`, and `reflect` now locate the workspace's session files to enumerate candidate session ids cheaply (listing only), then read each candidate through the `ReadSessionContext` tool with a focused query instead of parsing JSONL by hand. Direct transcript reading stays the fallback when the tool is unavailable or rejects an id. The current session's own transcript stays path-based, because the tool reads persisted other sessions, not reliably the in-flight one.
- **Commit-reminder hook.** New `hooks/hooks.json` registers a PreToolUse hook matched on the `Bash` tool, and `hooks/commit-reminder.mjs` implements it. The manifest gains `"hooks": "hooks/"`. The output shape came from research into the shipped plugins. superpowers 5.1.0 ships the one real `additionalContext` example, a SessionStart hook emitting the nested `hookSpecificOutput` object with `hookEventName` and `additionalContext`, so the reminder copies that exact shape with `hookEventName: "PreToolUse"`. The script only ever exits 0, so it never blocks or errors a commit. Installing pstack auto-enables ZCode's hook runner, because plugin hooks do that.
- **Idle-time tasks.** Guide 07 gained a short section on `OffPeakCreate`, which queues deferrable work for off-peak compute at no plan-quota cost. It is distinct from the Cron automations, which fire on a schedule.
- **Agent lifecycle tools.** poteto-mode's `Agent` defaults paragraph names `TaskOutput` for waiting on a background agent and `SendMessage` for messaging or resuming one.

Considered and skipped:

- **AGENTS.md pointer for the roles file.** On-demand reads keep the context window clean. An always-injected pointer taxes every session.
- **Dynamic workflows for swarm and autopilot.** Arena already uses the model-picking lever. Churning the Agent-based playbooks is a redesign, not a modernization.
- **`when_to_use` frontmatter.** The descriptions already carry triggers. Duplication buys nothing.
- **userConfig toggle for the hook.** There is no supported way for a hook script to read config values.

Two honest facts. `disable-model-invocation` is not a recognized ZCode frontmatter key, so typed-only skills stay model-invocable in ZCode today. The zcode-guide doc claims plugin `agents` fields are "recorded but not executed", while this very session lists `poteto-agent` and `comment-sicko` as live types, so that doc note is stale.
