# Razorpay Token Validation Fix Design

## Overview

This design addresses a critical JWT token validation bug where refreshed access tokens fail validation with "Invalid token type" error during Razorpay payment flows. The bug occurs because the refresh endpoint in `server_enhanced.py` creates new access tokens without the required `"type": "access"` field, while the authentication service expects this field for proper token validation. This causes payment transactions to fail even with valid, freshly refreshed tokens.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when a refreshed access token is used for API calls but lacks the "type": "access" field
- **Property (P)**: The desired behavior when refreshed tokens are used - they should include "type": "access" and pass validation successfully
- **Preservation**: Existing token generation and validation behavior that must remain unchanged by the fix
- **create_access_token**: The function in `server_enhanced.py` that creates JWT tokens but inconsistently includes the "type" field
- **verify_token**: The function in `auth_service.py` that validates JWT tokens and requires the "type" field to match the expected token type
- **refresh_access_token**: The endpoint in `server_enhanced.py` that creates new access tokens during token refresh

## Bug Details

### Bug Condition

The bug manifests when a user's access token expires during a Razorpay payment flow and gets refreshed. The `refresh_access_token` endpoint creates a new access token without the required `"type": "access"` field, causing subsequent API calls to fail token validation.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type TokenRefreshRequest
  OUTPUT: boolean
  
  RETURN input.isRefreshTokenRequest == true
         AND newAccessToken.payload.type == undefined
         AND subsequentAPICall.requiresAuthentication == true
END FUNCTION
```

### Examples

- **Refresh Token Request**: User's token expires during Razorpay order creation → refresh endpoint creates token without "type": "access" → subsequent order creation fails with "Invalid token type"
- **Payment Flow Interruption**: User initiates payment → token expires → refresh succeeds → payment API call fails due to missing "type" field
- **API Chain Failure**: Any authenticated API call after token refresh fails validation despite having a valid, unexpired JWT
- **Edge Case**: Multiple rapid API calls after refresh all fail until user logs in again to get properly formatted token

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Initial login tokens must continue to include "type": "access" field correctly
- Refresh tokens must continue to include "type": "refresh" field correctly  
- Token validation logic must continue to check for correct "type" field values
- Non-authentication endpoints must continue to work without tokens
- Token expiration and renewal timing must remain unchanged

**Scope:**
All token operations that do NOT involve the refresh endpoint should be completely unaffected by this fix. This includes:
- Initial login token generation
- Refresh token validation and processing
- Token expiration handling
- Non-JWT authentication mechanisms (if any)

## Hypothesized Root Cause

Based on the code analysis, the root cause is a **consistency issue between token generation functions**:

1. **Inconsistent Token Creation**: The `create_access_token` function in `server_enhanced.py` (line 280) creates tokens with only `{"sub": user.email}` data, while the `create_access_token` function in `auth_service.py` (line 49) properly includes `"type": "access"`

2. **Dual Implementation Problem**: There are two different `create_access_token` implementations:
   - `server_enhanced.py`: Simple implementation without "type" field
   - `auth_service.py`: Complete implementation with "type": "access" field

3. **Endpoint Using Wrong Function**: The refresh endpoint uses the incomplete `create_access_token` from `server_enhanced.py` instead of the proper one from `auth_service.py`

4. **Validation Mismatch**: The `verify_token` function in `auth_service.py` (line 78) strictly validates `payload.get("type") != token_type` but the refresh endpoint creates tokens without this field

## Correctness Properties

Property 1: Bug Condition - Refreshed Access Tokens Include Type Field

_For any_ token refresh request where a valid refresh token is provided, the new access token SHALL include `"type": "access"` in its JWT payload, enabling successful validation by the authentication service.

**Validates: Requirements 2.2, 2.3**

Property 2: Preservation - Non-Refresh Token Generation Unchanged

_For any_ token generation that is NOT through the refresh endpoint (initial login, refresh token creation), the token generation SHALL produce exactly the same tokens as before the fix, preserving all existing authentication flows.

**Validates: Requirements 3.1, 3.2, 3.3**

## Fix Implementation

### Changes Required

The fix involves updating the refresh endpoint to use the proper token creation function that includes the "type" field.

**File**: `backend/server_enhanced.py`

**Function**: `refresh_access_token` (line 849)

**Specific Changes**:
1. **Import Proper Function**: Import `create_access_token` from `auth_service.py` instead of using the local incomplete version
   - Add: `from auth_service import create_access_token as create_proper_access_token`

2. **Update Token Creation Call**: Replace the token creation call to use the proper function
   - Replace: `create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)`
   - With: `create_proper_access_token(data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires)`

3. **Ensure Consistent Data Structure**: Make sure the token data includes both email and user_id for consistency
   - The `auth_service.py` version expects both `sub` (email) and `user_id` fields

4. **Remove Duplicate Function**: Consider removing or renaming the incomplete `create_access_token` in `server_enhanced.py` to prevent future confusion

5. **Update Function Signature**: Ensure the refresh endpoint passes the correct parameters expected by the proper token creation function

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm that refreshed tokens lack the "type" field and fail validation.

**Test Plan**: Write tests that simulate the complete token refresh flow and examine the JWT payload structure. Run these tests on the UNFIXED code to observe the missing "type" field and subsequent validation failures.

**Test Cases**:
1. **Token Refresh Payload Test**: Decode refreshed access token JWT and verify "type" field is missing (will fail on unfixed code)
2. **Validation Failure Test**: Use refreshed token for authenticated API call and observe "Invalid token type" error (will fail on unfixed code)  
3. **Payment Flow Test**: Simulate expired token during Razorpay order creation, refresh, then retry order creation (will fail on unfixed code)
4. **Multiple API Calls Test**: Refresh token then make several authenticated API calls in sequence (will fail on unfixed code)

**Expected Counterexamples**:
- JWT payload missing `"type": "access"` field in refreshed tokens
- Authentication service rejecting valid refreshed tokens with "Invalid token type"
- Payment flows failing after successful token refresh

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := refresh_access_token_fixed(input)
  ASSERT result.access_token.payload.type == "access"
  ASSERT verify_token(result.access_token, "access") succeeds
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT login_token_generation_original(input) = login_token_generation_fixed(input)
  ASSERT refresh_token_generation_original(input) = refresh_token_generation_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss  
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Capture the behavior of login token generation and refresh token generation on UNFIXED code, then write property-based tests to verify this behavior continues after the fix.

**Test Cases**:
1. **Login Token Preservation**: Verify initial login tokens have identical structure and validation behavior
2. **Refresh Token Preservation**: Verify refresh tokens themselves (not access tokens) remain unchanged
3. **Token Validation Preservation**: Verify validation logic continues to work for all existing token types
4. **Expiration Handling Preservation**: Verify token expiration and timing behavior remains unchanged

### Unit Tests

- Test JWT payload structure for refreshed access tokens includes "type": "access"
- Test token validation succeeds for refreshed tokens
- Test refresh endpoint returns properly formatted tokens
- Test edge cases (expired refresh tokens, invalid refresh tokens)

### Property-Based Tests

- Generate random user data and verify refreshed tokens always include "type": "access"
- Generate random token refresh scenarios and verify validation always succeeds
- Test that all non-refresh token operations produce identical results before and after fix

### Integration Tests

- Test complete payment flow with token refresh (Razorpay order creation after token expiry)
- Test multiple authenticated API calls after token refresh
- Test token refresh during various user workflows (not just payments)
- Test that authentication service properly validates all token types after fix