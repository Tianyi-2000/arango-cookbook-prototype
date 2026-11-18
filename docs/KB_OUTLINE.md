# Knowledge base outline

Northwind Auto is a **fictional** used-car retailer that also buys cars from the public. Its help center is the knowledge base (KB) for this cookbook. Most articles are for people **selling** a car to Northwind; a few are for people who **bought** from Northwind, included because they look alike. All companies, states and policies are invented for illustration and are not legal information.

This outline lists what the data covers, without the article text, so that test questions can be written in a customer's own words before the articles exist.

**"Today" in this cookbook is 2026-11-01**, fixed, so results don't change with the day you run it.

## What's in the data
| Collection | Size | What it is |
|---|---|---|
| `articles` | 51 articles, 68 versions | Help center articles (authoritative) |
| `tickets` | ~200 | Past support conversations, 2022-03 to 2026-10 (not authoritative, sometimes outdated or wrong) |
| `forms` | 15 | Northwind forms, cited by code (`NW-XXX-n`) |
| `states` | 5 | Fictional states with their own rules |
| `lenders` | 12 | Fictional banks and credit unions; some are in the e-payoff network |
| `lessors` | 6 | Fictional leasing companies with different buyout rules |
| `stores` | 25 | Stores with coordinates and services (used later, for geo) |

