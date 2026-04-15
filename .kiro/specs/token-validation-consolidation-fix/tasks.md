# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Inconsistent Authentication System
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the inconsistent authentication between `/auth/me` and payment endpoints
  - **Scoped PBT Approach**: Focus on the concrete failing case where `/auth/me` uses legacy validation while payment endpoints use modern validation
  - Test that `/auth/me` and `/payments/subscription` endpoints handle the same token consistently (from Bug Condition in design)
  - The test assertions should match the Expected Behavior Properties from design - consistent authentication across all endpoints
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found to understand root cause (e.g., "/auth/me accepts token that /payments/subscription rejects")
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 2.1, 2.2_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Payment Endpoint Behavior
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for payment endpoints (`/payments/*`) and other endpoints using `get_current_user_dep`
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Property-based testing generates many test cases for stronger guarantees
  - Test that payment endpoints continue to authenticate successfully with valid tokens
  - Test that invalid tokens continue to be rejected with appropriate error messages
  - Test that token refresh flow continues to work correctly
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 3. Fix for token validation consolidation

  - [x] 3.1 Implement the authentication consolidation fix
    - Update `/auth/me` endpoint to use `get_current_user_dep` instead of `get_current_user`
    - Remove the legacy `get_current_user` function entirely (lines 348-375 in server_enhanced.py)
    - Clean up any unused imports related to legacy authentication
    - Verify no other code references the removed function
    - Ensure all authenticated endpoints now use centralized `auth_service.get_current_user`
    - _Bug_Condition: isBugCondition(input) where input.endpoint == "/auth/me" AND uses legacy validation_
    - _Expected_Behavior: consistent_validation_with_other_endpoints(result) from design_
    - _Preservation: Payment endpoint authentication behavior and token flows from design_
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 3.3, 3.4_

  - [x] 3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Consistent Authentication System
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - Verify `/auth/me` and payment endpoints now use consistent authentication logic
    - _Requirements: Expected Behavior Properties from design_

  - [x] 3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - Payment Endpoint Behavior
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all payment endpoints still authenticate successfully
    - Confirm token refresh flow still works correctly
    - Confirm error handling for invalid tokens remains unchanged

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
  - Verify complete authentication flow: login → `/auth/me` → payment endpoint → refresh → repeat
  - Verify error scenarios produce consistent responses across all endpoints
  - Confirm legacy authentication system is completely removed