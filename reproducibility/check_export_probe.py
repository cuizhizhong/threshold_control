"""严格比较隔离 MATLAB 导出候选；不改变最终比较器或科学数值判据。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw
import pymupdf

from bootstrap import dump
from compare_runs import compare_figure, _font_streams


def drawings(page):
    return [{key: value for key, value in item.items() if key != 'seqno'}
            for item in page.get_drawings()]


def compare(a: Path, b: Path, output: Path):
    cases = []
    for first in sorted(a.rglob('*')):
        if first.suffix not in {'.pdf', '.png', '.svg'}:
            continue
        if 'visual_reference' in first.parts:
            continue
        rel = first.relative_to(a)
        second = b / rel
        if not second.is_file():
            cases.append({'file': rel.as_posix(), 'passed': False, 'reason': 'missing'})
            continue
        if first.suffix == '.pdf':
            # 非正式名称确保不触发最终报告中已批准的三个窄例外。
            case = compare_figure(first, second, 'probe/' + rel.as_posix())
            with pymupdf.open(first) as da, pymupdf.open(second) as db:
                aa, bb = da[0], db[0]
                case.update(scientific_vectors_exact_without_seqno=drawings(aa) == drawings(bb),
                            font_streams_exact=_font_streams(da, aa) == _font_streams(db, bb),
                            text_geometry_exact=aa.get_text('rawdict') == bb.get_text('rawdict'),
                            page_size_a=list(aa.rect), page_size_b=list(bb.rect))
                if aa.rect == bb.rect:
                    pix_a, pix_b = aa.get_pixmap(dpi=150, alpha=False), bb.get_pixmap(dpi=150, alpha=False)
                    im_a = Image.frombytes('RGB', (pix_a.width, pix_a.height), pix_a.samples)
                    im_b = Image.frombytes('RGB', (pix_b.width, pix_b.height), pix_b.samples)
                    array_a, array_b = np.asarray(im_a), np.asarray(im_b)
                    changed = np.any(array_a != array_b, axis=2)
                    overlay = np.asarray(im_a).copy()
                    overlay[changed] = [255, 0, 0]
                    sheet = Image.new('RGB', (3 * im_a.width, im_a.height + 30), 'white')
                    for j, (label, tile) in enumerate([('PROCESS A', im_a), ('PROCESS B', im_b), ('ANY DIFFERENCE', Image.fromarray(overlay))]):
                        sheet.paste(tile, (j*im_a.width, 30))
                        ImageDraw.Draw(sheet).text((j*im_a.width+8, 8), label, fill='black')
                    target = output / 'diff' / rel.with_suffix('.png')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    sheet.save(target)
        elif first.suffix == '.png':
            with Image.open(first) as im_a, Image.open(second) as im_b:
                aa, bb = np.asarray(im_a.convert('RGB')), np.asarray(im_b.convert('RGB'))
            case = {'file': rel.as_posix(), 'size_a': list(aa.shape), 'size_b': list(bb.shape)}
            if aa.shape == bb.shape:
                diff = np.abs(aa.astype(int)-bb.astype(int))
                case.update(passed=bool(not np.any(diff)), pixel_equal=bool(not np.any(diff)),
                            maximum_channel_difference=int(diff.max()),
                            changed_channel_count=int(np.count_nonzero(diff)),
                            changed_channel_fraction=float(np.count_nonzero(diff)/diff.size))
            else:
                case.update(passed=False, reason='PNG dimensions changed')
        else:
            aa, bb = ET.parse(first).getroot(), ET.parse(second).getroot()
            nodes_a, nodes_b = list(aa.iter()), list(bb.iter())
            differences = []
            if len(nodes_a) == len(nodes_b):
                for k, (x, y) in enumerate(zip(nodes_a, nodes_b)):
                    if x.tag != y.tag or x.attrib != y.attrib or x.text != y.text:
                        differences.append({'node': k, 'tag': x.tag.rsplit('}',1)[-1],
                            'changed_attributes': [key for key in sorted(x.attrib.keys()|y.attrib.keys()) if x.attrib.get(key) != y.attrib.get(key)],
                            'text_changed': x.text != y.text})
            case = {'file': rel.as_posix(), 'passed': len(nodes_a)==len(nodes_b) and not differences,
                    'xml_nodes_a':len(nodes_a), 'xml_nodes_b':len(nodes_b),
                    'different_nodes':len(differences), 'first_differences':differences[:12]}
        cases.append(case)
    report = {'purpose':'strict export-method regression, not numerical rerun',
              'first':str(a), 'second':str(b), 'cases':cases,
              'passed':bool(cases) and all(case['passed'] for case in cases),
              'scientific_comparison_or_tolerance_changed':False}
    dump(output / 'strict_export_comparison.json', report)
    return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('first',type=Path)
    parser.add_argument('second',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    report=compare(args.first,args.second,args.output)
    print(json.dumps({'passed':report['passed'],'cases':report['cases']},ensure_ascii=False,indent=2))
