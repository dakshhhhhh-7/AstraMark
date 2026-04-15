# Token Validation Consolidation Bugfix Design

## Overview

The AstraMark application suffers from inconsistent token validation due to two parallel authentication systems. The `/auth/me` endpoint uses the legacy `get_current_user` function that performs basic JWT decoding without validating the "type" field, while payment endpoints use the modern `get_current_user_dep` function that calls `auth_service.get_current_user` with proper token type validation. This creates a scenario where tokens work with some endpoints but fail with others, leading to "Invalid token type" errors and unpredictable authentication behavior.

The fix involves consolidating all authentication to use the modern `auth_service.get_current_user` method, eliminating the legacy function entirely, and ensuring consistent token validation across all authenticated endpoints.

## Glossary

- **Bug_Condition (C)**: The condition that triggers inconsistent authentication - when the `/auth/me` endpoint uses legacy token validation while other endpoints use modern validation
- **Property (P)**: The desired behavior where all authenticated endpoints use consistent token validation logic through `auth_service.get_current_user`
- **Preservation**: Existing authentication behavior for payment endpoints and token generation that must remain unchanged
- **get_current_user**: The legacy function in `backend/server_enhanced.py` (lines 348-375) that performs basic JWT decoding without type validation
- **get_current_user_dep**: The modern dependency function that calls `auth_service.get_current_user` with proper validation
- **auth_service.get_current_user**: The centralized authentication method in `backend/auth_service.py` that validates token types and handles revocation

## Bug Details

### Bug Condition

The bug manifests when the `/auth/me` endpoint uses the legacy `get_current_user` function while other endpoints use the modern `get_current_user_dep` function. The legacy function performs basic JWT decoding without validating the "type" field, causing inconsistent token validation behavior across the application.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type HTTPRequest with Authorization header
  OUTPUT: boolean
  
  RETURN input.endpoint == "/auth/me"
         AND input.uses_function == "get_current_user" 
         AND other_endpoints.use_function == "get_current_user_dep"
         AND token_validation_logic_differs == true
