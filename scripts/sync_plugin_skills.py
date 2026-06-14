#!/usr/bin/env python3
"""Compatibility entrypoint for the full Vulca plugin package sync."""

from __future__ import annotations

import sys

from sync_plugin import main


if __name__ == "__main__":
    sys.exit(main())
