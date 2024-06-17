# 103 - Add or Update Event

Organizers need the ability to add, update, and delete scheduled events for
their community.

## Primary Actor

Organizer

## Precondition(s)

- User is [logged in to system][1].
- User has the authority for this usecase.

## Main Success Scenario

1. User decides to add a new event.
2. User enters the event name, description, date, time, and duration.
3. System verifies event does not conflict with existing events.
4. System posts the event.
5. System logs the event posting, username, and time.

## Extensions

1a. Update event:

  1. User decides to update an event.
  2. User selects the event to update.
  3. User updates the event name, description, date, time, and / or
     duration.
  4. User enters a reason for the update.
  5. System verifies event does not conflict with existing events.
  6. System updates the event.
  7. System logs the event update, reason, username, and time.

1b. Delete event:
  1. User decides to delete an event.
  2. User selects the event to delete.
  3. User enters a reason for the deletion.
  4. System marks the event as deleted and removes it from the schedule.
  5. System logs the event deletion, reason, username, and time.

2a. Reason to add event provided:
  1. User enters a reason why this event was added.

5a. Reason entered:
  1. System also logs the reason for this new event.

## Technology & Data Variations List

None.

## Related Information

None.


[1]: 101_login_to_system.md
