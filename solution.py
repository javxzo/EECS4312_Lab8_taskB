#Name: Javeria Alam
#Student ID: 218714451

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
        if not isinstance(capacity, int) or capacity < 0:
            raise ValueError("Capacity must be a non-negative integer.")
        self._capacity = capacity
        self._registered: List[str] = []
        self._waitlist: deque[str] = deque()

    def register(self, user_id: str) -> UserStatus:
        if not isinstance(user_id, str) or not user_id:
            raise ValueError("user_id must be a non-empty string.")
        if user_id in self._registered or user_id in self._waitlist:
            raise DuplicateRequest(f"User '{user_id}' is already in the system.")

        if len(self._registered) < self._capacity:
            self._registered.append(user_id)
            return UserStatus("registered")
        else:
            self._waitlist.append(user_id)
            position = len(self._waitlist)
            return UserStatus("waitlisted", position)

    def cancel(self, user_id: str) -> Optional[UserStatus]:
        if not isinstance(user_id, str) or not user_id:
            raise ValueError("user_id must be a non-empty string.")
        if user_id not in self._registered and user_id not in self._waitlist:
            raise NotFound(f"User '{user_id}' not found in the system.")

        promoted_status = None

        if user_id in self._registered:
            self._registered.remove(user_id)
            # Promote earliest waitlisted user if any
            if self._waitlist:
                promoted_user = self._waitlist.popleft()
                self._registered.append(promoted_user)
                promoted_status = UserStatus("registered")
        else:
            # Remove from waitlist
            waitlist_as_list = list(self._waitlist)
            waitlist_as_list.remove(user_id)
            self._waitlist = deque(waitlist_as_list)

        return promoted_status

    def status(self, user_id: str) -> UserStatus:
        if not isinstance(user_id, str) or not user_id:
            raise ValueError("user_id must be a non-empty string.")
        if user_id in self._registered:
            return UserStatus("registered")
        if user_id in self._waitlist:
            position = list(self._waitlist).index(user_id) + 1
            return UserStatus("waitlisted", position)
        return UserStatus("none")

    def snapshot(self) -> dict:
        return {
            "registered": list(self._registered),
            "waitlist": list(self._waitlist),
        }
