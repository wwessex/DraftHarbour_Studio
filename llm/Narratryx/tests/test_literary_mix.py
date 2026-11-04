"""Derivation safeguards: these invented fixture strings never become training inputs."""
import importlib.util
from pathlib import Path
import unittest

module_path=Path(__file__).resolve().parents[1]/'curation/literary-mix-v1/build.py'
spec=importlib.util.spec_from_file_location('literary_mix_builder',module_path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class LiteraryMixTests(unittest.TestCase):
    def test_all_derived_targets_are_exact_slices_and_context_excludes_target(self):
        text='Mara waited by the quiet quay. She put the rope beside the boat and watched the tide. "I will wait here until the last of the boats has gone," she said. The lantern went out.'
        tasks=list(module.derived_tasks(text))
        self.assertEqual({row[0] for row in tasks},{'continuation','dialogue'})
        for kind,task,prompt,start,end in tasks:
            self.assertGreater(end,start)
            self.assertEqual(text[start:end],text[start:end].strip())
            self.assertNotIn(text[start:end],prompt)
            self.assertIn(text[:start].rstrip(),prompt)
        dialogue=next(row for row in tasks if row[0]=='dialogue')
        self.assertTrue(text[dialogue[3]:dialogue[4]].startswith('"'))
        self.assertTrue(text[dialogue[3]:dialogue[4]].endswith('"'))
    def test_never_invents_a_dialogue_target_without_a_complete_quote(self):
        text=' '.join(['Quietly']*30)+'. An unfinished "spoken phrase.'
        self.assertEqual([row[0] for row in module.derived_tasks(text)],['continuation'])
    def test_rejects_dialogue_without_preceding_context_or_with_too_few_words(self):
        text='"It is a long way to the harbour from here," she said. He answered, "No." Then they walked for a long time across the empty quay.'
        self.assertEqual([row[0] for row in module.derived_tasks(text)],['continuation'])
    def test_fragment_split_preserves_every_character_of_the_source_target(self):
        text=' '.join(['word'+str(i) for i in range(50)])
        task=list(module.derived_tasks(text))[0]
        self.assertEqual(task[3],text.index('word25'))
        self.assertEqual(task[4],len(text))

if __name__=='__main__':unittest.main()
