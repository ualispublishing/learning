#!/usr/bin/env python3
"""Marker/retry trigger for French B2 Unit 02.

The workflow still executes the blob-locked canonical generator. If Unit 02 is
absent, that generator may append it; if Unit 02 already exists, its exact B2
source lock fails closed before any duplicate write.
"""
# Intentionally no direct mutation here; existence triggers the guarded workflow.
