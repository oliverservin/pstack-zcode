#!/usr/bin/env python3
"""Phase 1: deterministic Cursor->ZCode string replacements across pstack-zcode markdown.

Ordered longest-first. Every replacement is logged. Review with git diff after.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# (old, new) — applied verbatim; order matters (longest first within a theme)
REPLACEMENTS = [
    # benny install paths: Cursor automations dir -> ZCode non-scanned automations dir
    (".cursor/automations/benny/skills/", ".zcode/automations/benny/skills/"),
    (".cursor/automations/benny/", ".zcode/automations/benny/"),
    ("<target-repository>/.cursor/automations/benny/", "<target-repository>/.zcode/automations/benny/"),
    (".cursor/automations/", ".zcode/automations/"),
    # benny user-owned config location
    (".cursor/benny/", ".zcode/benny/"),
    # plugin enablement in target repo: Cursor settings -> ZCode workspace config
    (".cursor/settings.json", ".zcode/config.json"),
    # project-local skills dir
    (".cursor/skills/", ".zcode/skills/"),
    ("~/.cursor/skills/", "~/.zcode/skills/"),
    # pstack role config file
    ("~/.cursor/rules/pstack-models.mdc", "~/.zcode/pstack-roles.md"),
    # tool names
    ("Task subagent", "Agent subagent"),
    ("Task tool", "Agent tool"),
    ("Task call", "Agent call"),
    ("Task calls", "Agent calls"),
    ("`Task`", "`Agent`"),
    ("AskQuestion", "AskUserQuestion"),
    # skill authoring built-in
    ("Cursor's built-in `create-skill` skill", "the `skill-creator` skill (from the `skill-creator` plugin)"),
    ("Cursor's built-in `create-skill`", "the `skill-creator` skill (from the `skill-creator` plugin)"),
    ("**create-skill** skill (Cursor's built-in for authoring SKILL.md files)",
     "**skill-creator** skill (from the `skill-creator` plugin, for authoring SKILL.md files)"),
    ("`/create-skill`", "`/skill-creator`"),
    # cloud agents -> background subagents
    ("One Cursor cloud agent per PR", "One background subagent per PR"),
    ("Cursor cloud agent", "background subagent"),
    # Slack actions
    ("configured Cursor Slack actions", "configured Slack MCP tools"),
    ("Prefer configured Cursor Slack actions", "Prefer configured Slack MCP tools"),
    # 0.15.2: multi-phase-plan skeleton and playbooks
    ("and an explicit model per the Subagents section", "and an explicit subagent type per the Subagents section"),
    ("Ten lanes on `grok-4.6-fast-xhigh` at the PR head", "Ten background lanes at the PR head"),
    ("Browser, Electron, and web UIs use `control-ui` from `cursor-team-kit`. CLIs and TUIs use `control-cli` from `cursor-team-kit`.",
     "Browser, Electron, and web UIs use the `control-browser` skill from the `browser-use` plugin. CLIs and TUIs run in a shell, reading the real output."),
    ("Each live lane runs on its own cloud VM at the PR head. Drive through `control-ui` or `control-cli` from `cursor-team-kit`.",
     "Each live lane runs as its own background subagent at the PR head. Drive browser and web surfaces with the `browser-use` plugin's `control-browser` skill, CLIs in a shell."),
    ("In a local session, a real terminal `/loop`. In a cloud root, a cloud-sleeper wake chain. Never leave the cadence to memory.",
     "A scheduled automation (Cron) that re-fires the tick prompt. Never leave the cadence to memory."),
    ("arm a `/goal` with this exact text", "write the standing orders with this exact text"),
    ("the execution playbook from trunk and the armed /goal", "the execution playbook from the plugin root and the standing orders"),
    ("- [ ] Read these from trunk at program start. Re-read them at every tick.",
     "- [ ] Read these from the installed pstack copy (under `~/.zcode/cli/plugins/cache/`) at program start. Re-read them at every tick."),
    ("`git show origin/main:pstack/", "`<pstack plugin root>/"),
    ("Run `node pstack/skills/poteto-mode/scripts/check-plan.mjs <plan.md>`",
     "Run `node skills/poteto-mode/scripts/check-plan.mjs <plan.md>` from the pstack plugin root"),
    ("The program runs `pstack/skills/poteto-mode/playbooks/", "The program runs the pstack plugin's `skills/poteto-mode/playbooks/"),
    ("run the swarm per `pstack/skills/swarm/SKILL.md`", "run the swarm per `skills/swarm/SKILL.md` from the plugin root"),
    ("`pstack/skills/", "`skills/"),
    ("Run `/deslop` before each commit", "Run the **unslop** skill over the diff before each commit"),
    ("Triage every Bugbot and security-reviewer comment per", "Triage every review-bot and security-reviewer comment per"),
    ("- [ ] Bugbot triage done.", "- [ ] Review-bot triage done."),
    ("of the change on a lane VM", "of the change on a lane instance"),
]


def main() -> int:
    total = 0
    files_touched = 0
    for md in sorted(ROOT.glob("**/*.md")):
        rel = md.relative_to(ROOT)
        if rel.parts[0] in ("docs",) and rel.name.startswith("DESIGN"):
            continue
        text = md.read_text(encoding="utf-8")
        orig = text
        for old, new in REPLACEMENTS:
            if old in text:
                count = text.count(old)
                text = text.replace(old, new)
                print(f"{rel}: {count}x  {old!r} -> {new!r}")
                total += count
        if text != orig:
            md.write_text(text, encoding="utf-8")
            files_touched += 1
    print(f"\n{total} replacements across {files_touched} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
