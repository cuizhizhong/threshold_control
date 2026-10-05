"""逐图生成与原图继承的独立正/负例；不构成科学复算。"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bootstrap import sha
import run_all
from joint_extra import figures


class SelectiveFiguresTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='selective_figures_')
        self.root = Path(self.temp.name)
        self.output = self.root/'reproducibility/runs/test'
        self.output.mkdir(parents=True)
        self.labels = {'joint_compare_baseline':'fig:joint:compare',
                       'joint_capacity':'fig:joint:capacity',
                       'joint_phase_weights':'fig:joint:phase',
                       'joint_frontier_baseline':'fig:joint:frontier'}
        inventory = [{'label':f'fig:old:{i}', 'image':f'old_{i}.pdf'} for i in range(20)]
        inventory += [{'label':label, 'image':f'joint_v2/{stem}.pdf'}
                      for stem,label in self.labels.items()]
        hashes = {}
        for item in inventory:
            path = self.root/'latex/figures'/item['image']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(('original:'+item['label']).encode())
            hashes[item['image']] = sha(path)
        self.version = {'inventory':{'main':{'figures':inventory}},
                        'inherited_figure_sha256':hashes, 'textwidth_bp':451.275616438,
                        'generated_figure_labels':['fig:joint:frontier']}
        self.commands = []

    def tearDown(self):
        self.temp.cleanup()

    def fake_plot(self, command, **kwargs):
        self.commands.append(command)
        target = Path(command[command.index('--out')+1])
        self.assertFalse(target.exists() and any(target.iterdir()))
        target.mkdir(parents=True, exist_ok=True)
        selected = command[command.index('--labels')+1:] if '--labels' in command else list(self.labels.values())
        items = []
        for stem,label in self.labels.items():
            if label in selected:
                path = target/(stem+'.pdf')
                path.write_bytes(('new:'+label).encode())
                items.append({'label':label, 'file':str(path), 'file_sha256':sha(path)})
        (target/'figure_manifest.json').write_text(json.dumps({'figures':items}), encoding='utf-8')

    def integrate(self):
        with patch.object(run_all,'ROOT',self.root), patch.object(run_all.subprocess,'run',self.fake_plot):
            return run_all._integrated_figures(self.output,self.version,inherited=True)

    def test_one_generated_and_twenty_three_byte_inherited(self):
        result = self.integrate()
        self.assertEqual(result['figure_count'],24)
        self.assertEqual(result['inherited_figure_count'],23)
        self.assertEqual(self.commands[0][-2:],['--labels','fig:joint:frontier'])
        for item in result['figures']:
            if item.get('inherited'):
                self.assertEqual(sha(Path(item['file'])),sha(Path(item['original_source'])))

    def test_wrong_inherited_hash_stops_before_plot(self):
        self.version['inherited_figure_sha256']['joint_v2/joint_capacity.pdf']='invalid'
        with self.assertRaises(RuntimeError):
            self.integrate()
        self.assertEqual(self.commands,[])

    def test_absent_selection_keeps_four_joint_figures(self):
        del self.version['generated_figure_labels']
        result = self.integrate()
        self.assertNotIn('--labels',self.commands[0])
        self.assertEqual(result['figure_count'],24)
        self.assertEqual(sum(bool(item.get('inherited')) for item in result['figures']),20)

    def test_full_upstream_scope_still_generates_four_joint_figures(self):
        validation=self.output/'validation'
        validation.mkdir()
        prior={'figures':[{'label':item['label'],'file':'fresh/'+item['image']}
                          for item in self.version['inventory']['main']['figures'][:20]]}
        (validation/'figure_generation.json').write_text(json.dumps(prior),encoding='utf-8')
        with patch.object(run_all,'ROOT',self.root), patch.object(run_all.subprocess,'run',self.fake_plot):
            result=run_all._integrated_figures(self.output,self.version,inherited=False)
        self.assertNotIn('--labels',self.commands[0])
        self.assertEqual(result['figure_count'],24)
        self.assertTrue(result['old_figures_regenerated'])
        self.assertFalse(any(item.get('inherited') for item in result['figures']))

    def test_unknown_or_duplicate_selection_rejected(self):
        for labels in (['fig:bad'],['fig:joint:frontier','fig:joint:frontier']):
            self.version['generated_figure_labels']=labels
            with self.assertRaises(ValueError):
                self.integrate()
        self.assertEqual(self.commands,[])

    def test_cli_frontier_calls_only_duration_plot(self):
        res = self.root/'results'
        res.mkdir()
        (res/'validation.json').write_text(json.dumps({'tasks':{key:{'passed':True} for key in 'ABCD'}}),encoding='utf-8')
        (res/'input_manifest.json').write_text('{}',encoding='utf-8')
        target = self.root/'plot'
        args = ['figures.py','--res',str(res),'--out',str(target),'--text\u0077idth-bp','451.275616438','--labels','fig:joint:frontier']
        with patch.object(sys,'argv',args), patch.object(figures,'fig_compare') as a, \
                patch.object(figures,'fig_capacity') as b, patch.object(figures,'fig_phase') as c, \
                patch.object(figures,'fig_duration',return_value=[]) as d:
            figures.main()
        for unused in (a,b,c):
            unused.assert_not_called()
        d.assert_called_once()


if __name__=='__main__':
    unittest.main()
