# What It Does

This project allows you to set a sleep timer for music playing on a Chromecast audio.  As of May 2018, Google does not support sleep timers for music casting from a Google Home to a Chromecast Audio.  And the sleep timers on Android were cumbersome and unreliable at turning off a Chromecast.  With this script, you can set a sleep timer for a Chromecast with a single button press.

# How To Use It

The software runs on a Raspberry Pi that is equipped with the microphone, button, and speaker that comes with the [AIY voice kit](https://aiyprojects.withgoogle.com/voice/).  It relies on the AIY drivers and libraries, which are not duplicated in this repository.  You must supply the IP address of the Chromecast you wish to control and a correct path to [stream2chromecast](https://github.com/dancardy/stream2chromecast) in `chromecasttakeover.sh`.  You will want to run the `sleeptimer.py` script automatically by [setting it as a systemd service](https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units).  An example .service file is included in the repository.

To avoid conflicting with a Google Home, this script only listens for voice commands after the AIY voice kit button has been pressed.

| Command | Description |
|---------|-------------|
| Silence (button press with no command) | The sleep timer will be set for the default duration (45 minutes).|
| "Sleep in &lt;minutes&gt;" or <br>"Sleep &lt;minutes&gt;" or just <br>"&lt;minutes&gt;" | The sleep timer will be set (or re-set) to the specified time.|
| "Cancel" | Any active sleep timers are deactivated.|
| "How much time is left?" | The voice will announce the time left on the timer.|
| Other voice commands | You will receive the audio response provided by the Google Assistant API.|

# License

You are free to use this in any way you wish.
