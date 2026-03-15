## 1. Problem Understanding - Describe the problem your system solves.

System purpose:
Manage event registration with a fixed capacity, automatically handle a FIFO waitlist, support cancellations, prevent duplicates, and provide clear user status feedback while maintaining deterministic and predictable behavior. The system must also handle edge cases, invalid inputs, and ensure transparency for accessibility needs.

Inputs to the system:
- capacity: int (≥0)
- user_id: non-empty string
- Operations: register(user_id), cancel(user_id), status(user_id), snapshot()

Outputs produced by the system:
- UserStatus(state: "registered"/"waitlisted"/"none", position: Optional[int])
- Snapshot of registered and waitlisted users
- Exception messages for duplicate registration, invalid inputs, or not found users

Primary goal of the system:
Ensure reliable, conflict-free registration management with clear, predictable behavior and transparency for users, including automated promotion from waitlist when appropriate, consistent system state during rapid operations, and correct handling of edge cases.

---

## 2. Assumptions - List assumptions about the environment, users, or inputs.

A1: User IDs are unique non-empty strings.
A2: Capacity is a non-negative integer.
A3: System is single-threaded; simultaneous operations are processed sequentially in order.
A4: Users may cancel at any time but cannot be in multiple states simultaneously.
A5: Notifications or feedback are only provided for essential status changes to avoid overload.
A6: Waitlist ordering is preserved FIFO; earliest registered waitlisted user is promoted first.
A7: The system validates all input types and values, raising exceptions for invalid data.
A8: Snapshots reflect the exact system state at the moment of query.

---

## 3. Functional Requirements - Describe the main behaviors the system must perform.

FR1: The system shall register users up to the event capacity. (Derived from original spec)
FR2: The system shall place additional users into a FIFO waitlist when capacity is full. (Derived from original spec)
FR3: The system shall automatically promote the earliest waitlisted user when a registered user cancels. (Derived from C1 – Jane, behavior)
FR4: The system shall prevent duplicate registrations for the same user ID. (Derived from C3 – Jane, behavior)
FR5: The system shall provide deterministic ordering and promotion for all operations, including rapid consecutive registrations and cancellations. (Derived from C2 – Mo, pain point)
FR6: The system shall provide clear feedback and status, including waitlist position, to users, using return values or snapshots as appropriate. (Derived from C4, C7, C8 – Mo/Jane, need/behavior)
FR7: The system shall handle invalid inputs gracefully, raising appropriate exceptions for invalid user IDs or capacity. (New, based on LLM feedback)
FR8: The system shall allow users to re-register after cancellation, placing them according to capacity and waitlist rules. (New, based on LLM feedback)

---

## 4. System Constraints - Constraints are conditions the system must always respect.

C1: The system must automatically promote the earliest waitlisted user upon cancellation.
Derived from persona attribute: Jane – acts quickly, expects automatic conflict handling

C2: Waitlist promotions and ordering must be deterministic given the same sequence of operations.
Derived from persona attribute: Mo – stress if outcomes appear arbitrary

C3: A user cannot be registered or waitlisted more than once.
Derived from persona attribute: Jane – avoid duplicate messages

C4: The system shall provide clear feedback or status updates when a user is promoted, rejected, or their status changes.
Derived from persona attribute: Mo – needs transparency and explanations

C5: The waitlist shall always preserve strict FIFO ordering.
Derived from persona attribute: Jane – expects predictable ordering

C6: The system must handle zero capacity, sequential cancellations, and re-registrations gracefully without errors.
Derived from persona attribute: Mo – handles edge cases explicitly

C7: The system shall validate input types and values, rejecting invalid user IDs or capacity values.
Derived from persona attribute: Derived from persona needs and LLM review

C8: Snapshots must reflect the exact current state of registered and waitlisted users at the moment of query.
Derived from persona attribute: Mo – accessibility / clarity

---

## 5. Acceptance Criteria - Acceptance criteria define how system behavior will be verified.

AC1: Given a user registers when event capacity is not reached, when register(user_id) is called, then the user is added to registered list.
Linked Constraint ID(s): C1

AC2: Given a registered user cancels, when cancel(user_id) is called, then the earliest waitlisted user is promoted to registered.
Linked Constraint ID(s): C1, C2

AC3: Given a user attempts to register twice, when register(user_id) is called, then a DuplicateRequest exception is raised.
Linked Constraint ID(s): C3

AC4: Given a user queries status, when status(user_id) is called, then the system returns UserStatus with correct state and position.
Linked Constraint ID(s): C4, C8

AC5: Given multiple users are on the waitlist, when a registered user cancels, then users are promoted in strict FIFO order.
Linked Constraint ID(s): C2, C5

AC6: Given capacity=0 or multiple cancellations, when users register or cancel, then the system handles all operations gracefully, adding to waitlist as needed.
Linked Constraint ID(s): C6

