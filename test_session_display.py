"""
Test for session display update issue
"""

import pytest
from dataclasses import asdict
from datetime import datetime
from models import Session, Message


class MockReactiveValue:
    """Mock Solara's reactive value to test change detection"""

    def __init__(self, initial_value):
        self._value = initial_value
        self.change_count = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        # Solara detects changes by object identity
        if new_value is not self._value:
            self.change_count += 1
        self._value = new_value


def test_session_update_mutates_then_reassigns():
    """
    Test simulating the bug: when we mutate messages in place,
    then reassign with asdict, Solara should detect the change.

    This tests the current implementation in app.py lines 293-319.
    The bug: we mutate the session's messages, but the reactive
    framework might not see the change until we reassign.
    """
    # Create initial session
    initial_session = Session(
        topic_name="Test Topic",
        messages=[
            {
                "role": "tutor",
                "content": "Initial message",
                "canvas_image": None,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ],
        created_at=datetime.now().isoformat(),
        status="active",
        session_id="test_session_1",
    )

    # Simulate reactive value
    current_session = MockReactiveValue(initial_session)
    assert current_session.change_count == 0

    # Simulate what happens in submit_answer()
    # Step 1: Mutate the existing session's messages (lines 293, 313)
    student_msg = Message(
        role="student",
        content="Student answer",
        canvas_image=None,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    current_session.value.messages.append(asdict(student_msg))

    # At this point, we've mutated the session, but haven't reassigned
    # Solara won't detect this change yet!
    assert current_session.change_count == 0, "No reassignment = no change detected"

    tutor_msg = Message(
        role="tutor",
        content="Tutor feedback",
        canvas_image=None,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    current_session.value.messages.append(asdict(tutor_msg))

    # Still no change detected
    assert current_session.change_count == 0, "Still no reassignment = no change"

    # Step 2: Try to force re-render (line 319)
    current_session.value = Session(**asdict(current_session.value))

    # Now a change should be detected
    assert current_session.change_count == 1, "Reassignment should trigger change"
    assert len(current_session.value.messages) == 3

    # BUT: There's a potential issue - between lines 293 and 319,
    # the UI might try to render with the mutated session!
    # This is a race condition that could cause display issues.


def test_proper_session_update_pattern():
    """
    Test the CORRECT way to update a session - create entirely new object
    with a new messages list WITHOUT mutating the original.
    """
    # Create initial session
    initial_session = Session(
        topic_name="Test Topic",
        messages=[
            {
                "role": "tutor",
                "content": "Initial message",
                "canvas_image": None,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ],
        created_at=datetime.now().isoformat(),
        status="active",
        session_id="test_session_2",
    )

    # Simulate reactive value
    current_session = MockReactiveValue(initial_session)
    assert current_session.change_count == 0

    # Create new messages (CORRECT WAY - no mutation)
    student_msg = Message(
        role="student",
        content="Student answer",
        canvas_image=None,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    tutor_msg = Message(
        role="tutor",
        content="Tutor feedback",
        canvas_image=None,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    # Create new messages list with additional messages (no mutation!)
    new_messages = current_session.value.messages + [
        asdict(student_msg),
        asdict(tutor_msg),
    ]

    # Create completely new session with new messages list
    updated_session = Session(
        topic_name=current_session.value.topic_name,
        messages=new_messages,
        created_at=current_session.value.created_at,
        status=current_session.value.status,
        session_id=current_session.value.session_id,
    )

    # Assign the new session - this triggers change detection immediately
    current_session.value = updated_session

    # Change detected on the single assignment
    assert current_session.change_count == 1, "Single reassignment triggers change"

    # Verify the messages are there
    assert len(current_session.value.messages) == 3, "Should have 3 messages total"
    assert current_session.value.messages[1]["role"] == "student"
    assert current_session.value.messages[2]["role"] == "tutor"

    # Verify original session wasn't mutated
    assert len(initial_session.messages) == 1, "Original session unchanged"


@pytest.mark.xfail(
    reason="Demonstrates the bug that was fixed - mutating then reassigning doesn't work properly"
)
def test_session_update_without_ui_refresh_bug():
    """
    Test demonstrating the BUG that existed in old app.py code:
    Student message was added (outside if topic block),
    but UI refresh was inside the if topic block.
    If topic is None or AI fails, UI wouldn't update!

    THIS TEST FAILS, demonstrating the original bug.
    Marked as xfail to document the bug without breaking the test suite.
    """
    # Create initial session
    initial_session = Session(
        topic_name="Test Topic",
        messages=[
            {
                "role": "tutor",
                "content": "Initial message",
                "canvas_image": None,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ],
        created_at=datetime.now().isoformat(),
        status="active",
        session_id="test_session_3",
    )

    # Simulate reactive value
    current_session = MockReactiveValue(initial_session)
    assert current_session.change_count == 0

    # Simulate submit_answer() line 293 - add student message
    student_msg = Message(
        role="student",
        content="Student answer",
        canvas_image=None,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    current_session.value.messages.append(asdict(student_msg))

    # At this point, no UI update has been triggered
    assert current_session.change_count == 0, "No UI update yet"

    # Now simulate topic loading fails or topic is None (line 297-299)
    topic = None  # This simulates the if topic check failing

    if topic:
        # Lines 313-319 would execute here, including the UI update
        # But they DON'T execute if topic is None!
        pass

    # BUG: Student message was added, but UI was never updated!
    # The UI is showing old messages, but the session has the new message
    assert len(current_session.value.messages) == 2, "Message was added to session"

    # This assertion will FAIL, demonstrating the bug:
    # We EXPECT the UI to update (change_count > 0), but it doesn't (change_count == 0)
    assert (
        current_session.change_count > 0
    ), "BUG: UI should have updated when message was added, but it didn't!"

    # This is the bug the user is experiencing:
    # - Session is updated (messages has the new message)
    # - Display is NOT updated (no change detection triggered)


def test_fixed_session_update_with_immediate_ui_refresh():
    """
    Test the FIXED version: using immutable updates to trigger UI refresh immediately.
    This simulates the corrected code in app.py.

    THIS TEST SHOULD PASS, demonstrating the fix works.
    """
    # Create initial session
    initial_session = Session(
        topic_name="Test Topic",
        messages=[
            {
                "role": "tutor",
                "content": "Initial message",
                "canvas_image": None,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ],
        created_at=datetime.now().isoformat(),
        status="active",
        session_id="test_session_4",
    )

    # Simulate reactive value
    current_session = MockReactiveValue(initial_session)
    assert current_session.change_count == 0

    # FIXED: Use immutable update - create student message
    student_msg = Message(
        role="student",
        content="Student answer",
        canvas_image=None,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    # Create new messages list (no mutation!)
    new_messages = current_session.value.messages + [asdict(student_msg)]

    # Create new session and assign immediately (triggers UI update)
    current_session.value = Session(
        topic_name=current_session.value.topic_name,
        messages=new_messages,
        created_at=current_session.value.created_at,
        status=current_session.value.status,
        session_id=current_session.value.session_id,
    )

    # UI should update immediately after adding student message!
    assert current_session.change_count == 1, "UI updated when student message added"
    assert len(current_session.value.messages) == 2, "Student message is in session"

    # Now simulate AI feedback (even if topic is None, UI already updated)
    topic = None  # Even if this fails...

    if topic:
        # This won't execute, but that's OK - student message is already visible!
        pass

    # Student message is visible because UI was updated immediately
    assert current_session.change_count == 1, "UI was updated"
    assert current_session.value.messages[1]["role"] == "student"

    # This is the fix:
    # - Session is updated (messages has the new message)
    # - Display IS updated (change detection triggered immediately)
    # - Even if AI fails, student can see their message!
