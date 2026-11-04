import unittest
from collections import Counter
from foundation.binding_ablation import cases,diagnose


class BindingAblationTests(unittest.TestCase):
    def test_sixteen_cells_balance_each_factor(self):
        rows=cases();self.assertEqual(len(rows),16)
        self.assertEqual(len({(c['known_object'],c['first_fact_object'],c['unknown_cue_explicit'],c['field_count']) for c in rows}),16)
        self.assertEqual(Counter(c['expected_entity'] for c in rows),{'original':8,'duplicate':8})

    def test_original_prompt_reproduced_exactly(self):
        c=next(c for c in cases() if c['known_object']=='original' and c['first_fact_object']=='original' and not c['unknown_cue_explicit'] and c['field_count']==2)
        self.assertEqual(c['prompt'],'The original register is readable. A duplicate has not been inspected. Return JSON only with unknown_object (original/duplicate) and original_readable (boolean). Do not invent an inspection.')

    def test_second_field_type_not_confused_with_entity(self):
        c=next(c for c in cases() if c['known_object']=='original' and c['field_count']==2)
        d=diagnose('{"unknown_object":"duplicate","original_readable":1}',c)
        self.assertTrue(d['entity_correct']);self.assertFalse(d['format_compliant'])

    def test_valid_schema_can_have_wrong_entity(self):
        c=next(c for c in cases() if c['known_object']=='duplicate' and c['field_count']==2)
        d=diagnose('{"unknown_object":"duplicate","duplicate_readable":true}',c)
        self.assertTrue(d['format_compliant']);self.assertFalse(d['entity_correct'])