END FUNCTION
```

### Examples

- **Example 1**: User calls `/auth/me` with valid access token → succeeds with legacy validation (no type check)
- **Example 2**: Same user calls `/payments/subscription` with same token → succeeds with modern validation (includes type check)  
- **Example 3**: User refreshes token and calls `/auth/me` → may fail if token structure changes but legacy function doesn't handle it
- **Edge Case**: Token with missing or incorrect "type" field → works with `/auth/me` but fails with payment endpoints

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Payment endpoints must continue to authenticate successfully using the modern validation system
- Token generation and refresh functionality must remain exactly as implemented
- Error handling and HTTP status codes for invalid tokens must stay consistent

**Scope:**
All authentication behavior that does NOT involve the `/auth/me` endpoint should be completely unaffected by this fix. This includes:
- Payment endpoint authentication (`/payments/*`)
- Token refresh flows (`/auth/refresh`)
- Token generation during login (`/auth/token`)
- Error responses for expired or invalid tokens

## Hypothesized Root Cause

Based on the code analysis, the root cause is architectural inconsistency:

1. **Legacy Function Retention**: The old `get_current_user` function (lines 348-375 in `server_enhanced.py`) was kept when the new authentication service was introduced, creating parallel systems

2. **Incomplete Migration**: The `/auth/me` endpoint was not updated to use the new `get_current_user_dep` dependency when other endpoints were migrated

3. **Token Type Validation Gap**: The legacy function only validates JWT signature and expiration but ignores the "type" field that the modern system requires

4. **Service Isolation**: The legacy function bypasses the centralized `AuthService` class, missing features like token revocation checking and consistent error handling

## Correctness Properties

Property 1: Bug Condition - Consistent Authentication System

_For any_ HTTP request to an authenticated endpoint (including `/auth/me`), the fixed system SHALL use the centralized `auth_service.get_current_user` method for token validation, ensuring consistent authentication logic across all endpoints.

**Validates: Requirements 2.1, 2.2**

Property 2: Preservation - Payment Endpoint Behavior

_For any_ HTTP request to payment endpoints (`/payments/*`) or other endpoints that currently use `get_current_user_dep`, the fixed system SHALL produce exactly the same authentication behavior as before, preserving all existing validation logic and error handling.

**Validates: Requirements 3.1, 3.2, 3.3**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `backend/server_enhanced.py`

**Function**: `/auth/me` endpoint (line 909)

**Specific Changes**:
1. **Update Endpoint Dependency**: Change `Depends(get_current_user)` to `Depends(get_current_user_dep)` in the `/auth/me` endpoint
   - Replace line 909: `async def read_current_user(current_user: UserInDB = Depends(get_current_user)):`
   - With: `async def read_current_user(current_user: UserInDB = Depends(get_current_user_dep)):`

2. **Remove Legacy Function**: Delete the entire `get_current_user` function (lines 348-375)
   - This eliminates the parallel authentication system
   - Forces all endpoints to use the centralized authentication service

3. **Clean Up Imports**: Remove any unused imports related to the legacy authentication
   - Review JWT imports that may only be used by the legacy function
   - Keep imports needed by the modern authentication system

4. **Update Function References**: Ensure no other code references the removed `get_current_user` function
   - Search for any remaining calls to the legacy function
   - Update documentation or comments that reference the old system

5. **Verify Dependencies**: Ensure `get_current_user_dep` is properly imported and available
   - Confirm the dependency function is defined (line 124)
   - Verify it correctly calls `auth_service.get_current_user`

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the inconsistent authentication BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that call both `/auth/me` and payment endpoints with the same token, comparing their validation behavior. Run these tests on the UNFIXED code to observe differences and understand the root cause.

**Test Cases**:
1. **Token Type Validation Test**: Call `/auth/me` and `/payments/subscription` with token missing "type" field (will show different behavior on unfixed code)
2. **Revoked Token Test**: Use a revoked token with both endpoints (may show different handling on unfixed code)
3. **Malformed Token Test**: Use token with invalid structure with both endpoints (will show different error handling on unfixed code)
4. **Valid Token Test**: Use properly formatted token with both endpoints (should work on unfixed code but through different paths)

**Expected Counterexamples**:
- `/auth/me` accepts tokens that payment endpoints reject due to missing type validation
- Different error messages or status codes between endpoints for the same invalid token
- Possible causes: legacy function bypasses centralized validation, missing token type checks, different error handling

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := auth_me_endpoint_fixed(input)
  ASSERT consistent_validation_with_other_endpoints(result)
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT payment_endpoints_original(input) = payment_endpoints_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss  
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for payment endpoints and token flows, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Payment Endpoint Preservation**: Verify all `/payments/*` endpoints continue to work exactly as before with various token types
2. **Token Generation Preservation**: Verify `/auth/token` and `/auth/refresh` continue to generate tokens that work with all endpoints
3. **Error Response Preservation**: Verify invalid tokens continue to produce the same error messages and status codes
4. **Authentication Flow Preservation**: Verify complete login → API call → refresh flows continue working

### Unit Tests

- Test `/auth/me` endpoint with valid tokens (should work after fix)
- Test `/auth/me` endpoint with invalid tokens (should fail consistently with other endpoints)
- Test that legacy `get_current_user` function is completely removed and not callable
- Test that all endpoints now use the centralized authentication service

### Property-Based Tests

- Generate random valid tokens and verify they work consistently across all authenticated endpoints
- Generate random invalid tokens and verify they fail consistently across all authenticated endpoints  
- Test that authentication behavior is identical between `/auth/me` and payment endpoints for the same token

### Integration Tests

- Test complete authentication flow: login → call `/auth/me` → call payment endpoint → refresh → repeat
- Test error scenarios: expired token → call multiple endpoints → verify consistent error responses
- Test token revocation: revoke token → call multiple endpoints → verify all reject the token consistently