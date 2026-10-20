# Slasher Browser Game Design

## Working Title

**Last Shift at Black Pine**

## High Concept

A 2D top-down browser survival horror game inspired by 80s slasher movies, VHS grime, summer-camp paranoia, and synth-heavy dread. The player is the last counselor still moving through Black Pine Camp after curfew. A masked killer stalks the grounds. To survive the night, the player must keep power alive, rescue stranded campers, and assemble a route to the boathouse radio before dawn.

The tone should feel like a playable slasher finale rather than a gore simulator: panic, noise, chase beats, near misses, and improvised survival.

## Why This Fits The Browser

- Short runs: 10-15 minutes
- Simple readable input: move, interact, sprint, hide, distract
- Strong replay value from shuffled objectives and patrols
- Top-down 2D presentation keeps scope controlled and legible
- DOM HUD can handle text, prompts, timers, and accessibility settings

## Recommended Runtime

- Engine: Phaser
- Camera: top-down fixed camera with slight screen shake and lighting pulses
- Simulation: separate state for map, AI, timers, noise, and objective progress
- UI: DOM overlay for objective strip, panic meter, inventory slots, and pause screens

## Pillars

1. **Cat-and-mouse tension**
   The killer is not always on-screen, but the player should feel hunted at all times.
2. **Noise creates danger**
   Sprinting, slamming doors, broken glass, generators, and thrown objects all reshape the chase.
3. **Small victories under pressure**
   Every fuse installed, camper rescued, and shortcut unlocked feels like stealing time from the night.
4. **Cinematic escalation**
   The night gets worse in clear phases, like a slasher film moving toward its final act.

## Player Fantasy

You are not a fighter. You survive by reading the map, managing nerves, creating distractions, and making hard route choices before the killer closes in.

## Primary Verbs

- Move
- Crouch
- Sprint
- Interact
- Hide
- Throw distraction
- Barricade
- Rescue

## Core Loop

1. **Scout**
   Move through cabins, utility sheds, docks, and trails to gather tools, key items, and clues about safe routes.
2. **Stabilize**
   Restore critical camp systems such as lights, breaker boxes, or gate locks to slow the killer and open traversal options.
3. **Risk**
   Rescue stranded campers or retrieve high-value tools from dangerous zones to improve the odds of escape.
4. **Trigger**
   Each major objective raises tension, causing the killer to hunt more aggressively and forcing the player off comfortable routes.
5. **Escape**
   Reach the boathouse radio and call for help, then survive a final chase sequence to the extraction point.

That loop repeats several times in one run, with each cycle shortening the margin for error.

## Moment-To-Moment Play

- The player enters a zone and scans for loot, hiding spots, escape paths, and noise hazards.
- Interactions are quick but vulnerable. Fixing a breaker or lifting a barricade leaves the player exposed for a few seconds.
- Noise creates a visible and audible alert radius that can draw the killer.
- The killer does not fully mirror the player. Instead, it uses search states, suspicion, line-of-sight checks, and scripted spike events to preserve fear.
- When spotted, the game shifts into a chase: sprint management, door choices, vault routes, and improvised distractions.
- If the player breaks pursuit, they return to stealth, but panic stays elevated for a while, making the next mistake more likely.

## Run Structure

### Phase 1: Dusk

- Low killer pressure
- Learn the current map shuffle
- Find basic tools: flashlight, first fuse, map scraps, one distraction item

### Phase 2: Midnight

- More locked routes and failed utilities
- Rescue objectives appear
- Killer patrols become tighter and more reactive to sound

### Phase 3: Final Reel

- Storm cuts visibility
- Safe rooms stop feeling safe
- The radio objective unlocks
- The killer gets a direct pursuit burst and fewer fake-outs

## Win State

- Restore enough camp systems to power the boathouse radio
- Rescue at least a minimum number of campers or secure their cabin keys
- Call for extraction
- Survive the final chase to the dock

## Failure States

- The killer catches the player during a chase or failed hiding sequence
- Panic meter maxes out during high-pressure events, causing a stumble or botched interaction
- Too many campers are lost, locking the best ending and forcing a desperate solo escape variant

## Tension Systems

### Panic Meter

Panic rises when the killer is nearby, during darkness, after seeing bodies, or while staying in chase too long. High panic causes:

- louder breathing
- slower interaction timing
- less accurate throws
- short stumbles after long sprints

### Noise System

Most actions emit noise. The player constantly trades speed for stealth.

Examples:

- Sprinting on wooden floors is loud
- Rain masks footsteps outdoors
- Turning on cabin lights helps visibility but exposes position
- Throwing a bottle can redirect the killer for a short window

### Light And Power

Light is safety and risk at the same time.

- Lit cabins reduce panic and reveal clues
- Powered zones make the player easier to track
- Some objectives require restoring power, which also creates new danger

## Killer Design

The killer should feel inevitable, not random.

- **Search state**: patrols recent noise sources and last-known player position
- **Stalk state**: moves slowly near objectives the player is likely to visit
- **Chase state**: commits hard when line of sight is confirmed
- **Spike events**: occasional authored scares such as a phone ringing, a generator failing, or a body reveal

This avoids the cheap feeling of pure random teleporting AI while preserving horror pacing.

## Progression And Replay

- Maps keep the same overall camp layout but shuffle item placement, blocked paths, and stranded camper locations
- Between runs, unlock new counselor traits rather than raw power
- Example traits:
  - quieter sprint start
  - faster breaker repair
  - extra distraction slot
  - reduced panic gain in darkness

Keep progression sideways, not dominant. The run should still feel fragile.

## HUD Direction

- One narrow objective strip in a top corner
- Panic meter and stamina grouped together
- Two small inventory slots
- Contextual prompt near the player for hide, rescue, repair, or vault actions
- Big text surfaces such as notes, map, and settings stay in pause or drawer overlays

The center of the screen should stay clear during play.

## Audio And Visual Direction

- Wet asphalt blues, sodium-vapor yellows, blood-red accents
- Scanlines, tape wobble, and slasher title-card transitions used sparingly
- Synth stingers for detection
- Heavy ambient layers: insects, rain, power hum, dock creaks
- Music should swell during pursuit, then drop back to almost nothing after escape

## Vertical Slice Scope

Build the first playable slice around one 8-10 minute run:

- 1 camp map
- 4 explorable cabins
- 1 utility shed
- 1 dock area
- 3 repair objectives
- 2 rescue events
- 1 killer type
- 1 final chase ending

If that slice is tense, the full game is viable.

## Core Loop Summary

The cleanest version of the game is:

**Explore -> gather tools -> repair or rescue -> create noise risk -> evade killer -> reopen route options -> power the radio -> survive final chase**

That loop is readable, replayable, and naturally slasher-shaped.

## What To Avoid

- Combat-heavy design that turns the player into a hunter
- Huge open maps with long empty travel time
- Randomized AI that feels unfair rather than threatening
- Dense HUD panels that kill the horror framing
- Long narrative interruptions during active danger
