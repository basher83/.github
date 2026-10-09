"""Tests for the publication guard and deterministic overview."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import inventory


def private_sample():
    data = sample()
    original = data['repositories'][0]
    repo = {key: copy.deepcopy(original[key]) for key in ('repository', 'visibility', 'observation', 'required_checks')}
    repo['visibility']['value'] = 'private'
    repo['management'] = {
        'renovate': {'state': 'observed', 'extends': [{'reference': 'local>basher83/renovate-config', 'evidence': 'https://github.com/basher83/example/blob/' + 'a' * 40 + '/renovate.json'}], 'has_local_overrides': True},
        'workflows': {'state': 'observed', 'pr_workflow_declarations': True, 'shared_workflow_references': [{'reference': 'basher83/.github/.github/workflows/python-mise-fast-pr-gate.yml@main', 'evidence': 'https://github.com/basher83/example/blob/' + 'a' * 40 + '/.github/workflows/ci.yml'}], 'declared_check_names': ['lint']},
        'tools': {'state': 'observed', 'versions': [{'tool': 'python', 'version': '3.13.16', 'evidence': 'https://github.com/basher83/example/blob/' + 'a' * 40 + '/mise.toml'}]},
    }
    repo['required_checks']['reason'] = 'query_failed_or_value_withheld'
    repo['required_checks']['observed_at'] = original['visibility']['observed_at']
    repo['unknowns'] = ['runtime_unknown']
    data['repositories'] = [repo]
    data['scope'].update(public_count=0, private_count=1)
    return data


def sample():
    return {
        'schema_version': 2,
        'scope': {'historical_card_count': 92, 'public_count': 1, 'private_count': 0, 'included_count': 1, 'excluded_count': 91},
        'sources': [{'id': 'card', 'url': 'https://github.com/example/repo', 'observed_date': '2026-10-06'}],
        'repositories': [{
            'repository': 'basher83/example',
            'visibility': {'value': 'public', 'observed_at': '2026-10-09T20:00:00+00:00', 'evidence': 'https://api.github.com/repos/basher83/example'},
            'observation': {'revision': 'a' * 40, 'observed_at': '2026-10-09T20:00:00+00:00', 'evidence': 'https://github.com/basher83/example/tree/' + 'a' * 40},
            'purpose': {'text': 'Example | purpose', 'basis': 'inferred_from_readme_or_name', 'observed_date': '2026-10-06', 'source': 'card'},
            'stack': {'primary_language': None, 'frameworks': None},
            'lifecycle': {'archived': False, 'development_status': None},
            'fork': False,
            'renovate': {'state': 'absent', 'configs': []},
            'ci': {'state': 'observed', 'workflows': [], 'pr_workflow_declarations': False, 'shared_workflow_references': [], 'actionlint_references': [], 'runtime_result': None},
            'required_checks': {'state': 'unknown', 'checks': None, 'evidence': ['https://api.github.com/repos/basher83/example/rules/branches/main'], 'reason': 'permission denied'},
            'unknowns': ['frameworks'],
        }],
        'proposals': [],
        'historical_observations': [],
    }


class InventoryTests(unittest.TestCase):
    def test_rejects_unverified_visibility(self):
        for value in (None, 'unknown'):
            data = sample()
            data['repositories'][0]['visibility']['value'] = value
            with self.assertRaises(ValueError):
                inventory.validate(data)

    def test_accepts_bounded_private_management_metadata(self):
        data = private_sample()
        inventory.validate(data)
        rendered = inventory.render(data)
        self.assertIn('private', rendered)
        self.assertIn('3.13.16', rendered)
        self.assertIn('python-mise-fast-pr-gate.yml@main', rendered)
        self.assertIn('publication boundary', rendered.lower())

    def test_rejects_private_source_bodies_and_unrelated_content(self):
        for key in ('purpose', 'stack', 'application_code', 'architecture', 'logs'):
            data = private_sample()
            data['repositories'][0][key] = 'unrelated private material'
            with self.assertRaises(ValueError):
                inventory.validate(data)
        for key in ('run', 'env', 'workflow_body', 'local_overrides', 'registry_url'):
            data = private_sample()
            data['repositories'][0]['management']['workflows'][key] = 'private material'
            with self.assertRaises(ValueError):
                inventory.validate(data)

    def test_rejects_addresses_secrets_and_ambiguous_tool_values(self):
        for version in ('https://registry.internal/tool', '10.0.0.1', '${TOKEN}', 'ghp_123secret', '/private/path', 'git@host:tool', '1.0.ghp_sensitive', 'lts/registry.private.company'):
            data = private_sample()
            data['repositories'][0]['management']['tools']['versions'][0]['version'] = version
            with self.assertRaises(ValueError):
                inventory.validate(data)
        data = private_sample()
        data['repositories'][0]['unknowns'] = ['the password is secret']
        with self.assertRaises(ValueError):
            inventory.validate(data)

    def test_rejects_private_registry_preset_and_address_check_name(self):
        data = private_sample()
        data['repositories'][0]['management']['renovate']['extends'][0]['reference'] = 'registry.private.company'
        with self.assertRaises(ValueError):
            inventory.validate(data)
        data = private_sample()
        data['repositories'][0]['management']['workflows']['declared_check_names'] = ['registry.private.company']
        with self.assertRaises(ValueError):
            inventory.validate(data)

    def test_private_free_text_cannot_bypass_boundary_via_history_or_proposals(self):
        for section in ('historical_observations', 'proposals'):
            data = private_sample()
            data[section] = [{'repository': 'basher83/example', 'fact': 'private source body'}]
            with self.assertRaises(ValueError):
                inventory.validate(data)

    def test_private_tool_name_cannot_be_registry_address(self):
        data = private_sample()
        data['repositories'][0]['management']['tools']['versions'][0]['tool'] = 'registry.private.company'
        with self.assertRaises(ValueError):
            inventory.validate(data)

    def test_private_evidence_must_be_pinned_management_file(self):
        for path in ('src/application.py', 'manifests/prod.yml', 'mise.toml?secret=xyz'):
            data = private_sample()
            data['repositories'][0]['management']['tools']['versions'][0]['evidence'] = 'https://github.com/basher83/example/blob/' + 'a' * 40 + '/' + path
            with self.assertRaises(ValueError):
                inventory.validate(data)

    def test_requires_visibility_date_and_immutable_revision(self):
        for field, key in [('visibility', 'observed_at'), ('observation', 'revision')]:
            data = sample()
            data['repositories'][0][field][key] = ''
            with self.assertRaises(ValueError):
                inventory.validate(data)

    def test_rejects_duplicate_repositories_and_unknown_source(self):
        data = sample()
        data['repositories'].append(copy.deepcopy(data['repositories'][0]))
        with self.assertRaises(ValueError):
            inventory.validate(data)
        data = sample()
        data['repositories'][0]['purpose']['source'] = 'missing'
        with self.assertRaises(ValueError):
            inventory.validate(data)

    def test_unknown_checks_are_not_rendered_as_none(self):
        rendered = inventory.render(sample())
        self.assertIn('unknown', rendered)
        self.assertNotIn('| none |', rendered)
        data = sample()
        data['repositories'][0]['required_checks'] = {'state': 'observed', 'checks': [], 'evidence': ['https://api.github.com/repos/basher83/example']}
        self.assertIn('| none |', inventory.render(data))

    def test_overview_is_deterministic_and_escapes_table_cells(self):
        data = sample()
        data['repositories'].append(copy.deepcopy(data['repositories'][0]))
        data['repositories'][1]['repository'] = 'basher83/another'
        self.assertEqual(inventory.render(data), inventory.render({**data, 'repositories': list(reversed(data['repositories']))}))
        self.assertIn('Example \\| purpose', inventory.render(data))
        self.assertIn('inferred', inventory.render(data))
        self.assertIn('2026-10-06', inventory.render(data))

    def test_failed_scan_remains_unknown_in_overview(self):
        data = sample()
        repo = data['repositories'][0]
        repo['ci']['state'] = 'unknown'
        repo['ci']['pr_workflow_declarations'] = None
        repo['renovate']['state'] = 'unknown'
        rendered = inventory.render(data)
        self.assertIn('Workflows: unknown', rendered)
        self.assertIn('shared workflow calls: unknown', rendered)
        self.assertIn('actionlint references (scoped scan): unknown', rendered)
        self.assertNotIn('none in the observed default-branch workflow directory', rendered)

    def test_unknown_ci_cannot_claim_no_pr_workflows(self):
        data = sample()
        data['repositories'][0]['ci']['state'] = 'unknown'
        with self.assertRaises(ValueError):
            inventory.validate(data)

    def test_check_detects_stale_generated_overview(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'repositories.yaml').write_text(json.dumps(sample()))
            (root / 'README.md').write_text('stale')
            result = subprocess.run([sys.executable, inventory.__file__, '--directory', str(root), '--check'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('stale', result.stderr)
            subprocess.run([sys.executable, inventory.__file__, '--directory', str(root)], check=True, capture_output=True)
            subprocess.run([sys.executable, inventory.__file__, '--directory', str(root), '--check'], check=True, capture_output=True)


if __name__ == '__main__':
    unittest.main()
