#!/usr/bin/env bash

claude \
  --system "$(cat .claude/system.md && echo && cat agents.md)" \
  "$@"