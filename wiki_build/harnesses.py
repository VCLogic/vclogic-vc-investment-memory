"""Local CLI discovery and explicit selection; never starts a model call."""
import shutil
import subprocess
import sys

REQUIRED_FLAGS = {
    'codex': ('--ignore-user-config', '--ephemeral', '--output-schema', '--output-last-message', '--sandbox', '--json'),
    'claude': ('--print', '--json-schema', '--output-format', '--tools', '--strict-mcp-config',
               '--safe-mode', '--no-session-persistence', '--disable-slash-commands'),
}


def discover():
    return {name: shutil.which(name) for name in REQUIRED_FLAGS}


def select_harness(requested='auto', interactive=None):
    installed = discover()
    if requested != 'auto':
        if requested not in installed or not installed[requested]:
            raise ValueError(f'{requested} harness is not installed on PATH. Install and authenticate it before generation.')
        return requested
    available = [name for name, path in installed.items() if path]
    if not available:
        raise ValueError('Requirement: install and authenticate Codex CLI or Claude Code on PATH before generation. '
                         'Offline inventory, preparation and validation do not require a harness.')
    if len(available) == 1:
        return available[0]
    if interactive is None:
        interactive = sys.stdin.isatty()
    if not interactive:
        raise ValueError('Both Codex and Claude Code are installed. Select --harness codex or --harness claude '
                         'for a non-interactive run; use investor-memory harnesses --json to discover choices.')
    print('Available generation harnesses (authentication/model access not checked):', file=sys.stderr)
    for i, name in enumerate(available, 1):
        print(f'  {i}. {name}: {installed[name]}', file=sys.stderr)
    while True:
        try:
            print('Which harness do you prefer? Enter a name or number (q to cancel): ', end='', file=sys.stderr, flush=True)
            choice = input().strip().lower()
        except (EOFError, KeyboardInterrupt) as exc:
            raise ValueError('Harness selection cancelled; pass --harness explicitly to run later.') from exc
        if choice in available:
            return choice
        if choice.isdigit() and 1 <= int(choice) <= len(available):
            return available[int(choice)-1]
        if choice in ('q', 'quit', 'cancel'):
            raise ValueError('Harness selection cancelled.')
        print('Choose one of the listed harnesses.', file=sys.stderr)


def check_compatibility(name):
    command = [name, 'exec', '--help'] if name == 'codex' else [name, '--help']
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f'Cannot inspect {name} CLI; repair its installation before generation.') from exc
    missing = [flag for flag in REQUIRED_FLAGS[name] if flag not in result.stdout]
    if result.returncode or missing:
        raise ValueError(f'Incompatible {name} CLI. Update it before generation; missing required flags: {", ".join(missing) or "help failed"}.')
