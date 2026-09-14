"""CLI: python -m wiki_build {prepare,build,check}."""
import argparse
import json
import sys
from pathlib import Path

from .config import MODEL, BATCH_CHARS
from .prep_corpus import prepare
from .generator import SolGenerator, build
from .check_wiki import validate


def main():
    parser = argparse.ArgumentParser(description='Build a cited investor investment memory with Sol')
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare', help='inspect curated sources without calling a model')
    prep.add_argument('investor_dir', type=Path)
    prep.add_argument('--output', type=Path)
    run = commands.add_parser('build', help='prepare, generate with Sol, validate, publish')
    run.add_argument('investor_dir', type=Path)
    run.add_argument('--output', type=Path, required=True)
    run.add_argument('--cache-dir', type=Path, default=Path('.wiki-cache'))
    run.add_argument('--model', default=MODEL)
    run.add_argument('--timeout', type=int, default=900, help='seconds per model call')
    run.add_argument('--batch-chars', type=int, default=BATCH_CHARS)
    check = commands.add_parser('check', help='validate an existing generated wiki offline')
    check.add_argument('wiki_dir', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'check':
            errors = validate(args.wiki_dir)
            print(json.dumps({'valid': not errors, 'errors': errors}, indent=2))
            return 1 if errors else 0
        if args.output:
            source, dest = args.investor_dir.resolve(), args.output.resolve()
            if source == dest or source in dest.parents or dest in source.parents:
                raise ValueError('Output must be outside the input directory and not an ancestor of it')
            if dest.exists():
                raise FileExistsError(f'Output already exists: {dest}')
        if args.command == 'build':
            cache = args.cache_dir.resolve()
            if cache == source or source in cache.parents:
                raise ValueError('Cache must be outside the input directory')
            if cache == dest or dest in cache.parents:
                raise ValueError('Cache must be outside the output directory')
            if args.timeout <= 0:
                raise ValueError('Timeout must be positive')
        prepared = prepare(args.investor_dir)
        if args.command == 'prepare':
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(prepared, indent=2, ensure_ascii=False) + '\n')
            summary = {k: prepared[k] for k in ('vc_slug', 'corpus_chars', 'thin_corpus', 'warnings')}
            summary.update(documents=len(prepared['documents']), excluded=len(prepared['excluded']),
                           portfolio_records=len(prepared['portfolio']))
            print(json.dumps(summary, indent=2))
        else:
            generator = SolGenerator(args.cache_dir, args.model, args.timeout)
            print(build(prepared, args.output, generator, args.batch_chars))
        return 0
    except (ValueError, OSError, RuntimeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
