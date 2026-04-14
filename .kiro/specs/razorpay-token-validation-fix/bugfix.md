# Bugfix Requirements Document

## Introduction

This document addresses a critical authentication bug in the Razorpay payment flow where token validation fails with "Invalid token type" error after successful token refresh. The bug prevents users from completing payment transactions even when they have valid, freshly refreshed authentication tokens, causing a complete breakdown of the payment functionality.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a user's access token expires during Razorpay order creation THEN the system correctly detects the expired token and initiates a refresh

1.2 WHEN the token refresh endpoint successfully creates a new access token THEN the new access token is missing the required "type": "access" field in its JWT payload

1.3 WHEN the refreshed access token is used for subsequent API calls THEN the token validation logic fails with "Invalid token type" error because it expects the "type" field to be "access"

1.4 WHEN token validation fails after refresh THEN the user receives a 401 Unauthorized error and cannot complete the payment flow

### Expected Behavior (Correct)

2.1 WHEN a user's access token expires during Razorpay order creation THEN the system SHALL detect the expired token and initiate a refresh

2.2 WHEN the token refresh endpoint creates a new access token THEN the new access token SHALL include "type": "access" in its JWT payload

2.3 WHEN the refreshed access token is used for subsequent API calls THEN the token validation logic SHALL successfully validate the token and allow the request to proceed

2.4 WHEN token validation succeeds after refresh THEN the user SHALL be able to complete the Razorpay order creation and payment flow without authentication errors

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a user logs in initially THEN the system SHALL CONTINUE TO create access tokens with the correct "type": "access" field

3.2 WHEN a user uses a non-expired access token THEN the system SHALL CONTINUE TO validate the token successfully

3.3 WHEN refresh tokens are validated THEN the system SHALL CONTINUE TO check for "type": "refresh" field correctly

3.4 WHEN invalid or expired tokens are presented THEN the system SHALL CONTINUE TO reject them with appropriate error messages

3.5 WHEN users access non-payment endpoints with valid tokens THEN the system SHALL CONTINUE TO authenticate them successfully