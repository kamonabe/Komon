# Implementation Plan

- [x] 1. Create notification history module with core functionality
  - Create `src/komon/notification_history.py` with save and load functions
  - Implement JSON file I/O with proper error handling
  - Implement 100-item rotation logic
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.1, 3.2_

- [x] 1.1 Write property test for notification persistence
  - **Property 1: Notification persistence**
  - **Validates: Requirements 1.1, 1.2**

- [x] 1.2 Write property test for maximum queue size invariant
  - **Property 2: Maximum queue size invariant**
  - **Validates: Requirements 1.4, 3.1**

- [x] 1.3 Write property test for chronological order preservation
  - **Property 3: Chronological order preservation**
  - **Validates: Requirements 3.2**

- [x] 2. Implement notification formatting and display
  - Create `format_notification()` function for human-readable output
  - Implement timestamp formatting (ISO 8601 to readable format)
  - Design output format with emoji and clear structure
  - _Requirements: 2.3_

- [x] 2.1 Write property test for format completeness
  - **Property 5: Format completeness**
  - **Validates: Requirements 2.3**

- [x] 3. Integrate history saving into existing notification system
  - Modify `send_slack_alert()` in `src/komon/notification.py` to accept metadata
  - Add history saving call with try-except protection
  - Modify `send_email_alert()` similarly
  - Update call sites in `scripts/main.py` to pass metadata
  - _Requirements: 1.1, 4.1, 4.2_

- [x] 3.1 Write unit tests for notification integration
  - Test that Slack notifications still work when history save fails
  - Test that metadata is correctly passed and saved
  - Test backward compatibility with existing code
  - _Requirements: 4.1, 4.2_

- [x] 4. Extend advise command with history display
  - Add `advise_notification_history()` function to `scripts/advise.py`
  - Implement `--history N` command-line argument parsing
  - Add history display section to main advise output
  - Handle missing file and corrupted file cases gracefully
  - _Requirements: 2.1, 2.2, 2.4, 2.5, 4.3_

- [x] 4.1 Write property test for history retrieval with limit
  - **Property 4: History retrieval with limit**
  - **Validates: Requirements 2.2**

- [x] 4.2 Write property test for graceful error handling
  - **Property 6: Graceful error handling**
  - **Validates: Requirements 2.5, 3.3**

- [x] 4.3 Write unit tests for advise command extension
  - Test display with no history
  - Test display with corrupted file
  - Test --history N option
  - _Requirements: 2.1, 2.4, 2.5_

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Update documentation
  - Add usage examples to README.md
  - Document new --history option
  - Update CHANGELOG.md with new feature
  - _Requirements: All_
