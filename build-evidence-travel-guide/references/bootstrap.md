# Bootstrap and platform diagnostics

## Contents

1. Decision sequence
2. Install Agent-Reach
3. Install and connect OpenCLI
4. Browser and authentication boundary
5. Diagnostics
6. Failure recovery

## 1. Decision sequence

1. Check `agent-reach --version`.
2. If present, run `agent-reach doctor --json`.
3. If absent, prefer the official Agent-Reach installer.
4. Install only the channels needed for the requested platforms.
5. For Xiaohongshu, Reddit, Instagram, Facebook, or X, verify a browser-backed backend and user-controlled login state.
6. Inspect the installed router/skill and active backend help before constructing commands.
7. Test one supported read-only search and one supported full-post read before starting a large batch.

Installation is not evidence of access.
Agent-Reach is a capability/router and health layer; `agent-reach search ...` is not
a portable platform-read command. Never invent that command.

## 2. Install Agent-Reach

Official source:

`https://github.com/Panniantong/Agent-Reach`

Official installation instructions:

`https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md`

### Skill installation

For agents supporting the skills CLI:

```text
npx skills add Panniantong/Agent-Reach@agent-reach
```

### Isolated Python installation

Prefer `pipx`. If unavailable, use a virtual environment.

Windows PowerShell:

```powershell
py -3 -m venv "$env:USERPROFILE\.agent-reach-venv"
& "$env:USERPROFILE\.agent-reach-venv\Scripts\python.exe" -m pip install "https://github.com/Panniantong/agent-reach/archive/main.zip"
& "$env:USERPROFILE\.agent-reach-venv\Scripts\agent-reach.exe" install --env=auto --channels=opencli
```

macOS/Linux:

```bash
python3 -m venv "$HOME/.agent-reach-venv"
"$HOME/.agent-reach-venv/bin/python" -m pip install "https://github.com/Panniantong/agent-reach/archive/main.zip"
"$HOME/.agent-reach-venv/bin/agent-reach" install --env=auto --channels=opencli
```

Use `--safe` for inspection without system-package changes and `--dry-run` to preview actions.

## 3. Install and connect OpenCLI

Official source:

`https://github.com/jackwener/opencli`

Requirements: Node.js 20 or later.

```text
node --version
npm install -g @jackwener/opencli@latest
opencli doctor
```

Install the official OpenCLI Browser Bridge extension from the browser store or the project’s signed release instructions. Chromium-based Microsoft Edge is compatible, but extension-store availability may differ; use Edge’s permitted Chrome-extension installation path when necessary.

Verify:

```text
opencli doctor
opencli profile list
opencli list
```

When several browser profiles are connected, explicitly choose one. Never guess which profile contains the user’s travel-platform login.
After `opencli list`, inspect the advertised application/action help and use only
commands actually exposed by the installed version. Platform actions drift between
versions, so this skill deliberately does not hard-code a universal Xiaohongshu
search command.

## 4. Browser and authentication boundary

- Let the user log in manually.
- Do not read or export browser cookies automatically.
- Do not copy authentication data into logs, evidence files, or a public repository.
- Use read commands only.
- Do not evade CAPTCHA, platform rate limits, or access controls.
- Keep 2-3 seconds between repeated social requests and stop when challenged.

## 5. Diagnostics

Run:

```text
agent-reach doctor --json
opencli doctor
opencli profile list
opencli list
```

For each requested platform record:

- installed backend;
- connectivity;
- login state verified by an actual read command;
- timestamp;
- limitation or fallback.

Do not label a `warn` channel usable until an actual search succeeds.
Do not label a search backend usable for evidence until a result can also be opened
as `full_post_opened` or `full_indexed_text`. Record the exact supported command or
tool call used in the run notes; never substitute a command remembered from another
version.

## 6. Failure recovery

### Windows installer cannot find npm

Inspect `Get-Command node,npm,npx`. If npm exists as `npm.cmd`, invoke its absolute path. Do not reinstall unrelated packages blindly.

### Browser extension is installed but disconnected

- Ensure the intended Chromium profile is open.
- Confirm the extension is enabled.
- Run `opencli doctor`.
- List profiles and select the intended profile.
- Restart the OpenCLI daemon only through supported commands.

### Search works but full post fails

For Xiaohongshu, use the complete search-result URL containing the current `xsec_token`. A bare note ID is insufficient.

### Reddit or local platform unavailable

Use public web indexing, primary local sources, maps, accessible review sites, and other platforms. Label the missing platform explicitly; do not claim it was searched successfully.
