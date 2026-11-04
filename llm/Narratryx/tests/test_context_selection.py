"""Original diagnostic fixtures; never added to a training corpus."""
import unittest
from foundation.context_selection import ContextEntry, Fact, select_context


class ContextSelectionTests(unittest.TestCase):
    def entry(self, ident='mara', **kwargs):
        return ContextEntry(id=ident, project_id='a', name=ident.title(), facts=(Fact('ability', 'Cannot swim.'),), **kwargs)

    def test_visibility_project_archive_and_status_filter_before_ranking(self):
        entries = [self.entry(), self.entry('hidden', visible=False), self.entry('draft', status='draft'),
                   self.entry('archive', archived=True), ContextEntry('other', 'b', 'Other secret', (Fact('secret', 'OTHER SECRET'),))]
        result = select_context(entries, 'a', 'Hidden draft archive other secret')
        self.assertEqual(result['selected_ids'], ['mara'])
        self.assertNotIn('secret', result['text'].casefold())

    def test_field_visibility_and_hidden_links(self):
        entry = ContextEntry('mara', 'a', 'Mara', (Fact('ability', 'Cannot swim.'), Fact('motive', 'MURDER SECRET', visible=False)), linked_ids=('hidden',))
        text = select_context([entry, self.entry('hidden', visible=False)], 'a', 'murder motive')['text']
        for secret in ['MURDER', 'motive', 'hidden']:
            self.assertNotIn(secret, text)

    def test_explicit_state_excludes_incompatible_and_unknown_traits(self):
        entry = ContextEntry('mara', 'a', 'Mara', (Fact('clothes', 'Pleated khakis.', when={'form': 'human'}), Fact('wolf', 'Grey fur.', when={'form': 'wolf'}), Fact('ability', 'Cannot swim.')))
        wolf = select_context([entry], 'a', 'Mara clothes', {'form': 'wolf'})['text']
        self.assertIn('Grey fur', wolf)
        self.assertNotIn('khakis', wolf)
        unknown = select_context([entry], 'a', 'Mara')['text']
        self.assertNotIn('khakis', unknown)
        self.assertNotIn('Grey fur', unknown)
        self.assertIn('Cannot swim.', unknown)

    def test_alias_matching_respects_word_boundaries(self):
        entries = [ContextEntry('z', 'a', 'Mara', (Fact('ability', 'Cannot swim.'),), aliases=('Captain Venn',)), self.entry('a')]
        self.assertEqual(select_context(entries, 'a', 'Captain Venn arrives')['selected_ids'][0], 'z')
        self.assertEqual(select_context(entries, 'a', 'marathon')['selected_ids'][0], 'a')

    def test_whole_entry_budget_omissions_and_small_budget(self):
        huge = ContextEntry('huge', 'a', 'Huge', (Fact('text', 'x' * 6000),))
        result = select_context([huge, self.entry()], 'a', 'Huge', max_characters=500)
        self.assertLessEqual(len(result['text']), 500)
        self.assertIn('Cannot swim.', result['text'])
        self.assertIn('omitted for space', result['text'])
        self.assertEqual(result['selected_ids'], ['mara'])
        self.assertFalse(result['tokenizer_budget_verified'])
        self.assertEqual(select_context([self.entry()], 'a', '', max_characters=1)['text'], '')

    def test_read_only_data_and_selected_links(self):
        entry = self.entry(linked_ids=('dock', 'hidden'))
        before = repr(entry)
        text = select_context([entry, self.entry('dock')], 'a', 'Mara')['text']
        self.assertIn('"links":["dock"]', text)
        self.assertEqual(repr(entry), before)

    def test_duplicate_ids_and_negative_budget_rejected(self):
        with self.assertRaises(ValueError):
            select_context([self.entry(), self.entry()], 'a', '')
        with self.assertRaises(ValueError):
            select_context([], 'a', '', max_characters=-1)
