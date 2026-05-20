"""
users/utils/constants.py

Centralized constants for the auth module.
"""

# Token TTLs (in seconds)
EMAIL_VERIFICATION_TOKEN_TTL = 60 * 60 * 24       # 24 hours
PASSWORD_RESET_TOKEN_TTL     = 60 * 60             # 1 hour

# Redis key prefixes
REDIS_EMAIL_VERIFY_PREFIX   = "vidai:email_verify:"
REDIS_PASSWORD_RESET_PREFIX = "vidai:password_reset:"

# Email subjects
EMAIL_SUBJECT_VERIFY   = "Verify your VidAI Studio email"
EMAIL_SUBJECT_RESET    = "Reset your VidAI Studio password"

# Social auth
GOOGLE_TOKEN_INFO_URL  = "https://oauth2.googleapis.com/tokeninfo"
APPLE_KEYS_URL         = "https://appleid.apple.com/auth/keys"

# Error messages
ERR_DUPLICATE_EMAIL        = "An account with this email already exists."
ERR_INVALID_CREDENTIALS    = "Invalid email or password."
ERR_ACCOUNT_INACTIVE       = "This account has been deactivated."
ERR_EMAIL_NOT_VERIFIED     = "Please verify your email before logging in."
ERR_TERMS_NOT_ACCEPTED     = "You must accept the Terms of Service to register."
ERR_INVALID_RESET_TOKEN    = "Invalid or expired password reset token."
ERR_INVALID_VERIFY_TOKEN   = "Invalid or expired email verification token."
ERR_PASSWORDS_DONT_MATCH   = "Passwords do not match."
