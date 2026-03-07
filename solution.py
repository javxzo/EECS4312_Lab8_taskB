# Student Name: Javeria Alam
# Student ID: 218714451

from dataclasses import dataclass
from collections import deque
from typing import List, Optional


class DuplicateRequest(Exception):
    """Raised if a user tries to register but is already registered or waitlisted."""
    pass


class NotFound(Exception):
    """Raised if a user cannot be found for cancellation."""
    pass


@dataclass(frozen=True)
class UserStatus:
    """
    state:
      - "registered"
      - "waitlisted"
      - "none"
    position: 1-based waitlist position if waitlisted; otherwise None
    """
    state: str
    position: Optional[int] = None


class EventRegistration:
    """
    Manages registration for a single event with a fixed capacity and FIFO waitlist.

    Invariants:
      - Registered users never exceed capacity.
      - Waitlist ordering is strictly FIFO.
      - A user cannot appear more than once in the system.
      - A user cannot be both registered and waitlisted simultaneously.
      - System state remains consistent after every operation.
    """

    def __init__(self, capacity: int) -> None:
        """
        Args:
            capacity: maximum number of registered users (>= 0)
        """
        # C1, C9: capacity must be a non-negative integer
        if not isinstance(capacity, int) or capacity < 0:
            raise ValueError("Capacity must be a non-negative integer.")

        self._capacity = capacity

        # Maintains insertion order for registered users
        self._registered: List[str] = []

        # deque ensures O(1) FIFO promotion from the front
        # C2: waitlist ordering must remain FIFO
        self._waitlist: deque[str] = deque()

    def register(self, user_id: str) -> UserStatus:
        """
        Register a user:
          - If capacity available -> registered
          - Else -> waitlisted (FIFO)

        Raises:
            DuplicateRequest: if user already exists (registered or waitlisted)
            ValueError: if user_id is not a non-empty string
        """
        # C10: user_id must be a non-empty string
        if not isinstance(user_id, str) or not user_id:
            raise ValueError("user_id must be a non-empty string.")

        # C3, C4: user cannot appear more than once or in multiple states
        if user_id in self._registered or user_id in self._waitlist:
            raise DuplicateRequest(f"User '{user_id}' is already in the system.")

        # C1: register only if under capacity
        if len(self._registered) < self._capacity:
            self._registered.append(user_id)
            return UserStatus("registered")
        else:
            # C2, C7: append to back of FIFO waitlist, position is 1-based
            self._waitlist.append(user_id)
            position = len(self._waitlist)
            return UserStatus("waitlisted", position)

    def cancel(self, user_id: str) -> None:
        """
        Cancel a user:
          - If registered -> remove and promote earliest waitlisted user (if any)
          - If waitlisted -> remove from waitlist, update positions implicitly
          - If not found -> raise NotFound

        Raises:
            NotFound: if user does not exist in the system
        """
        # C6: canceling a non-existent user raises NotFound
        if user_id not in self._registered and user_id not in self._waitlist:
            raise NotFound(f"User '{user_id}' not found in the system.")

        if user_id in self._registered:
            # Remove from registered list
            self._registered.remove(user_id)

            # C2, C5: promote earliest waitlisted user if waitlist is non-empty
            if self._waitlist:
                promoted = self._waitlist.popleft()
                self._registered.append(promoted)
        else:
            # C2: remove from waitlist; deque reordering preserves FIFO
            waitlist_as_list = list(self._waitlist)
            waitlist_as_list.remove(user_id)
            self._waitlist = deque(waitlist_as_list)

    def status(self, user_id: str) -> UserStatus:
        """
        Return status of a user:
          - "registered"
          - "waitlisted" with 1-based position
          - "none" if not in system

        C5, C7: consistent state and 1-based indexing
        """
        if user_id in self._registered:
            return UserStatus("registered")

        if user_id in self._waitlist:
            # C7: 1-based position
            position = list(self._waitlist).index(user_id) + 1
            return UserStatus("waitlisted", position)

        return UserStatus("none")

    def snapshot(self) -> dict:
        """
        Returns a deterministic snapshot of internal state.

        Returns:
            dict with keys:
              "registered": ordered list of registered user_ids
              "waitlist":   ordered list of waitlisted user_ids (FIFO order)
        """
        return {
            "registered": list(self._registered),
            "waitlist": list(self._waitlist),
        }
