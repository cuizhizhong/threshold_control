"""用pypdf保留原图/预览矢量内容，生成9页并排对照；仅写独立预览目录。"""
import hashlib
import io
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageOps, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'paper/tmp/supplement_style_preview_20261027'
FIGURES = ('Main6', 'Main8', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S8')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def overlay(width, height, name, page_number, draw_body=False, total=None, old_label='原图', new_label='预览'):
    stream = io.BytesIO()
    c = Canvas(stream, pagesize=(width, height))
    c.setFont('Chinese', 17)
    label = f'正文图{name[4:]}' if name.startswith('Main') else f'补充图{name}'
    c.drawCentredString(width / 2, height - 34, f'{label}：风格预览对照')
    c.setFont('Chinese', 10)
    c.drawCentredString(width / 4, height - 61, old_label)
    c.drawCentredString(3 * width / 4, height - 61, new_label)
    c.setStrokeColorRGB(.8, .8, .8)
    c.line(width / 2, 48, width / 2, height - 76)
    c.setFont('Chinese', 9)
    c.drawString(35, 24, '独立预览；未替换正式图件，未修改稿件引用。')
    c.drawRightString(width - 35, 24, f'{page_number} / {total or len(FIGURES)}')
    c.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def refinement_comparison():
    """把上一版预览和本轮两图排在一起，供作者直接判断变化。"""
    width = 1190.551181
    writer = PdfWriter()
    previous = OUT / 'before_S6_S8_refinement'
    for index, name in enumerate(('S6', 'S8'), 1):
        rec = json.loads((OUT / f'{name}.receipt.json').read_text(encoding='utf-8'))
        old_receipt = json.loads((previous / f'{name}.receipt.json').read_text(encoding='utf-8'))
        assert sha(previous / f'{name}.pdf') == old_receipt['output_sha256'][f'{name}.pdf']
        assert sha(OUT / f'{name}.pdf') == rec['output_sha256'][f'{name}.pdf']
        pages = [PdfReader(path).pages[0] for path in (previous / f'{name}.pdf', OUT / f'{name}.pdf')]
        plot_width = rec['size_mm'][0] * 72 / 25.4
        height = max(float(p.mediabox.height) * plot_width / float(p.mediabox.width) for p in pages) + 148
        sheet = writer.add_blank_page(width=width, height=height)
        for side, page in enumerate(pages):
            scale = plot_width / float(page.mediabox.width)
            actual_h = float(page.mediabox.height) * scale
            x = (side + .5) * width / 2 - plot_width / 2
            y = (height - 100 - 48 - actual_h) / 2 + 48
            sheet.merge_transformed_page(page, Transformation().scale(scale).translate(x, y))
        sheet.merge_page(overlay(width, height, name, index, total=2,
                                old_label='上一版预览', new_label='本轮修改'))
    dest = OUT / 'S6_S8_refinement_comparison.pdf'
    with dest.open('wb') as f:
        writer.write(f)
    return dest


def main():
    pdfmetrics.registerFont(TTFont('Chinese', 'C:/Windows/Fonts/simhei.ttf'))
    # 对照页总宽420mm，高度随图件收紧；两幅图均按现稿实际印刷宽度展示。
    width = 1190.551181
    writer = PdfWriter()
    receipts = {}
    for index, name in enumerate(FIGURES, 1):
        rec = json.loads((OUT / f'{name}.receipt.json').read_text(encoding='utf-8'))
        receipts[name] = rec
        old, new = ROOT / rec['old_pdf'], OUT / f'{name}.pdf'
        assert sha(old) == rec['old_pdf_sha256']
        assert sha(new) == rec['output_sha256'][new.name]
        plot_width = rec['size_mm'][0] * 72 / 25.4
        pages = [PdfReader(path).pages[0] for path in (old, new)]
        height = max(float(p.mediabox.height) * plot_width / float(p.mediabox.width) for p in pages) + 148
        sheet = writer.add_blank_page(width=width, height=height)
        for side, page in enumerate(pages):
            pw, ph = float(page.mediabox.width), float(page.mediabox.height)
            scale = plot_width / pw
            actual_h = ph * scale
            assert actual_h <= height - 140
            x = (side + .5) * width / 2 - plot_width / 2
            y = (height - 100 - 48 - actual_h) / 2 + 48
            sheet.merge_transformed_page(page, Transformation().scale(scale).translate(x, y))
        sheet.merge_page(overlay(width, height, name, index))
    dest = OUT / 'preview_comparison.pdf'
    with dest.open('wb') as f:
        writer.write(f)

    # 全部新图的缩略总览；单图300dpi文件保留供放大。
    cell_w, cell_h = 660, 550
    board = Image.new('RGB', (3 * cell_w, 3 * cell_h), 'white')
    draw = ImageDraw.Draw(board)
    font = ImageFont.truetype('C:/Windows/Fonts/simhei.ttf', 23)
    for index, name in enumerate(FIGURES):
        r, col = divmod(index, 3)
        im = Image.open(OUT / f'{name}.png').convert('RGB')
        im.thumbnail((cell_w - 30, cell_h - 66), Image.Resampling.LANCZOS)
        xx = col * cell_w + (cell_w - im.width) // 2
        yy = r * cell_h + 50 + (cell_h - 66 - im.height) // 2
        board.paste(im, (xx, yy))
        title = f'正文图{name[4:]}' if name.startswith('Main') else f'补充图{name}'
        draw.text((col * cell_w + 20, r * cell_h + 14), title, font=font, fill='black')
    board.save(OUT / 'preview_overview.png')

    baseline_path = OUT / 'formal_files_before.json'
    baseline = json.loads(baseline_path.read_text(encoding='utf-8')) if baseline_path.exists() else {
        p.relative_to(ROOT).as_posix(): sha(p) for p in (ROOT / 'paper').rglob('*')
        if p.is_file() and 'tmp' not in p.parts and p.suffix in {'.tex', '.bib', '.pdf'}}
    changed = [rel for rel, h in baseline.items() if sha(ROOT / rel) != h]
    # 开始时已有的表头任务在预览期间完成本地提交；只允许识别其已提交主PDF更新，绝不覆写。
    concurrent = []
    assert set(changed) <= {'paper/flatten_curve_analysis_cn.pdf'}, changed
    for rel in changed:
        head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        blob = subprocess.check_output(['git', 'show', f'{head}:{rel}'], cwd=ROOT)
        current = sha(ROOT / rel)
        assert hashlib.sha256(blob).hexdigest() == current, f'发现未提交的并行正式稿变动：{rel}'
        concurrent.append(dict(path=rel, before_sha256=baseline[rel], current_sha256=current,
                               matches_git_commit=head, preview_script_writes_this_path=False))
    aux_count = receipts['S4']['checks']['auxiliary_boundary_roots']['count']
    assert aux_count == 241
    result = dict(preview_only=True, figures=list(FIGURES), comparison_pages=len(writer.pages),
                  formal_file_count=len(baseline), unchanged_formal_files=len(baseline) - len(changed),
                  protected_figure_and_tex_files_unchanged=True, concurrent_committed_pdf_changes=concurrent,
                  palette_sha256=sha(OUT / 'parula256.json'),
                  output_sha256={p.name:sha(p) for p in (dest, OUT / 'preview_overview.png')},
                  scientific_model_optimizations=0, fits=0, phase_classification_solves=0,
                  auxiliary_S4_unique_boundary_points=aux_count,
                  auxiliary_S4_actual_brentq_calls=receipts['S4']['checks']['auxiliary_boundary_roots']['initial_preview_execution_history']['total_boundary_root_calls'],
                  preview_scripts_sha256={p.name:sha(p) for p in (ROOT / 'nr_audit').glob('preview_*.py')},
                  note='S4的241个边界点为本轮授权的绘图辅助求根；其余图复用已有数据。')
    (OUT / 'preview_manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# 图件风格预览', '', '先看 `preview_comparison.pdf`：每页左为原图、右为预览，均按原稿实际印刷宽度展示。',
             '', '9幅图各有同名PDF、300dpi PNG与输入/输出核对收据；`preview_overview.png`为新版总览。',
             '', '## 核对', '', f'- 原正式文件中{len(baseline) - len(changed)}份SHA-256未改变，全部正式图件和TeX引用保留。',
             '- 全部热图采用MATLAB直接导出的完整parula(256)；正文图8(a)的分类颜色保留。',
             '- 图S4仅在原241个阈值点重新求触发边界；没有优化、拟合或相图分类。',
             '- 排版迭代期间图S4辅助边界累计实际调用brentq 1205次（5轮，独立阈值点241）；现已缓存，后续版面修改不重复求根。',
             '- 图S8保留原图竖线151.90、26326；第一条与现图注152.55的既有差异未修改。',
             '- 按追加的F4参考：正文图6/8及补充图S4/S8采用红色点划等高线、黑色数字、不加白色文字描边；等级、数据与结构边界含义未改变。',
             '- 未替换旧图、TeX引用或论文PDF；未提交、未推送。', '']
    if concurrent:
        lines.extend(['## 并行修改说明', '',
                      '- 预览期间，开始时已有的表头修订完成独立本地提交；主稿PDF随该提交更新，当前字节与该提交一致。本预览脚本未写入该文件。', ''])
    if (OUT / 'before_S6_S8_refinement/S6.pdf').exists():
        focused = refinement_comparison()
        result['S6_S8_refinement_comparison_sha256'] = sha(focused)
        result['S6_S8_refinement_details'] = dict(
            source_data_unchanged=True,
            S6_interpolation=receipts['S6']['checks']['panels']['base']['display_interpolation'],
            S6_white_halo_removed=True, S8_annotation_40_years_removed=True,
            S8_contour_fix='先设置对数横轴，再定位标注；不隐藏已切线的标签')
        (OUT / 'preview_manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        lines.extend(['## S6、S8第二轮预览', '',
                      '- `S6_S8_refinement_comparison.pdf`：左侧上一版预览，右侧本轮修改。',
                      '- S6去掉线条白边，按已有跳变边界分区做原非均匀网格的RGB双线性显示插值，避免跨分支混色；零区用纯色矢量遮罩限定，原节点值不变，边界保留矢量线，图例放(b)右上角。',
                      '- S8删去“约40年”的注记与箭头；先设置对数横轴再标注等值线，避免错误的大缺口。',
                      '- 本轮无求根、优化、拟合、分类或新增科学网格；正式图件和稿件保持。', ''])
    (OUT / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
