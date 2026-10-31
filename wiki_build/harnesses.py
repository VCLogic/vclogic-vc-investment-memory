"""Local CLI discovery and explicit selection; never starts a model call."""
import shutil
import subprocess
import sys

import questionary

from .config import MODEL

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
        interactive = sys.stdin.isatty() and sys.stdout.isatty()
    if not interactive:
        raise ValueError('Both Codex and Claude Code are installed. Select --harness codex or --harness claude '
                         'for a non-interactive run; use investor-memory harnesses --json to discover choices.')
    # Same arrow-key menu as the collector wizard; authentication is checked at invocation.
    choice = questionary.select(
        'Which generation harness?',
        choices=[questionary.Choice(f'{name}  ({installed[name]})', value=name) for name in available],
        use_jk_keys=False,
    ).ask()
    if choice is None:
        raise ValueError('Harness selection cancelled; pass --harness explicitly to run later.')
    return choice


def select_model(harness, requested=None, interactive=None):
    """The --model value if given; otherwise ask in a terminal, else the harness default."""
    if requested:
        return requested
    default = MODEL if harness == 'codex' else 'sonnet'
    if interactive is None:
        interactive = sys.stdin.isatty() and sys.stdout.isatty()
    if not interactive:
        return default
    # Claude Code accepts these aliases; other Codex or Claude models are typed in.
    names = [default] + (['opus', 'haiku'] if harness == 'claude' else [])
    choice = questionary.select(
        f'Which {harness} model?',
        choices=[questionary.Choice(f'{name} (default)' if name == default else name, value=name) for name in names]
        + [questionary.Choice('Other: type a model name', value='')],
        use_jk_keys=False,
    ).ask()
    if choice == '':
        choice = questionary.text('Model name').ask()
    if not choice:
        raise ValueError('Model selection cancelled; pass --model explicitly to run later.')
    return choice.strip()


def check_compatibility(name):
    command = [name, 'exec', '--help'] if name == 'codex' else [name, '--help']
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8',
                                errors='replace', timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f'Cannot inspect {name} CLI; repair its installation before generation.') from exc
    missing = [flag for flag in REQUIRED_FLAGS[name] if flag not in result.stdout]
    if result.returncode or missing:
        raise ValueError(f'Incompatible {name} CLI. Update it before generation; missing required flags: {", ".join(missing) or "help failed"}.')
