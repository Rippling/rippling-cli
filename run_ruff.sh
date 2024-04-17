#!/bin/bash

set -e

RUFF_LINT="${RUFF_LINT:-true}"
REQUIRED_RUFF_VERSION="0.0.286"
PYTHON_EXECUTABLE=${PYTHON_EXECUTABLE:-"python3"}

ensure_ruff_installed() {
    if ! "${PYTHON_EXECUTABLE}" -m ruff --version &>/dev/null; then
        echo "Installing ruff ${REQUIRED_RUFF_VERSION}"
        "${PYTHON_EXECUTABLE}" -m pip install ruff==${REQUIRED_RUFF_VERSION}
    fi
    RUFF_VERSION=$("${PYTHON_EXECUTABLE}" -m ruff --version)
    if [[ $RUFF_VERSION != "ruff $REQUIRED_RUFF_VERSION" ]]; then
        echo "Incorrect ruff version ${RUFF_VERSION}; Updating ruff version."
        "${PYTHON_EXECUTABLE}" -m pip install ruff==${REQUIRED_RUFF_VERSION}
    fi
}

run_ruff() {
    ruff_cmd="ruff check"
    if [[ "$2" != "" ]]; then
        ruff_cmd="$ruff_cmd $2 $1"
    else
        ruff_cmd="$ruff_cmd $1"
    fi
    # shellcheck disable=SC2086
    "${PYTHON_EXECUTABLE}" -m $ruff_cmd
}

if [[ "$1" == "--fix" ]]; then
    RUFF_ARGS="--fix --show-fixes"
else
    RUFF_ARGS=""
fi

if [[ $RUFF_LINT = true ]]; then
    ensure_ruff_installed
    run_ruff . "$RUFF_ARGS"
fi