# G4S Alarm support for Home Assistant

### Currently supports
* Arming and disarming alarm
* door/window sensors
* Temperature sensors for all devices with a built in thermomether

### Usage
Install the integration either manually or via HACS by adding this repo as a custom repo

Add the G4S integration by following the config flow in settings/integrations in your Home Assistant instance

Login to your G4S smart alarm account with you username and password

### Notes
Since i can only see G4S devices i my self have, any testers with other hardware would be greatly appreciated

When disabling the alarm a pin is required, this is then checked against all users known pins to validate if the pin is correct.

But since the integration runs via the user account that is logged in all events will seem to come from this user and not the user who the pin pelong to.
