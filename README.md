[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]


**This component will set up the following platforms.**

Platform | Description
-- | --
`climate` | Climate entity to control the stove.
`binary_sensor` | Water pump if available on the stove.
`sensor` | Smoke temperature in °C.
`sensor` | Fan Smoke Speed.
`sensor` | Temperature Room 1 / 2 / 3, if available on the stove.
`sensor` | Water temperature if available on the stove.
`sensor` | Power Level.
`sensor` | Speed Fan 1 / 2 / 3 if available on the stove.
`switch` | Stove On / Off.
`switch` | Eco Mode On / Off.
`switch` | Chrono Mode On / Off.


{% if not installed %}
## Installation

1. Click install.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Hottoh".

{% endif %}


## Configuration is done in the UI

<!---->

***

[integration_hottoh]: https://github.com/benlbrm/ha-hottoh-component
[buymecoffee]: https://www.buymeacoffee.com/benlbrm
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/benlbrm/ha-hottoh-component.svg?style=for-the-badge
[commits]: https://github.com/benlbrm/ha-hottoh-component/commits/master
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license]: https://github.com/benlbrm/ha-hottoh-component/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/benlbrm/ha-hottoh-component.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-benlbrm-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/benlbrm/ha-hottoh-component.svg?style=for-the-badge
[releases]: https://github.com/benlbrm/ha-hottoh-component/releases
[user_profile]: https://github.com/benlbrm
