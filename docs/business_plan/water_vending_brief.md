# Project: Water Vending — Initial Briefing

> Source: discussion transcript (Oct 5, 11:24).
> Status: raw brainstorm, requires formalization into a cost estimate and plan.

## 1. Project Context

- The project is a network of drinking water vending machines.
- The machine is treated primarily as a **"piece of hardware"** — a physical device with a set of requirements.
- Current stage goal: determine **which locations and areas we cover**, what the machine requirements are, and how we build the economics and documentation.

## 2. Machine Requirements ("Hardware")

### 2.1. General Principles
- **Low cost:** all else equal, choose what is cheaper, faster, more reliable.
- **Repairability:** spare parts warehouse, fast replacement of units.
- **Serviceability:** the machine must be easy to service.
- **Observability:** ability to remotely understand the machine's state.
- **Integration:** modules (camera, telemetry, payment) must integrate easily, without "a month-long integration on some bullshit protocol".

### 2.2. Machine Composition
- **Payment modules:**
  - coin acceptor;
  - bill acceptor;
  - **priority — cashless:** payment from a phone (pressed a button → bought 5 L). In Serbia, cash is treated cautiously, so cashless is preferable.
  - Option of **complete rejection of cash** is possible.
- **Camera:**
  - needed for monitoring the machine's state;
  - scenarios: machine working / "trashed" / taped over with a bag / stolen.
- **GPS tracker:**
  - cheap;
  - needed for location tracking (the machine can't see itself).
- **Telemetry:**
  - water temperature (freezing risk → need to react);
  - heater control.
- **Heater:**
  - removable or switchable;
  - in summer, it can be left out of the machine so it isn't stolen;
  - risk: removed during cartridge replacement, forgotten, not brought back.

### 2.3. Machine Configurations
- There may be **more than one** configuration.
- Example: in an office — card payment; in a professional area (kitchen) — a different "piece of hardware".
- Each configuration has its own technical requirements.

### 2.4. Production and Assembly
- Need to decide: **how we order assembly** — ourselves or otherwise.
- Risks: incompatible components shipped ("the coupler doesn't fit"), or a part is loose → it can be ripped out.
- **Coordination and tolerances:**
  - no one can be trusted;
  - all tolerances and mismatches are signed off;
  - penalties for violation (example: tolerance 0.5 mm, received 3 mm → fine).
- **Anti-vandalism:** the body and units must be protected.

## 3. Locations and Placement Strategy

### 3.1. Site Requirements
- The site must be **near us** — it's important that we use the product ourselves.
- Don't place it in the middle of the street: difficulties with laying utilities (welding, trenches, "philosophers").
- Better to negotiate with a building / office.
- Need to **track electricity consumption** — few will connect it for free.
- Site economics (example): ~150 EUR per month per site; meanwhile costs can "eat" a grand on the classic setup.

### 3.2. Target Audiences
- Offices.
- Professional areas (kitchens).
- Residential buildings.
- Need **strategic understanding**: which audiences we cover and where they are.

### 3.3. Entry Scenarios
- **Offices:** subscription model — guaranteed payment, volume cap ("we don't care how much you drink, but there must be a cap").
- **Professional areas:** a different machine configuration.
- Option with a water cooler (free installation) is possible as an alternative.

## 4. Product (Water)

- Water must be **purified (filtered)** and drinkable.
- Criticism of existing options:
  - filtered water from stores ("globuses") — impossible to drink;
  - mineral water like "AKOVA" — impossible to drink;
  - tap water — not allowed;
  - boiled — not allowed;
  - through a filter — "it becomes awesome", i.e. it becomes normal.
- Conclusion: the product must be such that you want to drink it.

## 5. Pricing and Franchise

### 5.1. Pricing
- Need to go through all four marketing Ps.
- Decide: **single price** or **different price**.
- Calculate the economics depending on the model.

### 5.2. Franchise
- Considered as a possible scaling model.
- Conditions:
  - franchise is sold in **open zones** (small ones) where the company itself is not present;
  - the company covers the city itself, the franchise — only in permitted zones.
- Company's role:
  - equipment supplier;
  - warranty repair;
  - training, consultations, courses.
- A field engineer for filter maintenance — **too expensive** (don't send a car for three hours).
- Scaling: expansion to the **entire Balkan region** is possible.
- Brand: monitor quality, "water is a product everyone loves".
- If scaling and consolidating costs fails — the franchise is not needed.

## 6. Finance and Taxes

### 6.1. Cash
- Plus of cash: ability to **not declare all expenses**.
- Example: water cost — 30–50% of turnover.
- Minus: need to buy an acceptor and configure it.

### 6.2. Tax Aspect
- Splitting flows:
  - bottled water — 20% tax;
  - the rest ("kisel") — 10%.
- Need to calculate **whether it's worth splitting** this.
- Example: we sell 2 L, tax 10% on the entire turnover.
- Competition: stores (bottles of alcohol) — they have their own taxes.

## 7. Documentation and Planning

### 7.1. What Is Needed
- **Cost estimate** — detailed.
- **Detailed plan**: P0, P1, phases.
- **First phase:** what can be bought, introducing the balance, discussing blocks.
- **Documentation package:**
  - business plan;
  - financial plan;
  - cost estimates;
  - calculations;
  - project.

### 7.2. Process
- Coordination of tolerances and penalties.
- Consultations with specialists ("dipsiks") on the documentation package.
- On engineering: we're not bringing anyone in yet, but a consultation is planned.

## 8. Open Questions

- Which locations and areas do we cover first?
- One machine configuration or several?
- Is card payment needed in the office?
- How do we order assembly: ourselves or through a contractor?
- Single price or different?
- Is a franchise needed, and on what terms?
- How do we split tax flows?
- What documentation package is minimally necessary to start?

## 9. Next Steps

1. Formalize machine requirements into a technical specification.
2. Assemble the cost estimate by blocks: technical, legal, financial, marketing, locations, IT/telemetry.
3. Review each part of the estimate.
4. Form the final documentation package (business plan, financial plan, cost estimates, project).
