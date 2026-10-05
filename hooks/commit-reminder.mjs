// Subcommand test, not a regex on the whole string: walk tokens after "git", skip global flags (the set that take a separate value) and valueless flags, then compare the first positional token to "commit". Catches "git -C path commit", rejects "git log ... commit".
const FLAGS_WITH_VALUE = new Set(["-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--super-prefix"]);
let raw = "";
process.stdin.on("data", (chunk) => {
  raw += chunk;
});
process.stdin.on("end", () => {
  try {
    const input = JSON.parse(raw);
    const command = input && input.tool_input && input.tool_input.command;
    if (typeof command === "string") {
      const tokens = command.split(/\s+/);
      let i = tokens.indexOf("git");
      let isCommit = false;
      if (i !== -1) {
        i += 1;
        while (i < tokens.length && tokens[i].startsWith("-")) {
          i += FLAGS_WITH_VALUE.has(tokens[i]) ? 2 : 1;
        }
        isCommit = tokens[i] === "commit";
      }
      if (isCommit) {
        process.stdout.write(
          JSON.stringify({
            hookSpecificOutput: {
              hookEventName: "PreToolUse",
              additionalContext:
                "Before you commit, run the unslop skill over the staged diff and your reply. poteto-mode's Before-commit trigger.",
            },
          })
        );
      }
    }
  } catch {}
  process.exit(0);
});
