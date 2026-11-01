#!/bin/sh
# Opens the NovaLife specification in your browser. Press Ctrl+C here to stop it.
cd "$(dirname "$0")" || exit 1
exec sh targets/novalife-2/specs/index.sh
