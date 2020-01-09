# 956 - Change Password

![User Goal](level_sea.png)

Users need the ability to change their password. This function allows a user
to change their password to another and ensures that it's of sufficient
strength.

## Primary Actor

All users

## Precondition(s)

- User is __logged in to system__.

## Main Success Scenario

1. User decides to change their password.
2. User enters a new password.
3. System verifies that new password meets requirements.
4. System logs that the password has changed, the username, IP address, and
   time.

## Extensions

3a. Password strength too low:

  1. System informs user and displays suggestions to improve.
  2. User enters a different password.

3b. New password is same as current:

  1. System informs user that they must enter a different password.
  2. User enters a different password.

## Technology & Data Variations List

None.

## Related Information

- See the [zxcvbn][1] utility from Dropbox for one method of determining
  password strength.
- See the [zxcvbn-python][2] for the Python port of zxcvbn.


[1]: https://github.com/dropbox/zxcvbn
[2]: https://github.com/dwolfhub/zxcvbn-python
