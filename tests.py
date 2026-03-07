#Student name: Javeria Alam
#Student id: 218714451

import pytest

from solution import EventRegistration, UserStatus, DuplicateRequest, NotFound


def test_register_until_capacity_then_waitlist_fifo_positions():
    er = EventRegistration(capacity=2)

    s1 = er.register("u1")
    s2 = er.register("u2")
    s3 = er.register("u3")
    s4 = er.register("u4")

    assert s1 == UserStatus("registered")
    assert s2 == UserStatus("registered")
    assert s3 == UserStatus("waitlisted", 1)
    assert s4 == UserStatus("waitlisted", 2)

    snap = er.snapshot()
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3", "u4"]


def test_cancel_registered_promotes_earliest_waitlisted_fifo():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist
    er.register("u3")  # waitlist

    er.cancel("u1")  # should promote u2

    assert er.status("u1") == UserStatus("none")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u2"]
    assert snap["waitlist"] == ["u3"]


def test_duplicate_register_raises_for_registered_and_waitlisted():
    er = EventRegistration(capacity=1)
    er.register("u1")
    with pytest.raises(DuplicateRequest):
        er.register("u1")

    er.register("u2")  # waitlisted
    with pytest.raises(DuplicateRequest):
        er.register("u2")


def test_waitlisted_cancel_removes_and_updates_positions():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist pos1
    er.register("u3")  # waitlist pos2

    er.cancel("u2")    # remove from waitlist

    assert er.status("u2") == UserStatus("none")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]


def test_capacity_zero_all_waitlisted_and_promotion_never_happens():
    er = EventRegistration(capacity=0)
    assert er.register("u1") == UserStatus("waitlisted", 1)
    assert er.register("u2") == UserStatus("waitlisted", 2)

    # No one can ever be registered when capacity=0
    assert er.status("u1") == UserStatus("waitlisted", 1)
    assert er.status("u2") == UserStatus("waitlisted", 2)
    assert er.snapshot()["registered"] == []

    # Cancel unknown should raise NotFound
    with pytest.raises(NotFound):
        er.cancel("missing")



#################################################################################
# Add your own additional tests here to cover more cases and edge cases as needed.
#################################################################################

# =============================================================================
# ADDITIONAL TESTS
# Covers: Functional Requirements, Constraints, Invariants, and Edge Cases
# =============================================================================

# -----------------------------------------------------------------------------
# FUNCTIONAL REQUIREMENTS - Registration (FR1, FR2, FR3, FR4)
# -----------------------------------------------------------------------------

def test_fr1_capacity_zero_is_valid():
    # FR1, C9: capacity of zero is a valid non-negative integer
    er = EventRegistration(capacity=0)
    assert er.snapshot()["registered"] == []
    assert er.snapshot()["waitlist"] == []

def test_fr1_negative_capacity_raises():
    # FR1, C9: negative capacity must be rejected
    with pytest.raises(ValueError):
        EventRegistration(capacity=-1)

def test_fr2_user_registered_when_space_available():
    # FR2, AC1, C1: user goes to registered list when space exists
    er = EventRegistration(capacity=3)
    result = er.register("u1")
    assert result == UserStatus("registered")
    assert er.snapshot()["registered"] == ["u1"]

def test_fr3_user_waitlisted_when_full():
    # FR3, AC2, C1, C2: user goes to waitlist when at capacity
    er = EventRegistration(capacity=1)
    er.register("u1")
    result = er.register("u2")
    assert result == UserStatus("waitlisted", 1)
    assert er.snapshot()["waitlist"] == ["u2"]

def test_fr4_duplicate_registered_raises():
    # FR4, AC5, C3, C4: duplicate registration raises DuplicateRequest
    er = EventRegistration(capacity=2)
    er.register("u1")
    with pytest.raises(DuplicateRequest):
        er.register("u1")

def test_fr4_duplicate_waitlisted_raises():
    # FR4, AC5, C3, C4: duplicate registration while waitlisted raises DuplicateRequest
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    with pytest.raises(DuplicateRequest):
        er.register("u2")

def test_fr4_duplicate_does_not_alter_state():
    # FR4, AC5, C5: system state is unchanged after a DuplicateRequest
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    try:
        er.register("u1")
    except DuplicateRequest:
        pass
    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u2"]

# -----------------------------------------------------------------------------
# FUNCTIONAL REQUIREMENTS - Cancellation (FR5, FR6, FR7, FR8, FR9, FR10)
# -----------------------------------------------------------------------------

def test_fr5_cancel_registered_user_removes_them():
    # FR5, C5: canceling a registered user removes them
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.register("u2")
    er.cancel("u1")
    assert er.status("u1") == UserStatus("none")
    assert er.snapshot()["registered"] == ["u2"]

