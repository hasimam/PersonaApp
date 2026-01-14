#!/usr/bin/env bash

claude "$@" < <(cat .claude/system.md agents.md)