AC7: Given invalid inputs, when register(user_id) or cancel(user_id) is called, then the system raises a ValueError or equivalent exception.
Linked Constraint ID(s): C7

AC8: Given a previously cancelled user re-registers, when register(user_id) is called, then the system places them correctly according to capacity and waitlist rules.
Linked Constraint ID(s): C6, C8

---

## 6. Edge Cases - Describe unusual or boundary situations the system must handle.

EC1: Zero capacity – all users attempting to register are placed in waitlist; no user is registered.
Expected system behavior: Waitlist order preserved; no user is registered.
Linked Constraint ID(s): C6
Covered by Acceptance Criteria ID(s): AC6

EC2: Duplicate registration attempt – a user attempts to register while already registered or waitlisted.
Expected system behavior: DuplicateRequest exception raised.
Linked Constraint ID(s): C3
Covered by Acceptance Criteria ID(s): AC3

EC3: Sequential cancellations – multiple registered users cancel in a row, including waitlisted users.
Expected system behavior: Earliest waitlisted users are promoted in FIFO order; system state remains consistent.
Linked Constraint ID(s): C1, C2, C5, C6
Covered by Acceptance Criteria ID(s): AC2, AC5, AC6

EC4: Waitlisted user cancels before promotion.
Expected system behavior: User is removed from waitlist; promotion order of remaining waitlisted users remains consistent.
Linked Constraint ID(s): C1, C2
Covered by Acceptance Criteria ID(s): AC2, AC5

EC5: Invalid input handling – empty string or None as user_id, or negative capacity.
Expected system behavior: System raises ValueError or equivalent exception.
Linked Constraint ID(s): C7
Covered by Acceptance Criteria ID(s): AC7

EC6: Re-registration of previously cancelled user.
Expected system behavior: User is treated as new registration and placed according to capacity/waitlist.
Linked Constraint ID(s): C6, C8
Covered by Acceptance Criteria ID(s): AC8

---

## 7. Traceability - Link functional requirements to constraints and acceptance criteria. FR → C → AC mapping

FR1 → C1 → AC1  
FR2 → C5 → AC5  
FR3 → C1 → AC2  
FR4 → C3 → AC3  
FR5 → C2 → AC5  
FR6 → C4, C7, C8 → AC4  
FR7 → C7 → AC7  
FR8 → C6, C8 → AC8  

---

## Revision Notes

Revision Note 1  
Requirement updated: FR5 – deterministic ordering  
Reason: Clarified that deterministic behavior applies to rapid consecutive registrations and cancellations.  
Action: Updated FR5; triggered by LLM feedback.

Revision Note 2  
Requirement updated: FR7 – invalid input handling  
Reason: LLM identified missing handling of invalid user_id or capacity inputs.  
Action: Added FR7; triggered by LLM feedback.

Revision Note 3  
Requirement updated: FR8 – re-registration after cancellation  
Reason: LLM highlighted edge case where a cancelled user re-registers.  
Action: Added FR8; triggered by LLM feedback.

Revision Note 4  
Requirement updated: AC4, AC8 – snapshot clarity and re-registration  
Reason: Ensured feedback and snapshots reflect exact current state.  
Action: Updated AC4 and AC8; triggered by LLM feedback.

Revision Note 5  
Requirement updated: EC4, EC5, EC6 – additional edge cases  
Reason: Addressed waitlisted user cancelling, invalid inputs, and re-registration scenarios.  
Action: Added EC4, EC5, EC6; triggered by LLM feedback.

## Revision Notes

Revision Note 1
Requirement updated: C4 – Feedback for promotion and rejection
Reason: Test `test_cancel_registered_promotes_earliest_waitlisted_fifo` revealed the system must explicitly return or provide feedback when a user is promoted during cancellation to meet Mo’s transparency requirement.
Action: Updated C4 to specify that `cancel()` must return the promoted user's new UserStatus.

Revision Note 2
Requirement updated: C8 – Re-registration after cancellation
Reason: Tests `test_reregister_after_cancel_goes_to_registered_if_space` and `test_reregister_after_waitlist_cancel_goes_to_registered` revealed the need to clarify that users re-registering after cancelation should have no residual state and be correctly placed in registration or waitlist according to current capacity.
Action: Clarified C8 to explicitly handle re-registration with deterministic placement.

Revision Note 3
Requirement updated: C2 – Deterministic waitlist ordering
Reason: Test `test_deterministic_waitlist_order_under_repeated_operations` showed the importance of enforcing deterministic ordering across identical operation sequences.
Action: Strengthened C2 to explicitly state that repeated identical operations must always produce identical system state for both registrations and waitlist positions.

Revision Note 4
Requirement updated: FR13 – Re-registration handling
Reason: Test coverage identified ambiguity in re-registration after a user cancels from the waitlist.
Action: Added explicit requirement: "Users re-registering after cancellation are treated as new registrations and placed according to current capacity, preserving FIFO ordering for the waitlist."
