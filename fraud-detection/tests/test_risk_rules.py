from risk_rules import label_risk, score_transaction


def test_label_risk_thresholds():
    assert label_risk(10) == "low"
    assert label_risk(35) == "medium"
    assert label_risk(75) == "high"


def test_large_amount_adds_risk():
    tx = {
        "device_risk_score": 10,
        "is_international": 0,
        "amount_usd": 1200,
        "velocity_24h": 1,
        "failed_logins_24h": 0,
        "prior_chargebacks": 0,
    }
    assert score_transaction(tx) >= 25


def test_high_risk_signals_produce_high_risk_score():
    tx = {
        "device_risk_score": 85,
        "is_international": 1,
        "amount_usd": 1400,
        "velocity_24h": 8,
        "failed_logins_24h": 6,
        "prior_chargebacks": 2,
    }

    score = score_transaction(tx)

    assert score == 100
    assert label_risk(score) == "high"


def test_low_risk_signals_remain_low_risk():
    tx = {
        "device_risk_score": 8,
        "is_international": 0,
        "amount_usd": 45.2,
        "velocity_24h": 1,
        "failed_logins_24h": 0,
        "prior_chargebacks": 0,
    }

    score = score_transaction(tx)

    assert score == 0
    assert label_risk(score) == "low"


def test_international_transactions_add_risk():
    domestic = {
        "device_risk_score": 10,
        "is_international": 0,
        "amount_usd": 100,
        "velocity_24h": 1,
        "failed_logins_24h": 0,
        "prior_chargebacks": 0,
    }
    international = {**domestic, "is_international": 1}

    assert score_transaction(international) == score_transaction(domestic) + 15


def test_prior_chargebacks_increase_risk_monotonically():
    base = {
        "device_risk_score": 10,
        "is_international": 0,
        "amount_usd": 100,
        "velocity_24h": 1,
        "failed_logins_24h": 0,
        "prior_chargebacks": 0,
    }

    one_chargeback = score_transaction({**base, "prior_chargebacks": 1})
    multiple_chargebacks = score_transaction({**base, "prior_chargebacks": 3})

    assert one_chargeback > score_transaction(base)
    assert multiple_chargebacks > one_chargeback


def test_high_velocity_and_login_failures_raise_score():
    calm = {
        "device_risk_score": 20,
        "is_international": 0,
        "amount_usd": 200,
        "velocity_24h": 1,
        "failed_logins_24h": 0,
        "prior_chargebacks": 0,
    }
    takeover_like = {
        **calm,
        "velocity_24h": 7,
        "failed_logins_24h": 5,
    }

    assert score_transaction(takeover_like) > score_transaction(calm)