def test_fr6_cancel_waitlisted_user_removes_them():
    # FR6, C2, C5: canceling a waitlisted user removes them and updates positions
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.cancel("u2")
    assert er.status("u2") == UserStatus("none")
    assert er.status("u3") == UserStatus("waitlisted", 1)

def test_fr7_cancel_registered_promotes_first_waitlisted():
    # FR7, AC3, C2, C5: earliest waitlisted user is promoted on registered cancel
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.cancel("u1")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

def test_fr8_cancel_registered_no_waitlist_no_promotion():
    # FR8, AC4, C1, C5: canceling with empty waitlist simply frees a slot
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.register("u2")
    er.cancel("u1")
    snap = er.snapshot()
    assert snap["registered"] == ["u2"]
    assert snap["waitlist"] == []

def test_fr9_cancel_nonexistent_raises_notfound():
    # FR9, AC7, C6: canceling a user never in the system raises NotFound
    er = EventRegistration(capacity=2)
    with pytest.raises(NotFound):
        er.cancel("ghost")

def test_fr10_cancel_already_canceled_raises_notfound():
    # FR10, AC7, C6: canceling a previously canceled user raises NotFound
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.cancel("u1")
    with pytest.raises(NotFound):
        er.cancel("u1")

# -----------------------------------------------------------------------------
# FUNCTIONAL REQUIREMENTS - Status & Snapshot (FR11, FR12)
# -----------------------------------------------------------------------------

def test_fr11_status_registered():
    # FR11, AC6, C5: status returns "registered" correctly
    er = EventRegistration(capacity=2)
    er.register("u1")
    assert er.status("u1") == UserStatus("registered")

def test_fr11_status_waitlisted_with_position():
    # FR11, AC6, C5, C7: status returns "waitlisted" with 1-based position
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    assert er.status("u2") == UserStatus("waitlisted", 1)
    assert er.status("u3") == UserStatus("waitlisted", 2)

def test_fr11_status_none_for_unknown_user():
    # FR11, AC6: status returns "none" for a user not in the system
    er = EventRegistration(capacity=2)
    assert er.status("ghost") == UserStatus("none")

def test_fr12_snapshot_returns_ordered_lists():
    # FR12, C2, C5: snapshot returns correctly ordered registered and waitlist
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    snap = er.snapshot()
    assert isinstance(snap["registered"], list)
    assert isinstance(snap["waitlist"], list)
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3"]

def test_fr12_snapshot_empty_system():
    # FR12, C5: snapshot on empty system returns empty lists
    er = EventRegistration(capacity=5)
    snap = er.snapshot()
    assert snap["registered"] == []
    assert snap["waitlist"] == []

# -----------------------------------------------------------------------------
# FUNCTIONAL REQUIREMENTS - Re-registration (FR13)
# -----------------------------------------------------------------------------

def test_fr13_reregister_after_cancel_goes_to_registered():
    # FR13, AC8, C3, C8: re-registering after cancel works when space is free
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.cancel("u1")
    result = er.register("u1")
    assert result == UserStatus("registered")

def test_fr13_reregister_after_cancel_goes_to_waitlist_when_full():
    # FR13, AC8, C8: re-registering when full places user at back of waitlist
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.cancel("u2")
    er.register("u3")
    er.register("u2")
    assert er.status("u2") == UserStatus("waitlisted", 2)

def test_fr13_reregister_has_no_residual_state():
    # FR13, AC8, C3, C8: re-registered user has no memory of previous position
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.cancel("u2")
    er.register("u2")
    assert er.status("u2") == UserStatus("waitlisted", 1)

# -----------------------------------------------------------------------------
# FUNCTIONAL REQUIREMENTS - User Identity (FR14)
# -----------------------------------------------------------------------------

def test_fr14_user_ids_are_case_sensitive():
    # FR14, C10: "Alice" and "alice" are treated as different users
    er = EventRegistration(capacity=2)
    er.register("Alice")
    er.register("alice")
    snap = er.snapshot()
    assert "Alice" in snap["registered"]
    assert "alice" in snap["registered"]

def test_fr14_empty_string_user_id_raises():
    # FR14, C10: empty string is not a valid user_id
    er = EventRegistration(capacity=2)
    with pytest.raises(ValueError):
        er.register("")

# -----------------------------------------------------------------------------
# CONSTRAINTS
# -----------------------------------------------------------------------------

def test_c1_registered_never_exceeds_capacity():
    # C1: at no point do registered users exceed capacity
    er = EventRegistration(capacity=3)
    for i in range(10):
        er.register(f"u{i}")
    assert len(er.snapshot()["registered"]) <= 3

