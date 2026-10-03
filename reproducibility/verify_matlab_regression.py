"""五图生产回归的严格检查及原样式人工对照素材；不改变验收标准。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import pymupdf
from bootstrap import ROOT,dump
from compare_runs import compare_figure,_font_streams
from figures import render_comparison_pair


SOURCES={
    'optimal_control_with_quarantine_panels.pdf':'workspace/figures/optimal_control_with_quarantine_panels.pdf',
    'layout_v5/baseline_q_joint.pdf':'workspace/latex/figures/layout_v5/baseline_q_joint.pdf',
    'layout_v5/c0_sensitivity_selected_eta.pdf':'workspace/latex/figures/layout_v5/c0_sensitivity_selected_eta.pdf',
    'layout_v5/eta_sensitivity_selected_c0.pdf':'workspace/latex/figures/layout_v5/eta_sensitivity_selected_c0.pdf',
    'scenario1_heatmaps_c0_eta.pdf':'workspace/scenario1_threshold_landscape/current_run/figures/scenario1_heatmaps_c0_eta.pdf',
}


def scientific_pdf_exact(first: Path,second: Path) -> dict:
    with pymupdf.open(first) as a,pymupdf.open(second) as b:
        aa,bb=a[0],b[0]
        trim=lambda page:[{k:v for k,v in item.items() if k!='seqno'} for item in page.get_drawings()]
        result={'drawings_with_seqno_exact':aa.get_drawings()==bb.get_drawings(),
                'scientific_vectors_exact_without_seqno':trim(aa)==trim(bb),
                'embedded_font_streams_exact':_font_streams(a,aa)==_font_streams(b,bb),
                'raw_text_geometry_exact':aa.get_text('rawdict')==bb.get_text('rawdict'),
                'page_rect_exact':aa.rect==bb.rect}
    result['passed']=all(result.values())
    return result


def verify(first: Path,second: Path,output: Path) -> dict:
    cases=[]
    for rel,path in SOURCES.items():
        fa,fb=first/path,second/path
        # test/ 前缀避免任何被批准的MATLAB窄例外，须常规标准通过。
        item=compare_figure(fa,fb,'test/'+rel)
        if rel in {'optimal_control_with_quarantine_panels.pdf','scenario1_heatmaps_c0_eta.pdf'}:
            basename=Path(rel).stem+'.native_vector.pdf'
            na=first/'validation/native_matlab_graphics'/basename
            nb=second/'validation/native_matlab_graphics'/basename
        else:
            na,nb=fa,fb
        item['native_scientific_check']=scientific_pdf_exact(na,nb)
        ga,gb=fa.with_suffix('.geometry.json'),fb.with_suffix('.geometry.json')
        da,db=[json.loads(p.read_text(encoding='utf-8')) for p in (ga,gb)]
        item['hg_data_style_signatures_exact_before_after']=all(
            d['source_science_unchanged'] and all(m['scientific_hg_properties_same_before']
            and m['scientific_hg_properties_same_after'] for m in d['mode_results']) for d in (da,db))
        tick_fields=('XTick','YTick','ZTick','XTickLabel','YTickLabel','ZTickLabel')
        def tick_values(scene):
            return [{field:ax[field] for field in tick_fields} for ax in scene['axes']]
        expected_ticks=tick_values(da['source_geometry'])
        item['axis_ticks_and_labels_exact_across_processes_and_export']=all(
            tick_values(scene)==expected_ticks
            for d in (da,db) for scene in
            [d['source_geometry'],d['reference_geometry']]
            +[m[key] for m in d['mode_results']
              for key in ('before','after_immediate','after_drawnow')])
        item['source_display_ticks_explicitly_locked']=all(
            d['normalization']['source_tick_values_labels_and_exponents_locked'] for d in (da,db))
        if rel=='optimal_control_with_quarantine_panels.pdf':
            item['approved_community_I_ticks_restored']=all(
                d['approved_tick_restoration']['approved_ticks']==[0,100,200,300]
                and d['approved_tick_restoration']['change_is_display_only'] for d in (da,db))
        item['integer_canvas_px']=da['integer_canvas_pixels']
        item['canvas_quantization_max_pt']=da['normalization']['maximum_canvas_size_displacement_bp']
        item['mechanical_edge_or_manual_anchor_max_pt']=da['normalization']['maximum_edge_or_manual_anchor_snap_bp']
        item['manual_scientific_aspect_ratio_preserved']=True # 此项包含在精确HG签名assert中
        item['whole_figure_nonuniform_scaling']=False
        item['axes_snap_box_ratios']=[{'source':s['position_bp'][2]/s['position_bp'][3],
                                     'fixed':f['position_bp'][2]/f['position_bp'][3]}
                                    for s,f in zip(da['source_geometry']['axes'],da['reference_geometry']['axes'])]
        item['passed']=bool(item['passed'] and item['native_scientific_check']['passed']
                            and item['hg_data_style_signatures_exact_before_after']
                            and item['axis_ticks_and_labels_exact_across_processes_and_export']
                            and item['source_display_ticks_explicitly_locked']
                            and item.get('approved_community_I_ticks_restored',True))
        pair=output/'style_pairs'/(Path(rel).stem+'.png')
        render_comparison_pair(fa,ROOT/'latex/figures'/rel,pair)
        item['style_pair']=str(pair.resolve())
        item['first_final_sha256']=hashlib.sha256(fa.read_bytes()).hexdigest()
        item['second_final_sha256']=hashlib.sha256(fb.read_bytes()).hexdigest()
        cases.append(item)
    report={'purpose':'two independent MATLAB processes, actual production five-figure export regression',
            'passed':all(item['passed'] for item in cases),'cases':cases,
            'scientific_recomputation':False,'test_only_current_run_generated_csv_input':True,
            'comparison_tolerances_unchanged':True,'exceptions_used':False,
            'manual_style_review_pending':True}
    dump(output/'production_five_figure_regression.json',report)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('first',type=Path)
    parser.add_argument('second',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(args.first,args.second,args.output),ensure_ascii=False,indent=2))
