# Bugfix Requirements Document

## Introduction

The AstraMark application has a persistent token validation error caused by two different authentication systems running in parallel. The old authentication system (`get_current_user`) performs direct JWT decoding without validating the "type" field, while the new system (`get_current_user_dep` → `auth_service.get_current_user`) properly validates token types. This inconsistency causes "Invalid token type" errors when endpoints using different authentication systems are accessed with the same token, creating unpredictable authentication failures across the application.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a valid access token is used with the `/auth/me` endpoint THEN the system fails with "Invalid token type" error because the old `get_current_user` function doesn't validate the "type" field

1.2 WHEN the same valid access token is used with payment endpoints THEN the system works correctly because they use the new `get_current_user_dep` function

1.3 WHEN tokens are refreshed using the refresh token endpoint THEN subsequent calls to `/auth/me` fail while payment endpoints continue to work, creating inconsistent authentication behavior

1.4 WHEN developers test authentication flows THEN they encounter unpredictable failures depending on which endpoints they access, making the system unreliable

### Expected Behavior (Correct)

2.1 WHEN a valid access token is used with the `/auth/me` endpoint THEN the system SHALL authenticate successfully and return user information

2.2 WHEN the same valid access token is used with any authenticated endpoint THEN the system SHALL use consistent token validation logic across all endpoints

2.3 WHEN tokens are refreshed using the refresh token endpoint THEN subsequent calls to any authenticated endpoint SHALL work consistently

2.4 WHEN developers test authentication flows THEN the system SHALL provide predictable and consistent authentication behavior across all endpoints

### Unchanged Behavior (Regression Prevention)

3.1 WHEN valid access tokens are used with payment endpoints THEN the system SHALL CONTINUE TO authenticate successfully as they currently do

3.2 WHEN invalid or expired tokens are provided THEN the system SHALL CONTINUE TO reject them with appropriate error messages

3.3 WHEN the refresh token flow is used THEN the system SHALL CONTINUE TO generate new access tokens that work with all endpoints

3.4 WHEN users access endpoints that don't require authentication THEN the system SHALL CONTINUE TO allow access without tokens