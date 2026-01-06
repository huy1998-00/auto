"""
Unit tests for TableTracker (Epic 1).

Tests table state tracking, round history, and learning phase.
"""

import pytest
from src.automation.orchestration.table_tracker import (
    TableTracker,
    TableStatus,
    TableState,
    RoundResult,
)


class TestTableTracker:
    """Test TableTracker class."""

    def test_initialization(self):
        """Test tracker initialization."""
        tracker = TableTracker(
            table_id=1,
            patterns="BBP-P;BPB-B",
        )
        
        assert tracker.table_id == 1
        assert tracker.state.status == TableStatus.LEARNING
        assert tracker.state.learning_phase is True
        assert tracker.state.rounds_watched == 0
        assert len(tracker.state.round_history) == 0

    def test_learning_phase_initial(self):
        """Test learning phase starts as True."""
        tracker = TableTracker(table_id=1)
        assert tracker.state.learning_phase is True
        assert tracker.state.status == TableStatus.LEARNING

    def test_add_round_history(self):
        """Test adding rounds to history."""
        tracker = TableTracker(table_id=1)
        
        tracker.add_round("B")
        assert len(tracker.state.round_history) == 1
        assert tracker.state.round_history[0] == "B"
        
        tracker.add_round("P")
        assert len(tracker.state.round_history) == 2
        
        tracker.add_round("B")
        assert len(tracker.state.round_history) == 3

    def test_round_history_max_3(self):
        """Test round history keeps only last 3 rounds."""
        tracker = TableTracker(table_id=1)
        
        tracker.add_round("B")
        tracker.add_round("P")
        tracker.add_round("B")
        tracker.add_round("P")  # Should remove first "B"
        
        assert len(tracker.state.round_history) == 3
        assert tracker.state.round_history == ["P", "B", "P"]

    def test_learning_phase_completion(self):
        """Test learning phase completes after 3 rounds."""
        tracker = TableTracker(table_id=1)
        
        assert tracker.state.learning_phase is True
        
        tracker.add_round("B")
        tracker.add_round("P")
        tracker.add_round("B")
        
        assert tracker.state.learning_phase is False
        assert tracker.state.status == TableStatus.ACTIVE
        assert tracker.state.rounds_watched == 3

    def test_get_last_3_rounds(self):
        """Test getting last 3 rounds as string."""
        tracker = TableTracker(table_id=1)
        
        # Less than 3 rounds
        tracker.add_round("B")
        assert tracker.get_last_3_rounds() == "B"
        
        tracker.add_round("P")
        assert tracker.get_last_3_rounds() == "BP"
        
        # Exactly 3 rounds
        tracker.add_round("B")
        assert tracker.get_last_3_rounds() == "BPB"

    def test_update_scores(self):
        """Test updating scores."""
        tracker = TableTracker(table_id=1)
        
        tracker.update_scores(blue_score=3, red_score=2)
        assert tracker.state.blue_score == 3
        assert tracker.state.red_score == 2
        assert tracker.state.previous_blue_score == 0
        assert tracker.state.previous_red_score == 0
        
        # Update again
        tracker.update_scores(blue_score=4, red_score=2)
        assert tracker.state.blue_score == 4
        assert tracker.state.previous_blue_score == 3
        assert tracker.state.previous_red_score == 2

    def test_detect_winner_score_increase(self):
        """Test detecting winner from score increase."""
        tracker = TableTracker(table_id=1)
        
        tracker.update_scores(blue_score=0, red_score=0)
        tracker.update_scores(blue_score=1, red_score=0)
        
        winner = tracker.detect_winner()
        assert winner == "P"  # Blue score increased -> Blue (P) won
        
        tracker.update_scores(blue_score=1, red_score=1)
        winner = tracker.detect_winner()
        assert winner == "B"  # Red score increased -> Red (B) won

    def test_detect_winner_no_change(self):
        """Test detecting winner when scores don't change."""
        tracker = TableTracker(table_id=1)
        
        tracker.update_scores(blue_score=1, red_score=1)
        tracker.update_scores(blue_score=1, red_score=1)
        
        winner = tracker.detect_winner()
        assert winner is None

    def test_set_patterns(self):
        """Test setting patterns."""
        tracker = TableTracker(table_id=1)
        
        tracker.set_patterns("BBP-P;BPB-B")
        assert tracker.state.patterns == "BBP-P;BPB-B"

    def test_make_decision_learning_phase(self):
        """Test decision making during learning phase."""
        tracker = TableTracker(table_id=1, patterns="BBP-P")
        
        # In learning phase, should not make decisions
        tracker.add_round("B")
        decision = tracker.make_decision()
        assert decision is None
        
        tracker.add_round("P")
        tracker.add_round("B")
        # Still learning, no decision
        decision = tracker.make_decision()
        assert decision is None

    def test_make_decision_after_learning(self):
        """Test decision making after learning phase."""
        tracker = TableTracker(table_id=1, patterns="BBP-P")
        
        # Complete learning phase
        tracker.add_round("B")
        tracker.add_round("B")
        tracker.add_round("P")
        
        # Now should make decision
        decision = tracker.make_decision()
        assert decision == "blue"  # BBP matches, decision is P -> blue

    def test_make_decision_no_match(self):
        """Test decision when no pattern matches."""
        tracker = TableTracker(table_id=1, patterns="BBB-B")
        
        # Complete learning
        tracker.add_round("B")
        tracker.add_round("B")
        tracker.add_round("P")  # History: BBP, but pattern is BBB
        
        decision = tracker.make_decision()
        assert decision is None  # No match

    def test_complete_round(self):
        """Test completing a round."""
        tracker = TableTracker(table_id=1, patterns="BBP-P")
        
        # Complete learning
        tracker.add_round("B")
        tracker.add_round("B")
        tracker.add_round("P")
        
        tracker.update_scores(blue_score=1, red_score=0)
        tracker.update_timer(15)
        
        round_result = tracker.complete_round()
        
        assert round_result is not None
        assert round_result.round_number == 1
        assert round_result.blue_score == 1
        assert round_result.red_score == 0
        assert tracker.state.current_round_number == 1

    def test_pause_resume(self):
        """Test pausing and resuming table."""
        tracker = TableTracker(table_id=1)
        
        assert tracker.state.status == TableStatus.LEARNING
        
        tracker.pause()
        assert tracker.state.status == TableStatus.PAUSED
        
        tracker.resume()
        assert tracker.state.status == TableStatus.LEARNING

    def test_stop(self):
        """Test stopping table."""
        tracker = TableTracker(table_id=1)
        
        tracker.stop()
        assert tracker.state.status == TableStatus.STOPPED

    def test_get_state_dict(self):
        """Test getting state as dictionary."""
        tracker = TableTracker(table_id=1)
        
        state_dict = tracker.get_state_dict()
        
        assert isinstance(state_dict, dict)
        assert state_dict["table_id"] == 1
        assert "status" in state_dict
        assert "round_history" in state_dict
