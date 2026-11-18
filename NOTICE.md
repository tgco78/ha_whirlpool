# Whirlpool source attribution

This repository includes the Whirlpool integration from Home Assistant Core, distributed under the Apache License, Version 2.0. The upstream starting point for the synchronization workflow is [Home Assistant Core 2026.10.1](https://github.com/home-assistant/core/tree/2026.10.1/homeassistant/components/whirlpool), commit `abe1fdd7cd6b4de1715c87b6fd87d92699514ef9`. See [LICENSE.md](LICENSE.md) for the upstream license.

In this repository, `custom_components/whirlpool/__init__.py` adds the switch platform and `custom_components/whirlpool/manifest.json` adds the custom integration version. The downstream tree also contains `custom_components/whirlpool/switch.py`, `custom_components/whirlpool/translations/` and `custom_components/whirlpool_extras/`, which are outside that upstream snapshot. The synchronization workflow applies reviewed upstream changes to the Whirlpool integration while preserving the Extras integration.
