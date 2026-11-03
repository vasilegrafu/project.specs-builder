#!/bin/sh
# Opens the example specification in your browser. Press Ctrl+C here to stop it.
cd "$(dirname "$0")" || exit 1
exec sh .claude/skills/specs-builder/examples/shop/specs/index.sh
