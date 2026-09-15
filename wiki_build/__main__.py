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
    inventory_parser = commands.add_parser('inventory', help='inventory all collected material without model calls')
    inventory_parser.add_argument('investor_dir', type=Path)
    inventory_parser.add_argument('--output', type=Path)
    full = commands.add_parser('full-build', help='review every collected source and build a complete memory')
    full.add_argument('investor_dir', type=Path)
    full.add_argument('--output', type=Path, required=True)
    full.add_argument('--cache-dir', type=Path, default=Path('.wiki-cache/full-review'))
    full.add_argument('--model', default=MODEL)
    full.add_argument('--timeout', type=int, default=1200)
    full.add_argument('--workers', type=int, default=3)
    full.add_argument('--reviews', type=Path, help='revalidate and reuse prior source reviews')
    full.add_argument('--inventory', type=Path, help='reuse a previously saved inventory snapshot')
    full.add_argument('--identity-resolutions', type=Path, help='source-backed account/speaker identity resolutions')
    full.add_argument('--supplements', type=Path, help='additional recovered transcript sources')
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
        if args.command in ('build', 'full-build'):
            cache = args.cache_dir.resolve()
            if cache == source or source in cache.parents:
                raise ValueError('Cache must be outside the input directory')
            if cache == dest or dest in cache.parents:
                raise ValueError('Cache must be outside the output directory')
            if args.timeout <= 0:
                raise ValueError('Timeout must be positive')
        if args.command in ('inventory', 'full-build'):
            from .inventory import inventory, apply_supplements, apply_resolutions
            from .full_review import review_all
            from .full_build import full_build
            from .render import write_json
            snapshot = getattr(args, 'inventory', None)
            inv = json.loads(snapshot.read_text()) if snapshot else inventory(args.investor_dir)
            if inv['vc_slug'] != args.investor_dir.name:
                raise ValueError('Inventory investor mismatch')
            supplemental = getattr(args, 'supplements', None)
            if supplemental: inv = apply_supplements(inv, supplemental)
            if getattr(args,'identity_resolutions',None): inv = apply_resolutions(inv,args.identity_resolutions,args.investor_dir)
            if args.command == 'inventory':
                if args.output:
                    args.output.parent.mkdir(parents=True, exist_ok=True); write_json(args.output, inv)
                print(json.dumps({'files':len(inv['files']), 'sources':len(inv['sources']), 'characters':sum(len(s['text']) for s in inv['sources']), 'warnings':inv['warnings']}, indent=2))
                return 0
            if not 1 <= args.workers <= 8: raise ValueError('Workers must be between 1 and 8')
            generator = SolGenerator(args.cache_dir, args.model, args.timeout)
            write_json(args.cache_dir / 'inventory.json', inv)
            prior=json.loads(args.reviews.read_text()) if args.reviews else []
            if isinstance(prior,dict): prior=prior['reviews']
            reviews = review_all(inv, generator, args.workers, existing_reviews=prior)
            write_json(args.cache_dir / 'reviews.json', reviews)
            print(full_build(inv, reviews, args.output, generator))
            return 0
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
