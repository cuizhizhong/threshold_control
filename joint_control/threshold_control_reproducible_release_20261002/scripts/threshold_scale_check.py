#!/usr/bin/env python3
"""核对比例情景的算术；不估计临床参数，也不求解疫情或 ICU 动态。"""
from __future__ import annotations
import argparse
import json
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path


def positive_decimal(value: str) -> Decimal:
    try:
        x = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError('请输入有效十进制数。') from exc
    if not x.is_finite() or x <= 0:
        raise argparse.ArgumentTypeError('参数必须是有限正数。')
    return x


def calculate(population: Decimal, beds_per_100k: Decimal,
              coefficient: Decimal, design_theta: Decimal) -> dict:
    if design_theta >= 1:
        raise ValueError('代表情景的感染人数比例须小于 1。')
    with localcontext() as ctx:
        ctx.prec = 32
        b = beds_per_100k / Decimal(100000)
        theta = b / coefficient
        result = {
            'inputs': {
                'population': str(population),
                'reference_beds_per_100k': str(beds_per_100k),
                'reference_coefficient': str(coefficient),
                'design_theta': str(design_theta),
            },
            'reference_scenario': {
                'beds': str(b * population),
                'theta': str(theta),
                'eta_persons': str(theta * population),
            },
            'separate_design_scenario': {
                'eta_persons': str(design_theta * population),
                'implied_beds_per_100k_at_reference_coefficient':
                    str(design_theta * coefficient * Decimal(100000)),
                'implied_beds_at_reference_coefficient':
                    str(design_theta * coefficient * population),
                'implied_coefficient_at_reference_bed_density': str(b / design_theta),
                'theta_excess_over_reference_percent':
                    str((design_theta / theta - 1) * Decimal(100)),
            },
            'interpretation': {
                'capacity_source': '陈胤孜等(2021)全国综合ICU资源预测量，不是西安实测可用床位。',
                'coefficient_source': 'Angulo等(2021)S4.1早期COVID-19名义风险比例；移用于本文仅作情景假设。',
                'not_clinical_estimate': True,
                'not_conservative_rounding': design_theta > theta,
                'ICU_occupancy_simulated': False,
                'epidemic_trajectories_recomputed': False,
            },
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--population', type=positive_decimal, default=Decimal('13163000'))
    parser.add_argument('--beds-per-100k', type=positive_decimal, default=Decimal('4.37'))
    parser.add_argument('--coefficient', type=positive_decimal, default=Decimal('0.0252'))
    parser.add_argument('--design-theta', type=positive_decimal, default=Decimal('0.002'))
    parser.add_argument('--output', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'validation/threshold_scale_calculations.json')
    args = parser.parse_args()
    try:
        report = calculate(args.population, args.beds_per_100k, args.coefficient, args.design_theta)
    except ValueError as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    args.output.write_text(text + '\n', encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
