# Game Insights — LILA BLACK

## Insight 1: AmbroseValley Has Three Dominant Kill Zones

**What I saw:** The kill zone heatmap on AmbroseValley shows three extreme hotspots concentrated in the central and lower-central areas of the map, while the northern and eastern edges are almost completely cold.

**Evidence:** Kill heatmap across 566 matches shows 1,799 kill events with 80%+ concentrated in roughly 20% of the map area.

**Actionable:** The three hotspot zones are likely high-loot areas pulling players into predictable confrontation. Level designers should consider whether this concentration is intentional or whether loot distribution elsewhere needs balancing to encourage exploration of dead zones.

**Why a Level Designer Should Care:** If players are ignoring 80% of the map, the design effort spent on those areas is wasted. Either those areas need stronger loot incentives or the hotspot areas need their loot density reduced.

---

## Insight 2: Storm Deaths Are Clustered at Map Edges, Not Random

**What I saw:** KilledByStorm events are not spread randomly across the map. They cluster at specific edge zones, suggesting the storm moves in a predictable direction and players who move late consistently die in the same locations.

**Evidence:** Storm death heatmap shows concentrated clusters on one side of AmbroseValley consistently across multiple days.

**Actionable:** Add extract points or cover near the storm-entry zones to give late-moving players a fighting chance. Alternatively, vary storm entry direction across matches to prevent players from gaming the pattern.

**Why a Level Designer Should Care:** Predictable storm deaths mean experienced players have a large advantage over new players simply from pattern knowledge, not skill. This hurts player retention.

---

## Insight 3: Bots and Humans Follow Completely Different Movement Patterns

**What I saw:** On the Player Paths view, human paths show irregular, exploratory movement with backtracking and cluster around loot/combat zones. Bot paths are visibly more linear and grid-like, moving in straighter lines across the map.

**Evidence:** Filtering to show only BotPosition vs only Position events shows clearly different spatial distributions. Bot paths converge less on the kill hotspots.

**Actionable:** Bot pathing could be improved to better simulate human exploration behaviour, specifically by adding loot-seeking logic that pulls bots toward high-value areas. Currently bots are not creating realistic combat pressure in the hotspot zones.

**Why a Level Designer Should Care:** If bots don't behave like humans, the map doesn't test as designed. A map balanced around bot behaviour will feel wrong when real players fill those slots.