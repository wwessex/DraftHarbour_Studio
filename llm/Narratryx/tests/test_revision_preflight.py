"""Fixed membership, untruncated supervision and new diagnostic boundaries."""
import copy
import importlib.util
from pathlib import Path
import sys
import unittest

from foundation.validation import Invalid

HERE = Path(__file__).resolve().parents[1] / 'curation/revision-preflight-v1'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


BUILD = module('revision_build', 'build.py')
previous = sys.modules.get('build')
sys.modules['build'] = BUILD
try:
    PREFLIGHT = module('revision_token_preflight', 'preflight.py')
finally:
    if previous is None:
        sys.modules.pop('build', None)
    else:
        sys.modules['build'] = previous
CASES = module('revision_cases', 'evaluation_cases.py')


class Tokenizer:
    eos_token_id = 0

    def apply_chat_template(self, messages, **kwargs):
        return messages[0]['content'] + '|assistant|'

    def encode(self, text, **kwargs):
        return [ord(c) for c in text]

    def decode(self, ids, **kwargs):
        return ''.join(chr(c) for c in ids)


class RevisionPreflightTests(unittest.TestCase):
    def test_round_robin_work_selection_preserves_inputs(self):
        rows = [dict(id='a1', source_work_ids=['a']), dict(id='a2', source_work_ids=['a']),
                dict(id='b1', source_work_ids=['b']), dict(id='b2', source_work_ids=['b'])]
        before = copy.deepcopy(rows)
        chosen = BUILD.balanced_subset(rows, 3)
        self.assertEqual([r['id'] for r in chosen], ['a1', 'b1', 'a2'])
        self.assertEqual(rows, before)

    def test_missing_quota_fails_instead_of_repeating_examples(self):
        with self.assertRaises(Invalid):
            BUILD.balanced_subset([dict(id='a', source_work_ids=['a'])], 2)

    def test_only_answer_and_eos_are_supervised(self):
        encoded, prompt, answer = PREFLIGHT.encode_example(Tokenizer(),
            [dict(role='user', content='instruction'), dict(role='assistant', content='prose')])
        self.assertEqual(encoded['labels'][:prompt], [-100]*prompt)
        self.assertEqual(encoded['labels'][prompt:], [ord(c) for c in 'prose']+[0])
        self.assertEqual(answer, 6)
        self.assertEqual(len(encoded['input_ids']), prompt+answer)

    def test_oversize_answer_is_rejected_without_truncation(self):
        with self.assertRaisesRegex(Invalid, 'exceeds'):
            PREFLIGHT.encode_example(Tokenizer(),
                [dict(role='user', content='instruction'), dict(role='assistant', content='prose')], limit=10)

    def test_nonroundtripping_tokenizer_is_rejected(self):
        class Broken(Tokenizer):
            def decode(self, ids, **kwargs):
                return 'changed prose'
        with self.assertRaisesRegex(Invalid, 'round-trip'):
            PREFLIGHT.encode_example(Broken(), [dict(role='user', content='x'), dict(role='assistant', content='source')])

    def test_missing_eos_fails_closed(self):
        tokenizer = Tokenizer()
        tokenizer.eos_token_id = None
        with self.assertRaisesRegex(Invalid, 'EOS'):
            PREFLIGHT.encode_example(tokenizer, [dict(role='user', content='x'), dict(role='assistant', content='source')])

    def test_diagnostic_has_twentyfour_unique_cases_and_eight_scenarios(self):
        cases = CASES.cases()
        self.assertEqual(len(cases), 24)
        self.assertEqual(len({c['id'] for c in cases}), 24)
        self.assertEqual(len({c['scenario_id'] for c in cases}), 8)
        self.assertTrue(all('evaluation only' in c['provenance'] for c in cases))

    def test_editing_has_no_minimum_and_future_arrivals_remain_explicit(self):
        cases = CASES.cases()
        self.assertTrue(all(c['word_count_min'] is None for c in cases if c['task']=='editing'))
        timed = [c for c in cases if c['kind']=='chronology-rewrite']
        self.assertEqual(len(timed), 4)
        self.assertTrue(all('has not arrived' in c['context'] and 'unknown' in c['context'] for c in timed))


if __name__ == '__main__':
    unittest.main()
