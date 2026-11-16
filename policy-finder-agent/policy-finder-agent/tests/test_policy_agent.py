from datetime import date

from policy_agent import PolicyAgent, parse_version

D = "data/sample_policies"
AS_OF = date(2026, 11, 15)


def agent():
    return PolicyAgent(D, as_of=AS_OF)


def test_version_sorting_is_numeric():
    assert parse_version("1.10") > parse_version("1.9")


def test_picks_newest_approved_travel_policy():
    d = agent().latest["travel policy"]
    assert d.version == "3.0" and str(d.effective_date) == "2026-01-01"


def test_draft_is_ignored():
    assert agent().latest["travel policy"].status == "Approved"
    assert "parental leave policy" not in agent().latest


def test_retired_version_not_latest():
    assert agent().latest["remote work policy"].version == "2.0"


def test_same_date_uses_highest_version_numerically():
    assert agent().latest["expense policy"].version == "1.10"


def test_future_dated_not_in_force_yet():
    early = PolicyAgent(D, as_of=date(2025, 6, 1))
    assert early.latest["travel policy"].version == "2.0"


def test_answer_uses_latest_only():
    ans = agent().ask("What is the hotel limit for travel?")
    assert "220" in ans.text and "180" not in ans.text
    assert "v3.0" in ans.sources[0]


def test_draft_only_policy_reports_not_in_force():
    ans = agent().ask("What is the parental leave policy?")
    assert "no approved" in ans.text.lower()


def test_unknown_policy():
    assert "no matching" in agent().ask("What is the pet policy?").text.lower()
