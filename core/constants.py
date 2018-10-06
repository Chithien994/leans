from core.enums import StatusCode

MESSAGES = {}
MESSAGES[StatusCode.USERNAME_IS_INVALID] 		= 'The username is invalid'
MESSAGES[StatusCode.PHONE_NUMBER_IS_INVALID] 	= 'The phone number is invalid'
MESSAGES[StatusCode.PASSWORD_IS_INVALID] 		= 'The password is invalid!'
MESSAGES[StatusCode.EMAIL_ADDRESS_IS_EMPTY] 	= 'The email address is empty!'
MESSAGES[StatusCode.EMAIL_ADDRESS_IS_INVALID] 	= 'The email address is invalid!'
MESSAGES[StatusCode.EMAIL_ADDRESS_IS_EXISTS] 	= 'This email already exists in our system!'
MESSAGES[StatusCode.FIRST_NAME_IS_EMPTY] 		= 'The first name is empty!'
MESSAGES[StatusCode.LAST_NAME_IS_EMPTY] 		= 'The last name is empty!'
MESSAGES[StatusCode.USER_ID_IS_INVALID] 		= 'The user id is invalid!'
MESSAGES[StatusCode.NEW_PASSWORD_IS_INVALID]	= 'The new password is invalid!'
MESSAGES[StatusCode.ACCESS_TOKEN_FB_IS_INVALID] = 'Invalid data!'
MESSAGES[StatusCode.OLD_PASSWORD_IS_INVALID] 	= 'The old password is invalid!'
