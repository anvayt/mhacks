"""Deterministic text; no LLM text and no locally modeled energy/cost numbers."""
import math
from urllib.parse import quote, urlsplit

WELCOME = ("Hi, I'm Hidden Rent 🏠 I show the predicted heating and cooling cost a rental listing doesn't.\n"
           'Send an Ann Arbor address or a Zillow, Redfin or Apartments.com link.')


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def money(value):
    return f'${value:,.0f}'


def band(value):
    if not isinstance(value, dict) or not number(value.get('p50')):
        return None
    if number(value.get('p10')) and number(value.get('p90')):
        return f"{money(value['p10'])}–{money(value['p90'])} (most likely {money(value['p50'])})"
    return money(value['p50'])


def question_text(question):
    if not question:
        return ''
    lines = [question['text']]
    lines += [f"{i}) {o['label']}" for i, o in enumerate(question.get('options', []), 1)]
    return '\n'.join(lines + ['Reply with an option number, the answer, or skip.'])


def estimate_text(est, question=None):
    lines = ['🏠 ' + est.get('building', {}).get('address', 'Your rental')]
    grades = est.get('grade_span') or []
    grade = est.get('grade')
    if grade:
        label = f'Grade {grades[0]}–{grades[-1]}' if len(grades) > 1 and not est.get('locked') else f'Grade {grade}'
        lines.append(label + (' 🔒 locked' if est.get('locked') else '') + ' (predicted)')
    if number(est.get('score')):
        lines.append(f"Score {est['score']}/100 (predicted)")
    pct = est.get('percentile_city')
    if number(pct) and 0 <= pct <= 1:
        lines.append(f'Top {(1 - pct) * 100:.1f}% citywide by predicted efficiency (from API percentile)')
    yearly = band(est.get('bill', {}).get('annual'))
    if yearly:
        lines.append('Predicted ' + ('cooling' if est.get('bill', {}).get('building_annual') else 'heating + cooling') + f': {yearly}/year')
    if est.get('bill', {}).get('note'):
        lines.append(est['bill']['note'])
    hidden = est.get('hidden_rent_usd_mo')
    if number(hidden):
        lines.append(f'Hidden rent: {money(hidden)}/month vs a typical same-size unit' if hidden >= 0 else
                     f'{money(abs(hidden))}/month less than a typical same-size unit')
    co2 = est.get('co2_t') or {}
    if number(co2.get('p50')):
        lines.append(f"Predicted heating + cooling CO₂: {co2['p50']:g} tonnes/year")
    if est.get('building', {}).get('sqft_estimated'):
        lines.append('Unit size is estimated from public records; confirm it in the web report.')
    if question:
        lines += ['', question_text(question)]
    else:
        lines.append('Say options for projected improvements.')
    return '\n'.join(lines)


def suggestions_text(items):
    lines = ['Your options (effects are projected if completed):']
    if not items:
        return 'No commitments are available for this home yet.'
    for i, item in enumerate(items, 1):
        head = f"{i}) {item['title']} — {item.get('who_acts', 'ask your landlord')}"
        p = item.get('projected')
        if item.get('pending_model') or not p:
            # Do not borrow rebate/GRH/effect figures or numeric note text for tips.
            lines.append(head + '. Tip only; this model cannot price its effect here.')
            continue
        figures = []
        usd = p.get('usd_saved_yr')
        if number(usd):
            figures.append(f'{money(usd)}/year saved' if usd >= 0 else f'costs {money(abs(usd))}/year more')
        co2 = p.get('co2_kg_saved_yr')
        if number(co2):
            figures.append(f'{abs(co2):g} kg CO₂/year ' + ('less' if co2 >= 0 else 'more'))
        if number(item.get('grh_points')):
            figures.append(f"{item['grh_points']} GRH points")
        lines.append(head + (': ' + ', '.join(figures) if figures else '') + '.')
    return '\n'.join(lines + ['Reply "try" plus option numbers to choose a what-if; then "ff" plus days to simulate it. No commitment is saved.'])


def simulation_text(data):
    if data.get('label') != 'simulated_projected_if_kept':
        return 'The API did not return a labelled simulation. No savings are claimed.'
    modeled = [c['title'] for c in data.get('commitments', []) if c.get('modeled')]
    if not modeled:
        return 'Simulated, not real usage: no selected actions have modeled effects. Say options and choose a priced what-if.'
    totals = data.get('totals', {})
    lines = ['Simulation, not real usage — projected if completed and kept.', 'Assumed actions: ' + '; '.join(modeled)]
    if number(totals.get('days')):
        lines.append(f"Over {totals['days']} days:")
    usd = totals.get('usd_saved')
    if number(usd):
        amount = f'${abs(usd):,.2f}' if abs(usd) < 10 else money(abs(usd))
        lines.append(f'Projected {amount} saved' if usd >= 0 else f'Projected cost increases by {amount}')
    kg = totals.get('kg_co2_saved')
    if number(kg):
        lines.append(f'{abs(kg):g} kg CO₂ ' + ('avoided (simulated)' if kg >= 0 else 'more (simulated)'))
    lines.append('Your current grade and real streak have not changed. No savings are verified.')
    return '\n'.join(lines)


def links(session_id, web_base, onboard_base):
    sid = quote(session_id, safe='')
    local = any(urlsplit(url).hostname in ('localhost', '127.0.0.1') for url in (web_base, onboard_base))
    return ('Local preview links; public website/onboarding URLs are not configured.\n' if local else '') + (f'Web report: {web_base.rstrip("/")}/share?session={sid}\n'
            f'Compare listings: {web_base.rstrip("/")}/compare?a={sid}\n'
            f'Continue in iMessage: {onboard_base.rstrip("/")}/?session={sid}')
