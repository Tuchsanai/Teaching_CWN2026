#!/bin/sh
case "$1" in
 *Username*) printf '%s\n' "${GITHUB_LOGIN:-${GITHUB_USER:-x-access-token}}" ;;
 *) printf '%s\n' "${GITHUB_TOKEN:-$GITHUB_PASSWORD}" ;;
esac
