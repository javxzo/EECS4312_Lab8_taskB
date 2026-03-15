## 1. Problem Understanding - Describe the problem your system solves.

System purpose:
Manage event registration with a fixed capacity, automatically handle a FIFO waitlist, support cancellations, prevent duplicates, and provide clear user status feedback while maintaining deterministic and predictable behavior.

Inputs to the system:
- capacity: int (≥0)
- user_id: non-empty string
- Operations: register(user_id), cancel(user_id), status(user_id), snapshot()

Outputs produced by the system:
- UserStatus(state: "registered"/"waitlisted"/"none", position: Optional[int])
- Snapshot of registered and waitlisted users
- Exception messages for duplicate registration or not found users

Primary goal of the system:
Ensure reliable, conflict-free registration management with clear, predictable behavior and transparency for users, including automated promotion from waitlist when appropriate.

## 2. Assumptions - List assumptions about the environment, users, or inputs.

A1: User IDs are unique non-empty strings.
A2: Capacity is a non-negative integer.
A3: System is single-threaded; simultaneous operations are processed in order.
A4: Users may cancel at any time but cannot be in multiple states simultaneously.
A5: Notifications or feedback are only provided for essential changes.
A6: Waitlist ordering is preserved FIFO; earliest registered waitlisted user is promoted first.

## 3. Functional Requirements - Describe the main behaviors the system must perform.

FR1: The system shall register users up to the event capacity. (Derived from original spec)
FR2: The system shall place additional users into a FIFO waitlist when capacity is full. (Derived from original spec)
FR3: The system shall automatically promote the earliest waitlisted user when a registered user cancels. (Derived from C1 – Jane, behavior)
FR4: The system shall prevent duplicate registrations for the same user ID. (Derived from C3 – Jane, behavior)
FR5: The system shall provide deterministic ordering and promotion for all operations. (Derived from C2 – Mo, pain point)
FR6: The system shall provide clear feedback and status, including waitlist position, to users. (Derived from C4, C7, C8 – Mo/Jane, need/behavior)

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

## 5. Acceptance Criteria - Acceptance criteria define how system behavior will be verified.

AC1: Given a user registers when event capacity is not reached, when register(user_id) is called, then the user is added to registered list.
Linked Constraint ID(s): C1

AC2: Given a registered user cancels, when cancel(user_id) is called, then the earliest waitlisted user is promoted to registered.
Linked Constraint ID(s): C1, C2

AC3: Given a user attempts to register twice, when register(user_id) is called, then a DuplicateRequest exception is raised.
Linked Constraint ID(s): C3

AC4: Given a user queries status, when status(user_id) is called, then the system returns UserStatus with correct state and position.
Linked Constraint ID(s): C4

AC5: Given multiple users on the waitlist, when a registered user cancels, then promotions follow strict FIFO order.
Linked Constraint ID(s): C2, C5

AC6: Given capacity=0 or multiple cancellations, when users register or cancel, then the system handles all operations gracefully, adding to waitlist as needed.
Linked Constraint ID(s): C6

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

## 7. Traceability - Link functional requirements to constraints and acceptance criteria. FR → C → AC mapping

FR1 → C1 → AC1  
FR2 → C5 → AC5  
FR3 → C1 → AC2  
FR4 → C3 → AC3  
FR5 → C2 → AC5  
FR6 → C4, C7, C8 → AC4  

## Revision Notes
