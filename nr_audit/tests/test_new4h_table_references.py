"""引用指代编辑仅限登记的两处前缀，仍拒绝数值、标签和其他文字变化。"""
import pytest

from audit_layout_migration import table_reference_norm


BEFORE = (r'控制时长 & $<0$ & 命题\ref{prop:threshold-tradeoff}、\ref{prop:contact-effects}\\'
          r'拐点 & $>0$ & 命题\ref{prop:s1:lambda-sensitivity}\\')
AFTER = (r'控制时长 & $<0$ & 命题\ref{prop:threshold-tradeoff}、补充命题\ref{prop:contact-effects}\\'
         r'拐点 & $>0$ & 补充命题\ref{prop:s1:lambda-sensitivity}\\')


def test_registered_supplement_reference_prefixes():
    assert table_reference_norm(BEFORE) == table_reference_norm(AFTER)


@pytest.mark.parametrize('changed', [
    AFTER.replace('$<0$', '$>0$'),
    AFTER.replace('prop:contact-effects', 'prop:other'),
    AFTER.replace('控制时长', '清零时间'),
    AFTER.replace('命题\\ref{prop:threshold-tradeoff}', '补充命题\\ref{prop:threshold-tradeoff}'),
])
def test_unregistered_table_changes_rejected(changed):
    assert table_reference_norm(BEFORE) != table_reference_norm(changed)
