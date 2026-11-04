"""Truth conditions for a composite current-lateness claim, not literary prose."""
from foundation.grounding_lessons import arrival_state

def overdue_claim(now: str, scheduled: str, arrived: bool | None) -> dict:
    """Claim: the expected visitor is already late AND still absent at this snapshot.

    Known arrival contradicts the absence conjunct, regardless of arrival time.
    At/before the deadline, 'already late' is false even if arrival is unknown.
    After the deadline with unknown arrival, neither absence nor overdue follows.
    """
    state=arrival_state(now,scheduled,arrived)
    remaining=state['minutes_to_schedule']
    if arrived is True or remaining>=0:
        verdict='contradicted'
    elif arrived is False:
        verdict='supported'
    else:
        verdict='not_established'
    return dict(verdict=verdict,minutes_to_schedule=remaining,arrival_state=state['state'])
