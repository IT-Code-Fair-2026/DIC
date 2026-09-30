# Introduction and Background Information

Draft content for the report's Introduction section (covers background, purpose, and
scope for all three problem statements). See `docs/PROJECT_CONTEXT.md` for the full
project context and `docs/DATASET_INVENTORY.md` / `docs/DATA_DICTIONARY.md` for the
underlying datasets referenced here.

---

## Introduction

Many remote communities across the Northern Territory lack reliable internet or mobile
coverage, and this gap is not evenly distributed: it interacts with where people live,
how many people live there, and what they earn. This report examines that interaction
through three linked problems, each built directly from combining three data layers we
constructed for all 792 NT remote communities (via the BushTel Community Profile) and
their 649 containing Statistical Areas Level 1 (SA1s, the Australian Bureau of
Statistics' finest publishable geography):

1. **Blackout exposure**: when a community's tower fails, who is cut off, and how many
   people does that represent?
2. **Investment prioritisation**: where should the next tower be funded to reach the
   most people who can least afford an alternative?
3. **Compounding vulnerability**: which communities would lose connectivity *and* have
   no physical service (school, clinic, emergency) to fall back on?

The purpose of this analysis is to move beyond simply reporting "which places lack
coverage" (a question the existing NT Mobile Coverage guide already answers at a
surface level) toward quantifying *who* is affected, *how severely*, and *where public
investment has the most leverage*. The scope is limited to the Northern Territory's
remote and very remote population (779 of 792 BushTel-listed communities), using 2021
Census figures, the ACMA radiocommunications licence register, BushTel community
records, and (for the third problem) school, health, and emergency-service location
data.

## Background Information

**Why SA1, not the individual village, carries the numbers.** The 2021 Census only
publishes reliable population, income, and household-size figures at the SA1 level:
Australia's smallest geography for which these statistics are released without
breaching privacy suppression rules. A single SA1 in remote NT can be enormous: Tanami
SA1 spans 142,011 km² (larger than many countries) and contains 15 named BushTel
communities but only 175 census-counted people. This means population,
`avg_household_income`, and `avg_household_size` are properties of the *region*, not the
individual settlement: BushTel supplies the settlement-level "depth" (which named
communities sit inside that region) but not a settlement-level population figure. Every
problem below is built on this same join: BushTel gives us *where people live and how
many distinct places*, Census/SA1 gives us *how many people, and how well-off they are*,
and the ACMA tower register gives us *what connectivity infrastructure physically
exists inside that same footprint*.

**Why this matters economically, not just geographically.** Household income falls
sharply with remoteness (median weekly household income: $2,250 in Outer Regional NT,
down to $1,325 in Very Remote areas) while average household size rises (2.8 people in
Outer Regional vs. 3.95 in Very Remote). In practice, this means the areas most likely to
depend on a single shared tower are also the areas least able to privately fund an
alternative (satellite internet, a second SIM on a different network) if that tower
fails; the same infrastructure gap has a different real-world weight depending on who
sits behind it.

**Why the blackout framing (Problem 1) is realistic, not hypothetical.** Of the 431
distinct mobile towers currently serving the NT, 330 (77%) operate on a single carrier
network with no second provider as backup, and one carrier (Telstra) alone operates 325
of them: meaning a single network fault, not just a natural disaster, can plausibly
take an entire region offline at once. This is the concrete basis for asking, per SA1,
how many people and households sit behind each tower.

**Why prioritisation (Problem 2) needs a formula, not intuition.** Public infrastructure
funding (e.g. the Mobile Black Spot Program) has historically left a visible backlog: 8
of 49 funded NT sites remain unbuilt, and those unbuilt sites sit a median 219 km from
the nearest community: even further than the sites already completed (102 km).
Deciding where the *next* dollar goes benefits from an explicit, reproducible ranking
rather than case-by-case judgement, which is what combining population, existing tower
count, income, and household size per SA1 provides.

**Why compounding vulnerability (Problem 3) is the honest picture.** Connectivity has
always been assessed on its own, but a community without a tower and without a nearby
clinic, school, or police presence experiences a materially different level of risk than
a community without a tower but with those services close by. The newly integrated
schools, medical, and emergency-facility datasets let us test, for the first time in
this project, whether the same communities are failed on both fronts simultaneously.
