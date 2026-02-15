# Core Spec: Admiralty Board Reader

## Overview

Zora reads the Star Trek Online Admiralty assignment board from the screen and produces structured data describing the current state.

## Domain Concepts

- **Ship** — A card with Engineering, Science, and Tactical stats, plus optional special abilities. Ships go on maintenance (cooldown) after being assigned.
- **Assignment** — A mission requiring certain stat thresholds. Has a limited number of ship slots.
- **Campaign** — An admiralty track (Klingon, Ferengi, Romulan, etc.) with its own progress and rewards. The user selects a campaign before viewing its assignments — campaign is not extracted from assignment cards.
- **Critical Success** — Achieved when assigned ship stats exceed the assignment requirements.

## First Milestone: Read Assignments

The assignments view and the ship roster are separate screens. This milestone covers only the assignment view.

The system must be able to:

1. Capture a screenshot of the STO game window
2. Locate the assignment list within the screenshot
3. Extract assignment details from each card:
   - Name/title
   - Required Engineering, Science, and Tactical stats
   - Number of ship slots
   - Duration
   - Rarity
   - Event rewards
   - (Additional fields may be discovered from real screenshots)
4. Output the extracted data in a structured format
