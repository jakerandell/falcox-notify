# FalcoX Notifier

I got sick of spamming [the alpha page](https://flightone.com/alpha) for updates so I wrote this pythong script to parse
the page and send a text when there is a new version or bin.

Written in Python 3 and uses sqlite for caching results. For best results, use virtualenv.

```bash
pip install requests bs4 markdown twilio
```