## Versions
The help center was rewritten on **2026-02-01**. Each article is one of four kinds:
- **unchanged**: one version, effective since 2022-01-01, still current. *(Being from 2022 doesn't make it stale.)*
- **rewritten** ★: a 2022 version (2022-01-01 to 2026-01-31, now superseded) and a 2026 version (from 2026-02-01, current).
- **new in 2026** ✚: one version, effective from 2026-02-01. Before that, the KB had nothing on the topic.
- **retired** ✖: one 2022 version, ended on 2026-01-31 with no replacement.

**Transition rules** (the 2026 versions say so explicitly):
- Offers issued before 2026-02-01 keep their old 7-day / 300-mile terms.
- NW-POA-1 forms signed before 2026-02-01 are accepted until 2026-06-30.

## Articles

### Selling: the basics
| doc_id | Title | One line | Kind |
|---|---|---|---|
| `how_selling_works` | Selling your car to Northwind: how it works | Offer → appraisal appointment → paperwork → payment | ★ walk-in store quotes ended; offers are online only |
| `walk_in_quotes` | Getting a quote at the store | Walk in and get a quote on the spot | ✖ retired 2026-01-31 |
| `offer_validity` | How long is my offer good for? | How long an offer lasts and what happens when it expires | ★ 7 days / 300 miles → 5 days / 250 miles (transition rule above) |
| `what_changes_offer` | What can change your offer at the appraisal | Undisclosed damage, missing keys, aftermarket parts | ★ missing key: $150 → $250 off; new damage disclosure form NW-DMG-1 |
| `appointment_checklist` | What to bring to your appraisal appointment | IDs, registration, keys, title or payoff letter | ★ NW-ODO-1 → NW-ODO-2; mobile ID accepted, in Virginia only |
| `reschedule_cancel` | Rescheduling or canceling an appointment | Rescheduling keeps the offer if it's still valid | unchanged |
| `home_pickup` | Home pickup service | Northwind picks up the car and pays on the spot | ★ free → $99 fee; not available in Texas; needs NW-PU-1 |
| `selling_without_buying` | Do I have to buy a car to sell one? | No; the offer is the same either way | unchanged |
| `offer_scams` | Protecting yourself from offer scams | Northwind never asks for payment or gift cards | ✚ new |

### Selling with a loan
| doc_id | Title | One line | Kind |
|---|---|---|---|
| `selling_with_loan` | Selling a car you are still paying off | The lender holds the title; Northwind pays the lender off from your offer | unchanged |
| `payoff_letter` | Getting a payoff letter from your lender | What the letter must show and how to get it | ★ 10-day → 15-day payoff; new NW-LPA-1 lets Northwind request it |
| `epayoff_network` | Lenders in our e-payoff network | Network lenders confirm the payoff the same day, with no letter needed | ✚ new |
| `negative_equity` | If you owe more than our offer | Paying the difference at the appointment | ★ personal checks no longer accepted; cashier's check or debit only |
| `getting_paid` | When and how you get paid | Payment methods, and when the lender is paid | ★ mailed checks ended; bank draft or direct deposit only |
| `keep_paying_until_confirmed` | Should I keep making loan payments? | Yes, until the lender confirms the payoff | unchanged |
| `lender_overpayment_refund` | Getting back an extra loan payment | The lender refunds you, not Northwind, in 2–4 weeks | unchanged |
| `lien_still_on_title` | My loan is paid off but the lien is still on the title | Get a lien release letter; form NW-LRL-1 | unchanged |

### Title problems
| doc_id | Title | One line | Kind |
|---|---|---|---|
| `lost_title` | Selling a paid-off car when the title is lost | You need a duplicate title before Northwind can buy | unchanged |
| `duplicate_title_virginia` · `_north_carolina` · `_georgia` · `_texas` · `_california` | Getting a duplicate title in *State* | Process and timing in each state (5 articles) | unchanged |
| `branded_title` | Salvage and rebuilt titles | Which branded titles Northwind buys | ★ rebuilt titles now bought at a reduced offer; salvage still not |
| `title_name_mismatch` | The name on the title doesn't match my ID | Name changes (marriage, court order); form NW-NMC-1 | unchanged |
| `electronic_titles` | States with electronic titles | Virginia and Texas: no paper title; the release is electronic | unchanged |

### Who owns the car
| doc_id | Title | One line | Kind |
|---|---|---|---|
| `co_owners` | When more than one person owns the car | Every owner signs; a power of attorney if one can't come | ★ NW-POA-1 (notarized) → NW-POA-2 (e-sign); Georgia still requires a notary |
| `inherited_car` | Selling a car you inherited | Heir or executor paperwork | ★ 2026 accepts affidavit NW-EST-1 in place of court letters for small estates |
| `business_car` | Selling a car owned by a business | An authorized signer and form NW-BUS-1 | unchanged |
| `divorce_ex_on_title` | My ex is still on the title | Both sign, or bring the court order that awards you the car | unchanged |
| `military_deployed` | Selling while deployed | Form NW-MIL-1 replaces a notarized power of attorney, in every state including Georgia | ✚ new |
| `selling_for_someone_else` | Selling a family member's car for them | You need their power of attorney | unchanged (still cites NW-POA-1, see "KB problems" below) |

### Leased cars
| doc_id | Title | One line | Kind |
|---|---|---|---|
| `leased_car` | Selling a car that you lease | A buyout from the leasing company; dealer payoff quote; form NW-LSE-1 | unchanged |
| `lessor_buyouts` | Which leasing companies allow third-party buyouts | Rules for all 6 leasing companies | ★ Crescent: not allowed → allowed; Apex adds a $350 fee |
| `lease_equity` | If our offer is more than your lease buyout | Who keeps the difference, which depends on the leasing company | unchanged |
| `lease_vs_turn_in` | Selling vs. turning in at lease end | Compare the two | unchanged |

### Registration, plates, insurance
| doc_id | Title | One line | Kind |
|---|---|---|---|
| `registration_expired` | My registration is expired | You can still sell; North Carolina requires it to be current | unchanged |
| `license_plates` | What to do with your license plates | Keep, leave, or return them, by state | ★ was "always remove"; 2026: in North Carolina plates stay with the car; in California return them within 10 days with NW-PLT-1 |
| `cancel_insurance` | When to cancel your insurance | Only after the sale is complete | unchanged |
| `toll_tags_personal_data` | Toll tags, garage codes and paired phones | Remove them before you sell | unchanged (has a broken link, see below) |
| `out_of_state` | Selling a car registered in another state | Extra paperwork depends on the state | ★ 2026 adds California's plate rule |

### Vehicle condition
| doc_id | Title | One line | Kind |
|---|---|---|---|
| `open_recalls` | Selling a car with an open recall | Northwind still buys it | unchanged |
| `odometer_problems` | Broken or replaced odometer | "Not actual mileage" on the odometer form | unchanged (still cites NW-ODO-1, see below) |
| `non_running_cars` | Selling a car that doesn't run | Was "not bought"; now bought, with towing at some stores | ★ |
| `modified_cars` | Cars with aftermarket modifications | How mods affect the offer | unchanged |
| `flood_damage` | Flood-damaged cars | Flood titles count as branded; Northwind doesn't buy them | unchanged |

### Buying from Northwind (look-alikes)
| doc_id | Title | One line | Kind |
|---|---|---|---|
| `buy_title_northwind_finance` | When will I get my title? (financed with Northwind) | Northwind holds it until the loan is paid | unchanged |
| `buy_title_outside_lender` | When will I get my title? (outside lender) | Your lender holds it, not Northwind | unchanged |
| `returns` | Returning a car you bought from us | The return window | ★ 7 days → 30 days |
| `trade_in_vs_sell` | Trading in vs. selling outright | The trade-in tax credit differs by state | ★ 2026: Texas caps the credit at $5,000 |
| `buy_temp_plates` | Temporary plates on a car you bought | How long they last | unchanged |

## Forms
| Code | Name | Status |
|---|---|---|
| NW-POA-1 | Power of attorney (notarized) | retired 2026-02-01 → NW-POA-2; copies signed before then accepted until 2026-06-30 |
| NW-POA-2 | Power of attorney (e-sign) | current; Georgia still requires a notary |
| NW-ODO-1 | Odometer statement | retired 2026-02-01 → NW-ODO-2 |
| NW-ODO-2 | Odometer disclosure statement | current |
| NW-DMG-1 | Damage disclosure | new in 2026 |
| NW-LPA-1 | Lender payoff authorization | new in 2026 |
| NW-LSE-1 | Lease buyout authorization | current |
| NW-LRL-1 | Lien release request | current |
| NW-EST-1 | Heir and estate affidavit | current; accepted for small estates since 2026 |
| NW-BUS-1 | Business signing authority letter | current |
| NW-NMC-1 | Name change affidavit | current |
| NW-MIL-1 | Deployed owner authorization | new in 2026 |
| NW-PU-1 | Home pickup agreement | current |
| NW-PLT-1 | Plate return receipt (California) | new in 2026 |
| NW-TRD-1 | Trade-in tax credit worksheet | current (buying side) |

## States (fictional)
| State | What is different |
|---|---|
| Virginia | Electronic titles; duplicate titles online in about a week; mobile ID accepted at appointments |
| North Carolina | Paper titles; duplicates take 4–6 weeks; cars from other states need an emissions certificate; plates stay with the car; registration must be current to sell |
| Georgia | Paper titles; a power of attorney must be notarized, even NW-POA-2 (NW-MIL-1 is the exception) |
| Texas | Electronic titles; no home pickup; trade-in tax credit capped at $5,000 |
| California | Paper titles; plates go back to the state within 10 days (NW-PLT-1) |

## Lenders (fictional): e-payoff network or not
- **In the network** (same-day payoff confirmation): Bayline Credit Union, Northwind Auto Finance, Meridian Auto Loans, Pinewood Federal Credit Union, Lakeshore Bank, and Granite Bank (joined in 2026).
- **Not in the network** (payoff letter needed): Redstone Credit, Coastal Credit Union, Oakline Finance, Valley Motor Credit, **Harbor Trust Bank**, and **Summit Peak Bank**. These last two have names close to two leasing companies, on purpose.

## Leasing companies (fictional)
| Company | Third-party buyouts |
|---|---|
| Harbor Leasing | not allowed |
| Summit Auto Lease | allowed |
| Crescent Motor Credit | not allowed in 2022; allowed since 2026-02-01 |
| Apex Lease Co | allowed; a $350 fee since 2026 |
| Bluewater Leasing | allowed only if you also buy a car from Northwind |
| Ironwood Lease | not allowed |

## Past support tickets
About 200 short conversations from 2022-03 to 2026-10, in chat, email and phone-note style. Each one cites the article version that was current when it was answered. About 10% gave answers that were right then but are outdated now, and a few contain agent mistakes. Tickets help retrieval because they use customers' words, but they're never the authority. Generated by a script (`scripts/generate_tickets.py`) and committed.

## Stores
25 stores across the 5 states, with coordinates, opening hours and services (appraisal, lease buyout, home pickup, towing for non-running cars). Used in the later geo chapter ("nearest store open Sunday that tows non-running cars").

## KB problems, left in on purpose (a real KB has these too)
- `selling_for_someone_else` (unchanged since 2022) still cites the retired **NW-POA-1**, and `odometer_problems` still cites the retired **NW-ODO-1**. A graph query can find every current article that points at a retired form.
- `toll_tags_personal_data` links to an article that doesn't exist (`account_deletion`).
- Some old tickets contradict the current articles.

## Tricky cases to aim at
- **Time boundaries:** an offer issued on Jan 28, 2026, used on Feb 4; an NW-POA-1 signed in January and used in May (or in July); a question asked on 2026-02-01 itself; asking in 2023 about something that only exists since 2026.
- **Rule conflicts and combinations:** a state exception beats the general rule (Georgia notary), and an exception to the exception (NW-MIL-1 in Georgia); three conditions at once (inherited + loan still open + title lost); a false premise ("since you can't buy a car without the title…").
- **Messy input:** typos ("Cresent", "lein holder", "Brevn"), slang ("pink slip" = title, "underwater" or "upside down" = negative equity), synonyms (lender = lienholder = bank), near-identical names (Harbor Leasing vs Harbor Trust Bank).
- **Messy KB:** a current article citing a retired form; an old ticket that contradicts the current article; a question that's half answerable.

## Not covered (questions about these have no answer in the KB)
Motorcycles, RVs and boats; cars registered outside the country; selling a car with an open insurance claim; consignment; financing a purchase (rates, credit checks).
