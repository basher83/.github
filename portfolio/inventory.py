"""Validate the repository inventory and generate its offline Markdown overview.

repositories.yaml deliberately uses JSON syntax, a YAML subset, so this tool
needs only Python's standard library. It performs no network requests.
"""
import argparse
import datetime
import json
from pathlib import Path
import re
import sys


PRIVATE_UNKNOWNS = {
    'effective_policy_unknown', 'runtime_unknown', 'private_purpose_and_stack_withheld',
    'private_override_values_withheld', 'alternate_config_paths_not_surveyed',
    'tree_query_failed', 'file_query_failed', 'tool_config_parse_failed',
    'tool_value_withheld', 'config_parse_failed', 'preset_reference_withheld',
    'check_name_withheld', 'workflow_reference_withheld',
    'required_check_name_withheld', 'required_checks_query_failed',
}


def private_boundary(repo):
    """Allow only typed management facts, never arbitrary private source content."""
    def require(condition):
        if not condition:
            raise ValueError(f'{repo["repository"]}: private publication boundary violation')

    def keys(value, allowed):
        require(isinstance(value, dict) and set(value) == set(allowed))

    def safe_name(value):
        return isinstance(value, str) and bool(re.fullmatch(r'[A-Za-z0-9_ /().-]{1,120}', value)) and not re.search(r'(?i)(secret|token|password|https?|\b\d{1,3}(?:\.\d{1,3}){3}\b|[A-Za-z0-9-]+\.[A-Za-z]{2,})', value)

    keys(repo, ('repository', 'visibility', 'observation', 'management', 'required_checks', 'unknowns'))
    keys(repo['visibility'], ('value', 'observed_at', 'evidence'))
    keys(repo['observation'], ('revision', 'observed_at', 'evidence'))
    name = repo['repository']
    revision = repo['observation']['revision']
    require(repo['visibility']['evidence'] == f'https://api.github.com/repos/{name}')
    require(repo['observation']['evidence'] == (f'https://github.com/{name}/tree/{revision}' if revision else f'https://github.com/{name}'))

    def evidence(value, kind):
        prefix = f'https://github.com/{name}/blob/{revision}/'
        require(revision is not None and isinstance(value, str) and value.startswith(prefix))
        path = value[len(prefix):]
        pattern = {'tools': r'\.?mise\.toml', 'preset': r'(?:\.github/)?renovate\.json5?', 'workflow': r'\.github/workflows/[A-Za-z0-9_.-]+\.ya?ml'}[kind]
        require(re.fullmatch(pattern, path))

    keys(repo['management'], ('renovate', 'workflows', 'tools'))
    renovation = repo['management']['renovate']
    keys(renovation, ('state', 'extends', 'has_local_overrides'))
    require(renovation['state'] in ('observed', 'absent', 'unknown'))
    require(type(renovation['has_local_overrides']) is bool or renovation['has_local_overrides'] is None)
    for item in renovation['extends']:
        keys(item, ('reference', 'evidence'))
        require(re.fullmatch(r'(?:local>basher83/renovate-config(?:/{2}presets/[A-Za-z0-9_.-]+\.json)?|(?::[A-Za-z][A-Za-z0-9_-]*|(?:config|schedule|group|helpers|mergeConfidence):[A-Za-z0-9_-]+))', item['reference']))
        evidence(item['evidence'], 'preset')
    workflows = repo['management']['workflows']
    keys(workflows, ('state', 'pr_workflow_declarations', 'shared_workflow_references', 'declared_check_names'))
    require(workflows['state'] in ('observed', 'unknown'))
    require(type(workflows['pr_workflow_declarations']) is bool or workflows['pr_workflow_declarations'] is None)
    require(workflows['state'] != 'unknown' or workflows['pr_workflow_declarations'] is None)
    for item in workflows['shared_workflow_references']:
        keys(item, ('reference', 'evidence'))
        require(re.fullmatch(r'(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/\.github/workflows/[A-Za-z0-9_.-]+\.ya?ml@[A-Za-z0-9_./-]+|\./\.github/workflows/[A-Za-z0-9_.-]+\.ya?ml)', item['reference']))
        evidence(item['evidence'], 'workflow')
    require(all(safe_name(check) for check in workflows['declared_check_names']))
    tools = repo['management']['tools']
    keys(tools, ('state', 'versions'))
    require(tools['state'] in ('observed', 'absent', 'unknown'))
    for item in tools['versions']:
        keys(item, ('tool', 'version', 'evidence'))
        require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{0,60}', item['tool']) and safe_name(item['tool']))
        version = item['version']
        require(isinstance(version, str) and re.fullmatch(r'(?:v?\d+(?:\.(?:\d+|\*)){0,2}(?:[-+][A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*)?|latest|stable|lts(?:/[A-Za-z0-9_-]+)?)', version))
        require(not re.search(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', version))
        evidence(item['evidence'], 'tools')
    checks = repo['required_checks']
    allowed = {'state', 'checks', 'observed_at', 'evidence'}
    if checks['state'] == 'unknown':
        allowed.add('reason')
        require(checks['reason'] == 'query_failed_or_value_withheld')
    keys(checks, allowed)
    require(checks['checks'] is None or all(safe_name(check) for check in checks['checks']))
    require(all(re.fullmatch(r'https://api.github.com/repos/' + re.escape(name) + r'/(?:rules/branches/[A-Za-z0-9_.%+-]+|branches/[A-Za-z0-9_.%+-]+/protection)', value) for value in checks['evidence']))
    require(set(repo['unknowns']) <= PRIVATE_UNKNOWNS)
    if revision is None:
        require('tree_query_failed' in repo['unknowns'])
        require(all(repo['management'][key]['state'] == 'unknown' for key in ('renovate', 'workflows', 'tools')))


def validate(data):
    """Reject unpublished/unverified entries and ambiguous observation states."""
    def require(condition, message):
        if not condition:
            raise ValueError(message)

    def dated(value):
        try:
            return datetime.datetime.fromisoformat(value).tzinfo is not None
        except (ValueError, TypeError):
            return False

    def url(value):
        return isinstance(value, str) and value.startswith(('https://github.com/', 'https://api.github.com/'))

    require(data.get('schema_version') == 2, 'Unsupported schema_version')
    sources = {source['id'] for source in data['sources']}
    require(len(sources) == len(data['sources']), 'Duplicate source IDs')
    for source in data['sources']:
        require(url(source['url']), 'Source must have GitHub evidence')
        datetime.date.fromisoformat(source['observed_date'])
    names = set()
    for repo in data['repositories']:
        name = repo['repository']
        require(re.fullmatch(r'basher83/[A-Za-z0-9_.-]+', name), 'Invalid repository name')
        require(name not in names, 'Duplicate repository')
        names.add(name)
        visibility = repo['visibility']
        require(visibility['value'] in ('public', 'private'), f'{name}: verified visibility required')
        require(dated(visibility['observed_at']) and url(visibility['evidence']), f'{name}: visibility evidence/date required')
        observed = repo['observation']
        require((visibility['value'] == 'private' and observed['revision'] is None) or re.fullmatch(r'[a-f0-9]{40}', observed['revision'] or ''), f'{name}: immutable revision required')
        require(dated(observed['observed_at']) and url(observed['evidence']), f'{name}: observation evidence/date required')
        if visibility['value'] == 'private':
            private_boundary(repo)
        else:
            require(repo['purpose']['source'] in sources, f'{name}: unknown purpose source')
            require(repo['purpose']['basis'] in ('historical_card_description', 'inferred_from_readme_or_name'), f'{name}: explicit purpose qualifier required')
            datetime.date.fromisoformat(repo['purpose']['observed_date'])
            require(isinstance(repo['fork'], bool) and isinstance(repo['lifecycle']['archived'], bool), f'{name}: lifecycle/fork flags required')
            ci = repo['ci']
            require(ci['state'] in ('observed', 'unknown'), f'{name}: invalid CI state')
            require(ci['state'] != 'unknown' or ci['pr_workflow_declarations'] is None, f'{name}: unknown CI cannot assert PR coverage')
            require(ci['pr_workflow_declarations'] in (True, False, None), f'{name}: invalid PR declaration')
            for workflow in ci['workflows']:
                require(url(workflow['evidence']) and observed['revision'] in workflow['evidence'], f'{name}: workflow evidence must be pinned')
        required = repo['required_checks']
        require(required['state'] in ('observed', 'unknown'), f'{name}: invalid required-check state')
        require(bool(required['evidence']) and all(url(e) for e in required['evidence']), f'{name}: required-check evidence missing')
        if required['state'] == 'unknown':
            require(required['checks'] is None and bool(required.get('reason')), f'{name}: unknown checks need null plus reason')
        else:
            require(isinstance(required['checks'], list), f'{name}: observed checks need a list (empty means none)')
        if visibility['value'] == 'public':
            require(repo['renovate']['state'] in ('observed', 'absent', 'unknown'), f'{name}: invalid Renovate state')
        require(isinstance(repo['unknowns'], list), f'{name}: explicit unknowns required')
    scope = data['scope']
    require(scope['public_count'] == sum(r['visibility']['value'] == 'public' for r in data['repositories']), 'Public count mismatch')
    require(scope['private_count'] == sum(r['visibility']['value'] == 'private' for r in data['repositories']), 'Private count mismatch')
    require(scope['included_count'] == len(names), 'Included count mismatch')
    require(scope['historical_card_count'] == scope['included_count'] + scope['excluded_count'], 'Scope counts do not reconcile')
    for entry in data['proposals'] + data['historical_observations']:
        require(entry['repository'] in names, 'Proposal/history references an excluded repository')
        require(entry['repository'] in {r['repository'] for r in data['repositories'] if r['visibility']['value'] == 'public'}, 'Private free-text proposals/history are outside publication boundary')
    return data


def cell(value):
    return str(value).replace('|', r'\|').replace('\n', ' ')


def required_label(repo):
    checks = repo['required_checks']
    if checks['state'] == 'unknown':
        return 'unknown'
    return ', '.join(checks['checks']) or 'none'


def render(data):
    """Render stable ordering with no clock, network or runtime assumptions."""
    all_repos = sorted(data['repositories'], key=lambda r: r['repository'].casefold())
    repos = [r for r in all_repos if r['visibility']['value'] == 'public']
    private_repos = [r for r in all_repos if r['visibility']['value'] == 'private']
    scope = data['scope']
    visibility_dates = sorted({r["visibility"]["observed_at"][:10] for r in all_repos})
    visibility_period = " to ".join(dict.fromkeys([visibility_dates[0], visibility_dates[-1]]))
    lines = [
        '<!-- Generated by portfolio/inventory.py; edit repositories.yaml, then regenerate. -->',
        '# Repository management inventory', '',
        'Canonical data: [repositories.yaml](repositories.yaml). This YAML file uses JSON syntax to keep generation dependency-free.', '',
        f'The 2026-10-06 card contained {scope["historical_card_count"]} entries. Visibility was checked on {visibility_period}; {scope["included_count"]} entries are included ({scope["public_count"]} public, {scope["private_count"]} private), with {scope["excluded_count"]} excluded. The initial public-only restriction was superseded by the operator-approved publication boundary below.', '',
        '## Publication boundary', '',
        'Private repository identity and shared-management facts are approved for publication: tool versions, direct preset/workflow references, declared/required check names and configured adoption. Private application code, internal architecture, infrastructure addresses, secrets, private registry addresses and unrelated content are excluded. No whole private manifests, workflow bodies or logs are copied. Ambiguous values are withheld for the operator’s decision.', '',
        'Private records use a strict nested allowlist. They contain no purpose/stack descriptions, arbitrary override values, commands, environment, workflow filters or job bodies. Evidence is restricted to the repository and known management files at the observed revision. Unknown categories are controlled codes rather than free text; private records cannot use the free-text proposal/history sections. Public records retain their existing historical descriptions and configuration detail.', '',
        'This boundary follows the operator’s 2026-10-09 approval after the two PR comments. The original public-only inventory is preserved in Git history; source survey dates and historical receipts below are unchanged.', '',
        'Purpose descriptions retain the card’s original date. “Inferred” means summarized from README/name rather than a GitHub description. Primary language is current GitHub metadata, not a complete stack survey. Unarchived does not establish active development.', '',
        'CI below means workflow declarations at the recorded revision. Public records retain PR triggers, branch/path filters and job conditions; private records retain only whether PR triggers are declared. These declarations do not prove that every PR gets functional checks. Required checks come from separate default-branch effective-rule and classic-protection queries. Empty checks mean observed none; null means unknown. App checks and hosted runtime results are not inventoried.', '',
        'Renovate fields record direct presets and local configuration only. Inherited preset resolution, organization defaults and actual bot behavior remain unknown. Shared references include local calls and calls to basher83/.github; other public reusable calls remain visible in workflow jobs. Private records publish only preset/workflow references and the presence of local overrides, not their contents.', '',
        '## Coverage and limits', '',
        '| Field | Populated | Unknown / limit |',
        '| --- | ---: | --- |',
        f'| Public purpose, archive/fork flags, revision/date | {len(repos)} | Frameworks and development stage unknown for all |',
        f'| Repository identity / visibility | {len(all_repos)} | {len(private_repos)} private entries publish bounded management facts only |',
        f'| Private workflow/config survey | {sum(r["management"]["workflows"]["state"] == "observed" for r in private_repos)} | {sum(r["management"]["workflows"]["state"] == "unknown" for r in private_repos)} unknown |',
        f'| Private direct Renovate config | {sum(r["management"]["renovate"]["state"] == "observed" for r in private_repos)} present | {sum(r["management"]["renovate"]["state"] == "absent" for r in private_repos)} absent; {sum(r["management"]["renovate"]["state"] == "unknown" for r in private_repos)} unknown |',
        f'| Private tool versions | {sum(bool(r["management"]["tools"]["versions"]) for r in private_repos)} repositories | Values outside safe version syntax are withheld; alternate tool manifests not surveyed |',
        f'| Public primary language | {sum(r["stack"]["primary_language"] is not None for r in repos)} | {sum(r["stack"]["primary_language"] is None for r in repos)} unknown |',
        f'| Public workflow declarations | {sum(r["ci"]["state"] == "observed" for r in repos)} | {sum(r["ci"]["state"] == "unknown" for r in repos)} unknown; {sum(r["ci"]["pr_workflow_declarations"] is True for r in repos)} declare PR triggers |',
        f'| Public direct Renovate config | {sum(bool(r["renovate"]["configs"]) for r in repos)} present | {sum(r["renovate"]["state"] == "absent" for r in repos)} absent in searched paths; {sum(r["renovate"]["state"] == "unknown" for r in repos)} unknown; effective policy unknown for all |',
        f'| Required status checks | {sum(r["required_checks"]["state"] == "observed" for r in all_repos)} | {sum(r["required_checks"]["state"] == "unknown" for r in all_repos)} unknown; {sum(bool(r["required_checks"]["checks"]) for r in all_repos)} have required checks |',
        f'| Runtime results / approved adoption exceptions | 0 | {len(all_repos)} unknown |', '',
        '## Public repositories', '',
        '| Repository | Lifecycle / fork | Primary language | Purpose (2026-10-06) | PR workflow declared | Required checks |',
        '| --- | --- | --- | --- | --- | --- |',
    ]
    for repo in repos:
        name = repo['repository']
        lifecycle = 'archived' if repo['lifecycle']['archived'] else 'unarchived'
        if repo['fork']:
            lifecycle += ', fork'
        purpose = repo['purpose']['text']
        if repo['purpose']['basis'] == 'inferred_from_readme_or_name':
            purpose += ' (inferred)'
        pr = {True: 'yes (declaration)', False: 'no', None: 'unknown'}[repo['ci']['pr_workflow_declarations']]
        values = [f'[{name.split("/", 1)[1]}](https://github.com/{name})', lifecycle, repo['stack']['primary_language'] or 'unknown', purpose, pr, required_label(repo)]
        lines.append('| ' + ' | '.join(cell(value) for value in values) + ' |')
    lines += ['', '## Configuration evidence', '', 'Dates and revisions below apply to file observations. Check requirements are mutable settings observed at that date, not properties of the Git revision.', '']
    for repo in repos:
        observed = repo['observation']
        lines += [f'### {repo["repository"]}', '', f'Observed {observed["observed_at"]}; [revision {observed["revision"][:12]}]({observed["evidence"]}). [Visibility API]({repo["visibility"]["evidence"]}).', '']
        configs = repo['renovate']['configs']
        if configs:
            for config in configs:
                presets = ', '.join(f'`{x}`' for x in config['extends']) or 'none'
                overrides = ', '.join(f'`{x}`' for x in sorted(config['local_overrides'])) or 'none'
                lines += [f'- Renovate [{config["path"]}]({config["evidence"]}): direct presets {presets}; local override fields {overrides}. Full values are in canonical data.']
        else:
            lines += [f'- Renovate: {repo["renovate"]["state"]} in searched config paths.']
        workflows = repo['ci']['workflows']
        if workflows:
            for workflow in workflows:
                triggers = ', '.join(f'`{event}`' for event in sorted(workflow['triggers'])) or 'none'
                lines.append(f'- Workflow [{workflow["path"]}]({workflow["evidence"]}): {triggers}. Filters and job conditions are in canonical data.')
        else:
            lines.append('- Workflows: unknown; file survey failed.' if repo['ci']['state'] == 'unknown' else '- Workflows: none in the observed default-branch workflow directory.')
        for ref in repo['ci']['shared_workflow_references']:
            lines.append(f'- Shared call ({ref["scope"]}): `{ref["reference"]}` from [{ref["caller"]}, job {ref["job"]}]({ref["evidence"]}).')
        if not repo['ci']['shared_workflow_references']:
            lines.append('- Central/local shared workflow calls: unknown; file survey failed.' if repo['ci']['state'] == 'unknown' else '- Central/local shared workflow calls: none observed in workflow jobs.')
        lint = repo['ci']['actionlint_references']
        lines.append('- actionlint references (scoped scan): ' + (', '.join(f'[{x["path"]}]({x["evidence"]})' for x in lint) if lint else ('unknown; file survey failed' if repo['ci']['state'] == 'unknown' else 'none observed')) + '.')
        lines.append(f'- Required checks: {required_label(repo)}. ' + ' '.join(f'[API evidence {i + 1}]({url})' for i, url in enumerate(repo['required_checks']['evidence'])) + '.')
        lines.append('')
    lines += ['', '## Private repositories: bounded management facts', '',
        'Purpose, language/stack, internal paths, filters and override contents are withheld. Check names below are declarations or separately observed required settings, not runtime passes. Private evidence links require repository access.', '',
        '| Repository | Renovate config / central preset | PR workflow declared | Central fast gate configured | Required checks |',
        '| --- | --- | --- | --- | --- |',
    ]
    for repo in private_repos:
        management = repo['management']
        presets = management['renovate']
        workflows = management['workflows']
        central = any(item['reference'].startswith('local>basher83/renovate-config') for item in presets['extends'])
        gate = any(item['reference'].startswith('basher83/.github/.github/workflows/python-mise-fast-pr-gate.yml@') for item in workflows['shared_workflow_references'])
        pr = {True: 'yes (declaration)', False: 'no', None: 'unknown'}[workflows['pr_workflow_declarations']]
        gate_label = 'yes (configured)' if gate else ('unknown' if workflows['state'] == 'unknown' else 'none observed')
        preset_label = presets['state'] + (' / central' if central else '')
        values = [f'[{repo["repository"].split("/", 1)[1]}](https://github.com/{repo["repository"]})', preset_label, pr, gate_label, required_label(repo)]
        lines.append('| ' + ' | '.join(cell(value) for value in values) + ' |')
    for repo in private_repos:
        observed = repo['observation']
        revision = observed['revision'][:12] if observed['revision'] else 'unknown'
        management = repo['management']
        lines += ['', f'### {repo["repository"]} (private)', '',
            f'Observed {observed["observed_at"]}; [revision {revision}]({observed["evidence"]}). [Visibility API]({repo["visibility"]["evidence"]}).', '',
        ]
        presets = management['renovate']
        lines.append(f'- Renovate: {presets["state"]}; local overrides present: {presets["has_local_overrides"]}. Override contents withheld.')
        for item in presets['extends']:
            lines.append(f'- Direct preset: `{item["reference"]}`. [Evidence]({item["evidence"]}).')
        workflows = management['workflows']
        lines.append(f'- Workflow survey: {workflows["state"]}; PR declaration: {workflows["pr_workflow_declarations"]}.')
        for item in workflows['shared_workflow_references']:
            lines.append(f'- Shared workflow configured: `{item["reference"]}`. [Evidence]({item["evidence"]}).')
        declared = ', '.join(f'`{cell(name)}`' for name in workflows['declared_check_names']) or ('unknown' if workflows['state'] == 'unknown' else 'none observed')
        lines.append(f'- Declared check names: {declared}. Job IDs/names only; matrix-expanded/reusable check names are not resolved.')
        tools = management['tools']
        lines.append(f'- Tool version survey: {tools["state"]}.')
        for item in tools['versions']:
            lines.append(f'- Tool `{item["tool"]}`: `{item["version"]}`. [Evidence]({item["evidence"]}).')
        lines.append(f'- Required checks: {required_label(repo)}. ' + ' '.join(f'[API evidence {i + 1}]({url})' for i, url in enumerate(repo['required_checks']['evidence'])) + '.')
        lines.append('- Unknown/withheld categories: ' + ', '.join(f'`{code}`' for code in repo['unknowns']) + '.')
    lines.append('')
    lines += ['## Historical observations', '']
    source_urls = {source['id']: source['url'] for source in data['sources']}
    for history in data['historical_observations']:
        lines.append(f'- {history["observed_date"]}, {history["repository"]}: {history["fact"]} {history.get("superseded_by", history.get("limits", ""))} [Historical source]({source_urls[history["source"]]}).')
    lines += ['', '## Proposals awaiting a separate decision', '', 'These are review candidates, not observed adoption, approved exceptions or authorization to migrate. CI duplication/equivalence with the central gate has not been evaluated. Approved exceptions remain unknown.', '']
    for proposal in data['proposals']:
        lines.append(f'- **{proposal["repository"]} ({proposal["type"]}):** {proposal["proposal"]} Basis: {proposal["basis"]} [Evidence]({proposal["evidence"]}).')
    lines += ['', '## Maintain this inventory', '',
        'Edit only `portfolio/repositories.yaml` for facts and proposals. Preserve historical dates and inference qualifiers; refresh visibility before publishing and apply the strict private-record boundary to repositories that become private. Never preserve unrestricted public-record fields after a visibility change. Add an immutable revision, observation date and evidence for new file facts; use null plus a reason when a query is blocked. Do not convert a missing config into a claim about bot installation or a CI declaration into a runtime pass.', '',
        'The initial survey searched default-branch `.github/workflows/*.{yml,yaml}`, root and `.github` `renovate.json/json5`, and root `mise.toml`, `.mise.toml`, `.pre-commit-config.yaml`, `hk.pkl` for actionlint references. Successful recursive-tree responses were checked for truncation; failed scans remain unknown. Refresh is manual; there is no recurring scanner.', '',
        'Run `python3 portfolio/inventory.py` to regenerate, `python3 portfolio/inventory.py --check` to validate freshness, and `python3 -m unittest discover -s portfolio -p "test_*.py"` for the publication and generation tests. `mise run ci` includes these checks alongside existing workflow linting.', '',
        'Validation guards the recorded visibility, provenance and generated output. It is offline and cannot establish current repository visibility today; a fresh API visibility and publication-boundary review is still needed before publication. Private extraction examines management files in memory and stores only allowlisted facts; no source bodies are retained in this repository. `mise.toml`/`.mise.toml` are the tool-version survey scope. Null revision means a commit could not be observed. Private check names and required settings may be unknown if requests fail or values are withheld.', '',
        '## Sources', '',
    ]
    for source in data['sources']:
        lines.append(f'- [{source["id"]}]({source["url"]}), source observation date {source["observed_date"]}. {source.get("note", "")}'.rstrip())
    return '\n'.join(lines).rstrip() + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        data = validate(json.loads((args.directory / 'repositories.yaml').read_text()))
        overview = render(data)
        path = args.directory / 'README.md'
        if args.check:
            if not path.exists() or path.read_text() != overview:
                raise ValueError('Generated overview is stale; run python3 portfolio/inventory.py')
        else:
            path.write_text(overview)
        print(f'Validated {len(data["repositories"])} repositories under publication boundary; overview {"current" if args.check else "generated"}.')
        return 0
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
