#!/usr/bin/env bash

# The Academic theme predates modern Hugo and breaks on its template API changes,
# so build with the pinned 0.111.3 extended binary rather than whatever is on PATH.
HUGO="${HUGO:-/Users/ringe/software/bin/hugo-0.111.3}"

exec "$HUGO" server "$@"
