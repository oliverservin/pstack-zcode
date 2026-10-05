# Set up pstack

In this page you install the plugin, pick which subagent types pstack uses, and run your first task. Setup is a few clicks plus a short conversation.

## Install the plugin

This repository doubles as a ZCode marketplace. In ZCode:

1. Open Settings → Plugin Management → Discover → **+**.
2. Add the git URL `https://github.com/oliverservin/pstack-zcode.git` as a marketplace (its root carries `marketplace.json`). A local clone of the repository works too.
3. Install **pstack** from the list.

The plugin appears under Installed when ZCode confirms it.

## Pick your subagent roles

Run:

```text
/setup-pstack
```

[`/setup-pstack`](../../skills/setup-pstack/SKILL.md) detects the subagent types available in your session (built-ins like `general-purpose`, `Explore`, and `code-reviewer`, plus plugin-contributed types like `poteto-agent`), asks for a reasoning budget, shows you each role (code delegates, judgment, the review panels), and asks what you want. Answer the questions. It writes `~/.zcode/pstack-roles.md`, a small file every pstack skill reads.

ZCode runs every subagent on the session model, so what the file configures is the subagent type per role. That is where the diversity comes from. You only override what you care about. A role with no line in the file keeps the skill's default. To restore a default, delete that role's line. A rerun of `/setup-pstack` shows every current choice before it overwrites the file, so it won't silently drop a role you customized.

You might be wondering what happens if you use Auto. Set a role to `inherit-parent` or `auto` and that role's work stays in the main thread instead of a subagent. Both values mean the same thing. For a panel role the value is a list, and one subagent runs per entry, so the list length sets the panel size. Setup also configures `swarm workers`, the default type for every `/swarm` worker unless a race names a type for each arm.

## Accept the verification offer, or don't

At the end of setup, `/setup-pstack` looks for a way to prove app behavior in your project, either a `verify-*` skill or an existing harness. If it finds neither, it offers once to generate one with [`/create-verification-skill`](../../skills/create-verification-skill/SKILL.md).

Say yes and it writes `.zcode/skills/verify-<app>/`, a project-local skill that teaches agents to drive your app the way a user does. It proves the skill works once before handing it over. Say no and setup moves on. You can run `/create-verification-skill` yourself any time. [Verify and ship](./06-verify-and-ship.md#create-a-project-verification-skill) covers it in depth.

If you're new to pstack, say yes. An agent that can check its own work keeps going until the check passes. An agent that can't hands every result back to you to check by hand. Of everything in this guide, the verification skill pays off the most.

Setup writes the roles file once. Skills read it when they run, so your choices apply from the next skill run.

## Keep the cost in check

pstack spends extra tokens on subagents and review panels. That's the price of the rigor. To spend fewer:

- Rerun `/setup-pstack` and pick a smaller reasoning budget or lighter types for the panel roles.
- Set a role to `auto` or `inherit-parent` so its work runs in the main thread instead of a subagent.
- Shorten a panel list. Each entry runs one subagent.
- Save `/poteto-mode` for work that needs rigor. A small, obvious edit doesn't.

## Run your first task

Pick something real but small, and describe it the way you'd describe it to a colleague:

```text
/poteto-mode add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. Its first items are the matched playbook's steps copied in, the Feature playbook for this prompt. If `/poteto-mode` skips a step, the step stays in the list with `skip: <reason>`, so you can see what it chose not to do.

From here you can type normal follow-ups. `/poteto-mode` is a normally invokable skill. Once invoked it stays on across turns, applying itself when a playbook matches or the task needs rigor, and staying out of the way otherwise. Say so to opt out.

Next: [Route work through `/poteto-mode`](./02-poteto-mode.md).