def test_c2_waitlist_fifo_order_preserved_after_multiple_cancels():
    # C2: FIFO order is preserved after multiple waitlist cancellations
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.register("u4")
    er.cancel("u2")
    assert er.snapshot()["waitlist"] == ["u3", "u4"]

def test_c2_promotion_always_fifo():
    # C2: promotion always takes the earliest waitlisted user
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.cancel("u1")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

def test_c3_user_cannot_appear_twice():
    # C3: a user can only exist once across the entire system
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    registered = er.snapshot()["registered"]
    waitlist = er.snapshot()["waitlist"]
    all_users = registered + waitlist
    assert len(all_users) == len(set(all_users))

def test_c4_user_cannot_be_registered_and_waitlisted():
    # C4: no user can exist in both registered and waitlist simultaneously
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    snap = er.snapshot()
    overlap = set(snap["registered"]) & set(snap["waitlist"])
    assert len(overlap) == 0

def test_c5_state_consistent_after_sequential_cancellations():
    # C5: state remains consistent after multiple sequential cancellations
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.cancel("u1")
    er.cancel("u2")
    er.cancel("u3")
    snap = er.snapshot()
    assert snap["registered"] == []
    assert snap["waitlist"] == []

def test_c7_waitlist_positions_are_one_based():
    # C7: first waitlisted user has position 1, not 0
    er = EventRegistration(capacity=0)
    result = er.register("u1")
    assert result == UserStatus("waitlisted", 1)

def test_c7_positions_update_correctly_after_waitlist_cancel():
    # C7: positions correctly shift after a waitlisted user cancels
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.register("u4")
    er.cancel("u2")
    assert er.status("u3") == UserStatus("waitlisted", 1)
    assert er.status("u4") == UserStatus("waitlisted", 2)

def test_c8_reregistration_permitted_after_cancel():
    # C8: users are explicitly allowed to re-register after canceling
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.cancel("u1")
    result = er.register("u1")
    assert result == UserStatus("registered")

# -----------------------------------------------------------------------------
# INVARIANTS
# -----------------------------------------------------------------------------

def test_invariant_no_user_in_multiple_states_after_promotion():
    # Invariant: after promotion, user exists only in registered, not waitlist
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.cancel("u1")
    snap = er.snapshot()
    assert "u2" in snap["registered"]
    assert "u2" not in snap["waitlist"]

def test_invariant_consistency_after_rapid_operations():
    # Invariant C5: state is consistent after many back-to-back operations
    er = EventRegistration(capacity=2)
    for i in range(5):
        er.register(f"u{i}")
    er.cancel("u0")
    er.cancel("u1")
    snap = er.snapshot()
    all_users = snap["registered"] + snap["waitlist"]
    assert len(all_users) == len(set(all_users))
    assert len(snap["registered"]) <= 2

def test_invariant_no_ghost_users_after_cancel():
    # Invariant C5: canceled users do not linger in any structure
    er = EventRegistration(capacity=2)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.cancel("u3")
    snap = er.snapshot()
    assert "u3" not in snap["registered"]
    assert "u3" not in snap["waitlist"]

# -----------------------------------------------------------------------------
# NON-TRIVIAL SCENARIOS
# -----------------------------------------------------------------------------

def test_scenario_multiple_sequential_cancellations_promote_in_order():
    # Non-trivial: each cancellation promotes the next FIFO user in order
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.cancel("u1")
    assert er.status("u2") == UserStatus("registered")
    er.cancel("u2")
    assert er.status("u3") == UserStatus("registered")
    er.cancel("u3")
    assert er.snapshot()["registered"] == []

def test_scenario_waitlisted_user_cancels_before_promotion():
    # Non-trivial: waitlisted user cancels before being promoted
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.cancel("u2")
    assert er.status("u2") == UserStatus("none")
    assert er.status("u3") == UserStatus("waitlisted", 1)
    er.cancel("u1")
    assert er.status("u3") == UserStatus("registered")

def test_scenario_capacity_zero_no_promotion_ever():
    # Non-trivial AC9, C1: with capacity 0, no user is ever promoted
    er = EventRegistration(capacity=0)
    er.register("u1")
    er.register("u2")
    er.cancel("u1")
    assert er.status("u2") == UserStatus("waitlisted", 1)
    assert er.snapshot()["registered"] == []

def test_scenario_query_after_promotion():
    # Non-trivial: status query immediately after promotion reflects new state
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.cancel("u1")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u1") == UserStatus("none")

def test_scenario_full_cycle_register_cancel_reregister():
    # Non-trivial: full user lifecycle works correctly end to end
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")
    er.cancel("u1")
    er.cancel("u2")
    result = er.register("u1")
    assert result == UserStatus("registered")
    assert er.snapshot()["registered"] == ["u1"]
    assert er.snapshot()["waitlist"] == []
