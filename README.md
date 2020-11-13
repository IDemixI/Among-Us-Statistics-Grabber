![Among Us: Statistics Grabber](https://i.imgur.com/R4yeJ8V.png)

# Among Us: Statistics Grabber

A script written in Python to extract and upload your Among Us player statistics to a REST endpoint so you can share with your friends and build a leaderboard or analyse data.

The current leaderboard can be found at: ![http://demix-server.ddns.net:2281/amongus](http://demix-server.ddns.net:2281/amongus)

Among Us, Statistics, Data Analytics, Leaderboard, Stats

[![GitHub Issues](https://img.shields.io/github/issues/IDemixI/Among-Us-Statistics-Grabber)](https://github.com/IDemixI/Among-Us-Statistics-Grabber/issues)
![GitHub Licence](https://img.shields.io/github/license/IDemixI/Among-Us-Statistics-Grabber)
![GitHub Releases](https://img.shields.io/github/downloads/IDemixI/Among-Us-Statistics-Grabber/latest/total)
![GitHub last commit](https://img.shields.io/github/last-commit/IDemixI/Among-Us-Statistics-Grabber)
[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-blue)](http://paypal.me/demix)

---

## Table of Contents

- [Installation](#installation)
- [Features](#features)
- [JSON Schema](#json-schema)
- [Contributing](#contributing)
- [Contributors](#contributors)
- [FAQ](#faq)
- [License](#license)

---

## Installation

### Executable

- Simply download the latest release and run it once to perform the setup. After this, the program will run whenever you launch Among Us via Steam.

### Python

- Download the Python Script, ensure you have all of the required packages, then run the script from a Python interpreter (e.g. `python AmongUsStats.py` or `py AmongUsStats.py`)

![Settings GIF](https://i.imgur.com/pnlpk04.gif)&nbsp;&nbsp;&nbsp;![Tray Icon GIF](https://i.imgur.com/wYzImHO.gif)

### Manual (Using either Python script or Executable)

Add the following line to your Steam: Among Us Launch Options if you're running the script manually via Python or you've downloaded the binary.

- Python: `python-interpreter "C:\path\to\script.py" %command%`
- Binary: `"C:\path\to\executable.exe" %command%`

---

## Features

- Ability to change REST Endpoint to push your JSON statistics to a database/front-end of your choice.
- Player Stats file will be polled on an interval while playing Among Us and will update live, as you play.
- Additional fields are sent in the POST Data - Unique Player ID, Last Used Nickname, Date & Time of your last change to statistics.
- Log file written to `C:\Users\<user>\AppData\LocalLow\Innersloth\Among Us\statGrabber.log` which tracks successful POST requests and also if you've opened/closed the game. 

---

## JSON Schema

Your statistics are organised into a simple JSON object before being posted to your REST endpoint. The elements you're able to access are as follows:
```
User ID
Nickname
lastUpdated
Bodies Reported
Emergencies Called
Tasks Completed
All Tasks Completed
Sabotages Fixed
Impostor Kills
Times Murdered
Times Ejected
Crewmate Streak
Times Impostor
Times Crewmate
Games Started
Games Finished
Crewmate Vote Wins
Crewmate Task Wins
Impostor Vote Wins
Impostor Kill Wins
Impostor Sabotage Wins
Unknown 1
Unknown 2
Unknown 3
Unknown 4
Unknown 5
Unknown 6
Unknown 7
```

---

## Contributing

> To get started...

1. 🍴 [Fork this repo](https://github.com/IDemixI/Among-Us-Statistics-Grabber#fork-destination-box)
2. 👥 Add yourself as a contributor under the credits section
3. 🔧 [Open a new pull request](https://github.com/IDemixI/Among-Us-Statistics-Grabber/compare) after changing the code
4. 🎉 Get your pull request approved - success!

Or just [create an issue](https://github.com/IDemixI/Among-Us-Statistics-Grabber/issues) - every little bit of help counts! 😊

---

## Contributors

| <a href="https://github.com/IDemixI" target="_blank">**IDemixI**</a> | <a href="https://github.com/OMCS" target="_blank">**OMCS**</a> |
| :---: |:---:|
| [![IDemixI](https://avatars1.githubusercontent.com/u/23632287?v=3&s=150)](https://github.com/IDemixI)    | [![OMCS](https://avatars3.githubusercontent.com/u/3914622?v=3&s=150)](https://github.com/OMCS) |
| [IDemixI](https://github.com/IDemixI) | [OMCS](https://github.com/OMCS) |

---

## FAQ

- **How do I uninstall the application?**
  - You can remove the application by simply deleting the executable and removing the Launch Options from Among Us via Steam.

---

## License

[![License](http://img.shields.io/:license-mit-blue)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**
- Copyright 2020 © [Conceptual Designs](https://github.com/IDemixI).
