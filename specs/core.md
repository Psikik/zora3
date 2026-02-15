# Core Spec: Admiralty Board Reader

## Overview

Zora reads the Star Trek Online Admiralty assignment board from the screen and produces structured data describing the current state.

## Domain Concepts

- **Ship** — A card with Engineering, Science, and Tactical stats, plus optional special abilities. Ships go on maintenance (cooldown) after being assigned.
- **Assignment** — A mission requiring certain stat thresholds. Has a limited number of ship slots. Belongs to a campaign.
- **Campaign** — An admiralty track (Klingon, Ferengi, Romulan, etc.) with its own progress and rewards.
- **Critical Success** — Achieved when assigned ship stats exceed the assignment requirements.

## First Milestone: Read the Board

The system must be able to:

1. Capture a screenshot of the STO game window
2. Locate the admiralty board UI within the screenshot
3. Extract assignment details from the board:
   - Assignment name
   - Required Engineering, Science, and Tactical stats
   - Number of ship slots
   - Which campaign the assignment belongs to
4. Extract available ship card details:
   - Ship name
   - Engineering, Science, and Tactical stats
   - Maintenance status (available or on cooldown)
5. Output the extracted data in a structured format
