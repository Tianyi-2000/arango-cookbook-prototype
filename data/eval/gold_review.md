# Gold set review

56 questions, 8 per type. **40 drafts to review** (below, by type) and 16 seeds already kept (at the end).
Generated from `data/eval/gold.json` by `scripts/render_gold_review.py`; don't edit this file, edit the JSON and re-run. "Today" is 2026-11-01; a version tag like `[2026]` shows which article version is meant.

For each draft: would a real customer send it? Is the perfect answer right? Do you agree with what makes it hard? Mark keep / edit / drop. After your review the gold set is frozen.

> [!todo] Before the freeze: make it sound like real people
> - Rewrite some questions the way people really type: misspellings, broken grammar, run-on sentences, no punctuation, two questions in one.
> - Add a few meaningless or off-topic messages ("asdf??", "whats the weather", a half-typed line). The right behavior is to skip them: no answer from the KB, just ask to rephrase.
> - Tell Claude in shorthand, e.g. `q12 edit: "my car dont start no more can u still buy it"`, or `add off-topic: "lol ok"`.

## exact (6 drafts)

### q03 · exact
**"Does Apex Lease Co charge anything if you buy out my lease?"**
- tricky: time_boundary
- Perfect answer: Yes. Since February 1, 2026, Apex adds a $350 third-party buyout fee to the buyout amount.
- Must-include: `$350`
- Gold articles (all needed): Which leasing companies allow third-party buyouts `[2026]`
- Traps: —
- What makes it hard: The 2022 version lists Apex as allowed with no fee; the fee is one clause inside a list of six companies.
- Your call: keep / edit / drop

### q04 · exact
**"What's form NW-LRL-1 for?"**
- Perfect answer: It's the lien release request. If your loan is paid off but the title still lists the lender, sign NW-LRL-1 and Northwind contacts the lender for the release; it can add 1 to 2 weeks.
- Must-include: `lien release`
- Gold articles (all needed): My loan is paid off but the lien is still on the title `[2022]`
- Traps: Getting a payoff letter from your lender `[2026]`
- What makes it hard: The question is only a code. Other lender-related forms (NW-LPA-1 in the payoff-letter article) look close to an embedding.
- Your call: keep / edit / drop

### q05 · exact
**"Do I need NW-EST-1 or court letters to sell my late father's car?"**
- tricky: rule_conflict
- Perfect answer: Either, together with the death certificate: NW-EST-1 is accepted for a small estate that doesn't go through probate court; otherwise bring court letters naming the executor or administrator.
- Must-include: `small estate` · `probate`
- Gold articles (all needed): Selling a car you inherited `[2026]`
- Traps: Selling a family member's car for them `[2022]`
- What makes it hard: The 2022 version knows only court letters, and the family-car article suggests a power of attorney, which ends at death.
- Your call: keep / edit / drop

### q06 · exact
**"What is the NW-PU-1 form, and do I have to pay for it?"**
- tricky: time_boundary
- Perfect answer: It's the home pickup agreement you sign when you book home pickup. The form is free, but home pickup costs $99, taken out of your payment, and it isn't available in Dunmore.
- Must-include: `home pickup agreement` · `$99`
- Gold articles (all needed): Home pickup service `[2026]`
- Traps: —
- What makes it hard: The 2022 home-pickup article says pickup is free and never names the form.
- Your call: keep / edit / drop

### q07 · exact
**"Does Bluewater Leasing let you buy my leased car?"**
- tricky: rule_conflict
- Perfect answer: Only if you also buy a car from Northwind. Any lease equity then goes toward that purchase.
- Must-include: `only if you also buy`
- Gold articles (any one is enough): Which leasing companies allow third-party buyouts `[2026]`; If our offer is more than your lease buyout `[2022]`
- Traps: —
- What makes it hard: A conditional 'yes' hidden in a list; a bot that sees 'allowed' stops reading.
- Your call: keep / edit / drop

### q08 · exact
**"What do I put on the odometer form if my odometer was replaced?"**
- tricky: messy_kb
- Perfect answer: Mark 'not actual mileage' on the odometer disclosure statement, which is NW-ODO-2 now (NW-ODO-1 was retired on February 1, 2026). Expect a reduced offer, and bring records of the true mileage if you have them.
- Must-include: `not actual mileage` · `NW-ODO-2`
- Gold articles (all needed): Broken or replaced odometer `[2022]`; What to bring to your appraisal appointment `[2026]`
- Traps: —
- What makes it hard: The odometer article still names the retired NW-ODO-1 (KB rot); the current code is only in the checklist.
- Your call: keep / edit / drop

## semantic (6 drafts)

### q11 · semantic
**"My car got totaled by the insurance company years ago and then it was fixed up. Would you still take it?"**
- tricky: time_boundary
- Perfect answer: Yes. That's a rebuilt title, and since February 1, 2026 Northwind buys rebuilt-title cars at a reduced offer. Salvage and flood titles are still not accepted.
- Must-include: `yes` · `reduced offer`
- Gold articles (all needed): Salvage and rebuilt titles `[2026]`
- Traps: Flood-damaged cars `[2022]`
- What makes it hard: No 'rebuilt' or 'branded' in the question, and the 2022 version says no.
- Your call: keep / edit / drop

### q12 · semantic
**"My car won't even start anymore. Is it worth contacting you?"**
- tricky: time_boundary
- Perfect answer: Yes. Since 2026 Northwind buys cars that don't run, and select stores tow them in for free. It can't go through home pickup.
- Must-include: `yes` · `tow`
- Gold articles (all needed): Selling a car that doesn't run `[2026]`
- Traps: Home pickup service `[2026]`
- What makes it hard: 'Won't start' vs. 'doesn't run'; the 2022 version says no; home pickup looks like the convenient answer but excludes these cars.
- Your call: keep / edit / drop

### q13 · semantic
**"Someone called saying they're from your company and that I have to pay a processing fee before they can release the money for my car. Is that real?"**
- Perfect answer: No. Northwind never asks you to pay anything to receive or release an offer. Don't pay, and report it through the Help Center.
- Must-include: `no` · `never asks`
- Gold articles (all needed): Protecting yourself from offer scams `[2026]`
- Traps: When and how you get paid `[2026]`
- What makes it hard: It reads like a payment question, so the getting-paid article looks relevant.
- Your call: keep / edit / drop

### q14 · semantic
**"My husband and I both own the car, but he's working abroad for a few months. How can I sell it without him here?"**
- tricky: rule_conflict
- Perfect answer: He can sign power of attorney NW-POA-2 electronically, with no notary (in Corlan it must be notarized). You bring it with your photo ID.
- Must-include: `NW-POA-2` · `electronically`
- Gold articles (all needed): When more than one person owns the car `[2026]`
- Traps: Selling while deployed `[2026]`; Selling a family member's car for them `[2022]`
- What makes it hard: 'Abroad' pulls toward the deployment article (NW-MIL-1), which is for the military only, and the family-car article still pushes the retired NW-POA-1.
- Your call: keep / edit / drop

### q15 · semantic
**"My autopay went out the same week you paid off my loan. Who sends me that money back?"**
- Perfect answer: Your lender refunds the extra payment to you directly, usually 2 to 4 weeks after the loan is closed. Northwind doesn't receive or forward it.
- Must-include: `your lender` · `2 to 4 weeks`
- Gold articles (all needed): Getting back an extra loan payment `[2022]`
- Traps: When and how you get paid `[2026]`
- What makes it hard: 'Autopay' and 'money back' share no words with 'extra loan payment' or 'refund'.
- Your call: keep / edit / drop

### q16 · semantic
**"Do I need to get rid of my stuff in the car's computer before you take it?"**
- Perfect answer: Yes. Unpair your phone, clear garage door codes, remove toll tags, and remove the car from any connected-car app.
- Must-include: `unpair your phone` · `garage`
- Gold articles (all needed): Toll tags, garage codes and paired phones `[2022]`
- Traps: When to cancel your insurance `[2022]`
- What makes it hard: 'Stuff in the car's computer' never says phone, toll tag or data.
- Your call: keep / edit / drop

## multi_hop (5 drafts)

### q20 · multi_hop
**"I lease from Apex and your offer is $2,000 more than my buyout. How much of that do I get?"**
- tricky: time_boundary
- Perfect answer: About $1,650. Apex passes lease equity to you, but since February 1, 2026 it adds a $350 third-party buyout fee to the buyout amount.
- Must-include: `$1,650`
- Gold articles (all needed): If our offer is more than your lease buyout `[2022]`; Which leasing companies allow third-party buyouts `[2026]`
- Traps: If you owe more than our offer `[2026]`
- What makes it hard: The equity rule and the fee live in two articles; the 2022 buyout article has no fee, which gives $2,000.
- Your call: keep / edit / drop

### q21 · multi_hop
**"I'm using home pickup and I still owe Pinewood Federal. When does Pinewood get paid, and is anything taken out of what I get?"**
- Perfect answer: Pinewood Federal Credit Union is in the e-payoff network, so it's paid the same day. You get the offer minus the payoff, minus the $99 home pickup fee.
- Must-include: `same day` · `$99`
- Gold articles (all needed): Home pickup service `[2026]`; When and how you get paid `[2026]`; Lenders in our e-payoff network `[2026]`
- Traps: When and how you get paid `[2022]`
- What makes it hard: Three facts in three articles: the fee (home pickup), the payment timing (getting paid) and whether Pinewood is a network lender (e-payoff).
- Your call: keep / edit / drop

### q22 · multi_hop
**"My offer expired while I was waiting for a duplicate title from Brevin. Do I have to start over, and will the price be the same?"**
- state: brevin
- Perfect answer: Yes, request a new offer; the amount reflects current market prices and may be higher or lower. Brevin duplicates take 4 to 6 weeks, so book the appointment for when it arrives.
- Must-include: `new offer` · `higher or lower`
- Gold articles (all needed): Getting a duplicate title in Brevin `[2022]`; How long is my offer good for? `[2026]`
- Traps: —
- What makes it hard: The duplicate-title article only says you 'may need a new one'; what happens to the price is in the offer article.
- Your call: keep / edit / drop

### q23 · multi_hop
**"I bought my car from you with a loan from Bayline Credit Union. Now I want to sell it back before it's paid off. Who has my title, and do I need a payoff letter?"**
- tricky: rule_conflict
- Perfect answer: Bayline holds the title until the loan is paid off. You can still sell: Northwind pays Bayline from your offer, and because Bayline is in the e-payoff network, no payoff letter is needed.
- Must-include: `Bayline holds the title` · `no payoff letter`
- Gold articles (all needed): When will I get my title? (outside lender) `[2022]`; Selling a car you are still paying off `[2022]`; Lenders in our e-payoff network `[2026]`
- Traps: When will I get my title? (financed with Northwind) `[2022]`
- What makes it hard: It starts on the buying side and ends on the selling side. The Northwind-financing title article looks closer but is the wrong lender.
- Your call: keep / edit / drop

### q24 · multi_hop
**"My dad passed away and his car is still financed with Lakeshore Bank. Do I need a payoff letter to sell it?"**
- Perfect answer: No payoff letter: Lakeshore Bank is in the e-payoff network. You still need the death certificate plus court letters or NW-EST-1, and Northwind pays the loan off from the offer.
- Must-include: `no payoff letter` · `death certificate`
- Gold articles (all needed): Selling a car you inherited `[2026]`; Selling a car you are still paying off `[2022]`; Lenders in our e-payoff network `[2026]`
- Traps: Selling a family member's car for them `[2022]`
- What makes it hard: Inherited → loan → network lender: three hops, and the family-car article (power of attorney) is a confident wrong turn.
- Your call: keep / edit / drop

## temporal (6 drafts)

### q27 · temporal
**"Can I just drive over to one of your stores and have someone look at my car and give me a price?"**
- tricky: time_boundary
- Perfect answer: Not anymore. Since February 1, 2026 offers are online only: get an instant offer online, then book an appraisal appointment at a store.
- Must-include: `online` · `no walk-in`
- Gold articles (all needed): Selling your car to Northwind: how it works `[2026]`
- Traps: —
- What makes it hard: The retired walk-in article matches the question almost word for word.
- Your call: keep / edit / drop

### q28 · temporal
**"Back in December 2025 I got an offer. How many miles could I put on the car before it expired?"**
- rules as of 2025-12-15 · tricky: time_boundary
- Perfect answer: 300 miles, or 7 days, whichever came first. That was the rule until January 31, 2026.
- Must-include: `300 miles`
- Gold articles (all needed): How long is my offer good for? `[2022]`
- Traps: —
- What makes it hard: The question is about the past: the current 2026 version (250 miles) is the trap here, and filtering to 'today' picks it.
- Your call: keep / edit / drop

### q29 · temporal
**"Is Granite Bank in your e-payoff network? My appointment is next week."**
- asked on 2026-02-20 · rules as of 2026-02-27 · tricky: time_boundary
- Perfect answer: Not yet: Granite Bank joins on March 15, 2026. For next week's appointment, bring a payoff letter or sign NW-LPA-1 so Northwind requests one.
- Must-include: `not yet` · `March 15`
- Gold articles (all needed): Lenders in our e-payoff network `[2026]`
- Traps: —
- What makes it hard: The article lists Granite next to the network lenders; the joining date is the whole answer.
- Your call: keep / edit / drop

### q30 · temporal
**"In 2023 I tried to return a car I'd bought from you, 10 days after delivery, and they said it was too late. Was that right?"**
- rules as of 2023-06-15 · tricky: time_boundary
- Perfect answer: Yes. Back then the return window was 7 days (and 250 miles). Since February 1, 2026 it's 30 days, but that doesn't apply to cars bought before then.
- Must-include: `yes` · `7 days`
- Gold articles (all needed): Returning a car you bought from us `[2022]`
- Traps: —
- What makes it hard: The current 30-day rule would say the store was wrong.
- Your call: keep / edit / drop

### q31 · temporal
**"Can you mail me a check for my car like you did for my friend in 2023?"**
- tricky: time_boundary
- Perfect answer: Not anymore. Northwind stopped mailing checks on February 1, 2026; you get a bank draft or a direct deposit (1 to 3 business days).
- Must-include: `no` · `direct deposit`
- Gold articles (all needed): When and how you get paid `[2026]`
- Traps: —
- What makes it hard: The friend's 2023 story matches the 2022 version, which offered mailed checks.
- Your call: keep / edit / drop

### q32 · temporal
**"How much do you take off the offer if I only have one key?"**
- tricky: time_boundary
- Perfect answer: $250 for each missing key (it was $150 before February 1, 2026).
- Must-include: `$250`
- Gold articles (all needed): What can change your offer at the appraisal `[2026]`
- Traps: —
- What makes it hard: Two versions with different numbers in the same sentence position.
- Your call: keep / edit / drop

## conditional (5 drafts)

### q36 · conditional
**"I live in Dunmore. Can someone come pick up my car?"**
- Perfect answer: Not in Dunmore: home pickup isn't available there, so bring the car to a store.
- Must-include: `not available in Dunmore`
- Gold articles (all needed): Home pickup service `[2026]`
- Traps: —
- What makes it hard: The 2022 version says pickup is available in every state.
- Your call: keep / edit / drop

### q37 · conditional
**"My registration expired last month. I'm in Brevin. Can I still sell this weekend?"**
- state: brevin · tricky: rule_conflict
- Perfect answer: In Brevin the registration has to be current on the day of the sale, so renew it first. In the other states an expired registration is fine.
- Must-include: `renew` · `must be current`
- Gold articles (all needed): My registration is expired `[2022]`
- Traps: —
- What makes it hard: The article's headline says yes; the Brevin exception is one sentence.
- Your call: keep / edit / drop

### q38 · conditional
**"I'm in Aldora. Do I need to bring my paper title?"**
- state: aldora
- Perfect answer: No. Aldora uses electronic titles, so there's no paper title to bring; Northwind transfers the title electronically at the appointment.
- Must-include: `no paper title` · `electronically`
- Gold articles (all needed): States with electronic titles `[2022]`
- Traps: Selling a paid-off car when the title is lost `[2022]`
- What makes it hard: The lost-title article (which demands a title) and the checklist ('bring the title') both look relevant.
- Your call: keep / edit / drop

### q39 · conditional
**"Can I show my ID on my phone instead of my physical license? I live in Eastvale."**
- state: eastvale · tricky: rule_conflict
- Perfect answer: Not in Eastvale. A state mobile ID is accepted only in Aldora; everywhere else, bring the physical card.
- Must-include: `physical card` · `only in Aldora`
- Gold articles (all needed): What to bring to your appraisal appointment `[2026]`
- Traps: —
- What makes it hard: The checklist says mobile ID is accepted, but only for one state.
- Your call: keep / edit / drop

### q40 · conditional
**"I'm in Dunmore and trading in a car worth $9,000 on one of yours. How much of the trade-in counts against the sales tax?"**
- state: dunmore · tricky: time_boundary
- Perfect answer: $5,000. Since February 1, 2026, Dunmore caps the trade-in tax credit at $5,000 of trade-in value.
- Must-include: `$5,000`
- Gold articles (all needed): Trading in vs. selling outright `[2026]`
- Traps: —
- What makes it hard: The 2022 version says every state taxes only the difference, which suggests the full $9,000.
- Your call: keep / edit / drop

## checklist (6 drafts)

### q43 · checklist
**"I'm deployed overseas and my wife is selling our car in Corlan. We both own it. What does she need to bring?"**
- state: corlan · tricky: rule_conflict
- Perfect answer: Her photo ID, the registration, all keys, the title, NW-ODO-2, and your NW-MIL-1 signed electronically with a copy of your deployment orders. No notary is needed, even in Corlan.
- Must-include: `NW-MIL-1` · `deployment orders` · `NW-ODO-2`
- Gold articles (all needed): What to bring to your appraisal appointment `[2026]`; Selling while deployed `[2026]`; When more than one person owns the car `[2026]`
- Traps: Selling a family member's car for them `[2022]`
- What makes it hard: Three articles, and Corlan's notary rule plus the family-car article (notarized NW-POA-1) both point the wrong way.
- Your call: keep / edit / drop

### q44 · checklist
**"My car is paid off but I lost the title, and I'm in Eastvale. Walk me through everything I need to do to sell it."**
- state: eastvale
- Perfect answer: Get a duplicate title at an Eastvale motor vehicle office (same day at the main offices, 2 to 3 weeks by mail); you can get an offer and book meanwhile. Bring your photo ID, the registration, all keys, the duplicate title and NW-ODO-2. After the sale, return the plates to Eastvale within 10 days with the NW-PLT-1 receipt.
- Must-include: `duplicate title` · `NW-ODO-2` · `return the plates`
- Gold articles (all needed): Selling a paid-off car when the title is lost `[2022]`; Getting a duplicate title in Eastvale `[2022]`; What to bring to your appraisal appointment `[2026]`; What to do with your license plates `[2026]`
- Traps: Selling a car you are still paying off `[2022]`
- What makes it hard: Four articles, and the plate rule is easy to forget because it applies after the sale.
- Your call: keep / edit / drop

### q45 · checklist
**"My mom passed away and left me her paid-off car. It's a small estate and we're not going through probate. What do I bring?"**
- Perfect answer: The death certificate, affidavit NW-EST-1 signed by the heir, your photo ID, the title, the registration, all keys, and NW-ODO-2.
- Must-include: `death certificate` · `NW-EST-1` · `title`
- Gold articles (all needed): Selling a car you inherited `[2026]`; What to bring to your appraisal appointment `[2026]`
- Traps: Selling a family member's car for them `[2022]`
- What makes it hard: The family-car article (power of attorney) looks closer than the inheritance article, and a power of attorney ends at death.
- Your call: keep / edit / drop

### q46 · checklist
**"I'm selling a car that belongs to my LLC. What paperwork do I need?"**
- Perfect answer: NW-BUS-1 signed by an officer of the company, your photo ID, the company's EIN, the title, the registration, all keys and NW-ODO-2. Payment goes to the business bank account.
- Must-include: `NW-BUS-1` · `EIN`
- Gold articles (all needed): Selling a car owned by a business `[2022]`; What to bring to your appraisal appointment `[2026]`
- Traps: —
- What makes it hard: 'LLC' never appears in the KB, which says 'business' and 'company'.
- Your call: keep / edit / drop

### q47 · checklist
**"I owe more on my car than your offer, and my loan is with Coastal Credit Union. What do I bring to finish the sale?"**
- tricky: time_boundary
- Perfect answer: A 15-day payoff letter from Coastal (it isn't in the e-payoff network; or sign NW-LPA-1 so Northwind requests it), plus a cashier's check or debit card for the difference, your photo ID, the registration, all keys and NW-ODO-2.
- Must-include: `payoff letter` · `cashier's check or debit`
- Gold articles (all needed): If you owe more than our offer `[2026]`; Getting a payoff letter from your lender `[2026]`; Lenders in our e-payoff network `[2026]`; What to bring to your appraisal appointment `[2026]`
- Traps: —
- What makes it hard: Whether Coastal needs a letter depends on the network list, and the 2022 version still allows personal checks.
- Your call: keep / edit / drop

### q48 · checklist
**"Before I hand my car over to you, what should I do about my insurance, plates, toll tag and all that? I'm in Brevin."**
- state: brevin · tricky: rule_conflict
- Perfect answer: Keep the car insured until the sale is complete, then cancel. Leave the plates on the car (in Brevin, plates stay with the vehicle). Remove the toll tag, clear garage codes and unpair your phone.
- Must-include: `keep insurance until` · `leave the plates` · `toll tag`
- Gold articles (all needed): When to cancel your insurance `[2022]`; What to do with your license plates `[2026]`; Toll tags, garage codes and paired phones `[2022]`
- Traps: —
- What makes it hard: The 2022 plates article says always remove them, and three small topics live in three articles.
- Your call: keep / edit / drop

## unanswerable (6 drafts)

### q51 · unanswerable
**"Do you buy motorcycles?"**
- Perfect answer: The help center doesn't cover motorcycles; please contact a store.
- Must-include: (says it is not covered)
- Gold articles (all needed): —
- Traps: Selling your car to Northwind: how it works `[2026]`
- What makes it hard: 'How selling works' sounds relevant enough to answer 'yes, get an instant offer'.
- Your call: keep / edit / drop

### q52 · unanswerable
**"What interest rate would I get if I finance my next car with Northwind Auto Finance?"**
- Perfect answer: The help center doesn't cover financing rates or credit checks; please ask a store or Northwind Auto Finance.
- Must-include: (says it is not covered)
- Gold articles (all needed): —
- Traps: When will I get my title? (financed with Northwind) `[2022]`
- What makes it hard: The Northwind-financing title article names Northwind Auto Finance, so it looks like the place to answer from.
- Your call: keep / edit / drop

### q53 · unanswerable
**"Could you sell my car for me on consignment so I get a higher price?"**
- Perfect answer: The help center doesn't cover consignment; Northwind's process is an offer to buy the car outright.
- Must-include: (says it is not covered)
- Gold articles (all needed): —
- Traps: Selling a family member's car for them `[2022]`
- What makes it hard: 'Sell my car for me' matches 'Selling a family member's car for them' almost word for word.
- Your call: keep / edit / drop

### q54 · unanswerable
**"Do you buy imported right-hand-drive cars?"**
- Perfect answer: The help center doesn't say; please contact a store.
- Must-include: (says it is not covered)
- Gold articles (all needed): —
- Traps: Cars with aftermarket modifications `[2022]`
- What makes it hard: The modified-cars article talks about non-factory cars and invites a guess about the offer.
- Your call: keep / edit / drop

### q55 · unanswerable
**"Do you buy boats? And would you take my car if it has an open recall?"**
- tricky: messy_kb
- Perfect answer: For the car: yes, an open recall doesn't stop the sale or change the offer. Boats aren't covered by the help center; please contact a store.
- Must-include: `recall: yes` · `boats: not covered`
- Gold articles (all needed): Selling a car with an open recall `[2022]`
- Traps: —
- What makes it hard: Half answerable, with the unanswerable half first.
- Your call: keep / edit / drop

### q56 · unanswerable
**"How long does Ironwood Lease take to send you a dealer payoff quote?"**
- tricky: rule_conflict
- Perfect answer: The help center doesn't say how long Ironwood takes, and it doesn't matter here: Ironwood Lease doesn't allow third-party buyouts, so Northwind can't buy the leased car from them. You could buy it out yourself first.
- Must-include: `Ironwood doesn't allow third-party buyouts`
- Gold articles (all needed): Which leasing companies allow third-party buyouts `[2026]`
- Traps: Selling a car that you lease `[2022]`
- What makes it hard: The timing isn't in the KB, and the question hides a false premise (that a quote is coming at all).
- Your call: keep / edit / drop

---

## Seeds already kept (2026-11-13), for reference

### q01 · exact · seed 1A
**"My car is leased through Harbor. Can I sell it to you?"**
- tricky: messy_input
- Perfect answer: Not directly. Harbor Leasing doesn't allow third-party buyouts, so Northwind can't buy the car from them. You could buy it out yourself first, or return it at the end of the lease.
- Must-include: `no` · `Harbor Leasing`
- Gold articles (all needed): Which leasing companies allow third-party buyouts `[2026]`
- Traps: —
- What makes it hard: 'Harbor' matches Harbor Leasing (a leasing company) and Harbor Trust Bank (a lender); 'leased' is the only clue. Embeddings can't tell company names apart.

### q02 · exact · seed 1B
**"Which form do I sign so you can get the payoff number, NW-LPA-1 or NW-LSE-1? It's a lease."**
- tricky: messy_input
- Perfect answer: NW-LSE-1. It's the lease buyout authorization, which lets Northwind request the dealer payoff quote from your leasing company. NW-LPA-1 is for loans.
- Must-include: `NW-LSE-1`
- Gold articles (any one is enough): Selling a car that you lease `[2022]`; Getting a payoff letter from your lender `[2026]`
- Traps: —
- What makes it hard: The two codes differ by two letters and both 'let Northwind get a payoff number'. text_en splits codes into tokens and embeddings blur them; lease vs. loan is the only real difference.

### q09 · semantic · seed 2A
**"The bank still has the pink slip because I haven't finished paying the car off. Can I still sell it to you?"**
- tricky: messy_input
- Perfect answer: Yes. While a loan is open, your lender holds the title. Northwind pays the lender off from your offer, so you don't need the title in hand.
- Must-include: `yes` · `pay off the lender`
- Gold articles (all needed): Selling a car you are still paying off `[2022]`
- Traps: Selling a paid-off car when the title is lost `[2022]`
- What makes it hard: 'Pink slip' and 'bank' share no words with 'title' and 'lienholder'; the lost-title article ('we cannot buy without a title') looks closest.

### q10 · semantic · seed 2B
**"My father passed away in March and the car is still in his name. I'd like to sell it."**
- tricky: rule_conflict
- Perfect answer: You can sell it as his heir or the executor. Bring the death certificate and either the court letters or, for a small estate, affidavit NW-EST-1.
- Must-include: `NW-EST-1` · `death certificate`
- Gold articles (all needed): Selling a car you inherited `[2026]`
- Traps: Selling a family member's car for them `[2022]`
- What makes it hard: No 'inherit', 'heir' or 'estate' in the question. The family-car article looks like a perfect match but needs a power of attorney, which ends when the person dies.

### q17 · multi_hop · seed 3A
**"I still have a loan with Bayline Credit Union. Do I need to get a payoff letter before I come in?"**
- tricky: rule_conflict
- Perfect answer: No. Bayline is in Northwind's e-payoff network, so Northwind confirms the payoff with them directly the same day, with no letter needed.
- Must-include: `no` · `e-payoff` · `same day`
- Gold articles (all needed): Lenders in our e-payoff network `[2026]`
- Traps: —
- What makes it hard: The payoff-letter article is the closest match and says to bring a letter. The exception lives in the lender record (Bayline is in the network) and the e-payoff article.

### q18 · multi_hop · seed 3B
**"I lease from Crescent and your offer is higher than my buyout. Do I get the extra money?"**
- tricky: time_boundary
- Perfect answer: Yes. Since February 1, 2026 Crescent allows third-party buyouts, and Crescent passes the difference to you.
- Must-include: `yes` · `since 2026`
- Gold articles (all needed): Which leasing companies allow third-party buyouts `[2026]`; If our offer is more than your lease buyout `[2022]`
- Traps: —
- What makes it hard: Two articles (which lessors allow buyouts; who keeps the equity), and the 2022 buyout article says Crescent doesn't allow it.

### q19 · multi_hop · seed 8B
**"my lein holder is harbor, they said call u guys for the payof number"**
- tricky: messy_input
- Perfect answer: Harbor Trust Bank isn't in Northwind's e-payoff network, so a 15-day payoff letter is needed. You can request it yourself, or sign NW-LPA-1 and Northwind requests it for you.
- Must-include: `payoff letter` · `NW-LPA-1`
- Gold articles (all needed): Lenders in our e-payoff network `[2026]`; Getting a payoff letter from your lender `[2026]`
- Traps: Which leasing companies allow third-party buyouts `[2026]`; Selling a car that you lease `[2022]`
- What makes it hard: Two typos ('lein', 'payof') and an ambiguous 'harbor'. 'Lienholder' means a loan, so it's Harbor Trust Bank, not Harbor Leasing.

### q25 · temporal · seed 4A
**"I got my offer on January 28 and I can't come in until February 4. The website says offers last 5 days. Did mine expire?"**
- asked on 2026-02-02 · tricky: time_boundary
- Perfect answer: No. Offers issued before February 1, 2026 keep the old 7-day terms, so yours is good through February 4.
- Must-include: `still valid` · `7 days`
- Gold articles (all needed): How long is my offer good for? `[2026]`
- Traps: —
- What makes it hard: The 2026 headline rule says it expired; only the transition clause inside the 2026 article gives the right answer, so filtering to current versions isn't enough.

### q26 · temporal · seed 4B
**"My mom signed the old notarized power of attorney for me back in January. My appointment is July 10. Can I still use it?"**
- asked on 2026-06-20 · rules as of 2026-07-10 · tricky: time_boundary, messy_kb
- Perfect answer: No. NW-POA-1 forms signed before February 1 are accepted only until June 30, 2026. She needs to sign NW-POA-2, which can be signed electronically.
- Must-include: `no` · `June 30` · `NW-POA-2`
- Gold articles (all needed): When more than one person owns the car `[2026]`
- Traps: Selling a family member's car for them `[2022]`
- What makes it hard: The code is never said ('the old notarized one' = NW-POA-1), the deadline falls between the question and the appointment, and an unchanged article still cites NW-POA-1 as current.

### q33 · conditional · seed 5A
**"I live in Corlan. My brother co-owns the car but he's deployed overseas with the Army. Does his power of attorney have to be notarized?"**
- state: corlan · tricky: rule_conflict
- Perfect answer: No. A deployed owner can sign NW-MIL-1, which replaces a notarized power of attorney in every state, including Corlan.
- Must-include: `no` · `NW-MIL-1`
- Gold articles (any one is enough): Selling while deployed `[2026]`; When more than one person owns the car `[2026]`
- Traps: Selling a family member's car for them `[2022]`; Getting a duplicate title in Corlan `[2022]`
- What makes it hard: The co-owners article says Corlan always requires a notary, the obvious and wrong answer here: an exception to an exception.

### q34 · conditional · seed 5B
**"I moved from Eastvale to Brevin last year, but the car is still registered in Eastvale. What do I do with the plates when I sell?"**
- state: brevin · tricky: rule_conflict
- Perfect answer: Plates follow the state that issued them. They're Eastvale plates, so return them to Eastvale within 10 days and keep the NW-PLT-1 receipt.
- Must-include: `return` · `10 days` · `NW-PLT-1`
- Gold articles (any one is enough): What to do with your license plates `[2026]`; Selling a car registered in another state `[2026]`
- Traps: —
- What makes it hard: Two states in one question. Brevin's rule (plates stay on the car) matches where the customer lives, and it's the wrong one.

### q35 · conditional · seed 8A
**"Since you guys won't buy a car unless I have the title in my hand, I guess I have to pay off my whole loan first?"**
- tricky: rule_conflict
- Perfect answer: No. You don't need the title or to pay the loan off first. Your lender holds the title, and Northwind pays the lender from your offer.
- Must-include: `no` · `pays the lender`
- Gold articles (all needed): Selling a car you are still paying off `[2022]`
- Traps: Selling a paid-off car when the title is lost `[2022]`
- What makes it hard: A false premise. The lost-title article seems to confirm it ('we cannot buy ... without a title'), and bots tend to agree with the user.

### q41 · checklist · seed 6A
**"I inherited my uncle's car in Brevin. There's still a loan on it and nobody can find the title. What do I need to bring to sell it?"**
- state: brevin · tricky: rule_conflict
- Perfect answer: You don't need the title: the lender holds it while the loan is open. Bring your photo ID, the death certificate, court letters or NW-EST-1 for a small estate, a 15-day payoff letter (not needed if the lender is in the e-payoff network), a current registration (Brevin requires it), all keys, and NW-ODO-2.
- Must-include: `no duplicate title needed` · `NW-EST-1` · `payoff letter`
- Gold articles (all needed): Selling a car you inherited `[2026]`; Selling a car you are still paying off `[2022]`; Getting a payoff letter from your lender `[2026]`; What to bring to your appraisal appointment `[2026]`; My registration is expired `[2022]`
- Traps: Selling a paid-off car when the title is lost `[2022]`; Getting a duplicate title in Brevin `[2022]`
- What makes it hard: The lost-title and Brevin duplicate-title articles look most relevant and would send the customer on a 4 to 6 week detour that isn't needed. The real items are spread across five articles.

### q42 · checklist · seed 6B
**"I want to sell my leased car using home pickup. I'm in Dunmore. What do I need to have ready?"**
- state: dunmore · tricky: rule_conflict
- Perfect answer: Home pickup isn't available in Dunmore, so you'll need to bring the car to a store. Bring your photo ID, the registration, all keys, the dealer payoff quote from your leasing company (or sign NW-LSE-1 so Northwind requests it), and NW-ODO-2.
- Must-include: `no home pickup in Dunmore` · `dealer payoff quote`
- Gold articles (all needed): Home pickup service `[2026]`; Selling a car that you lease `[2022]`; What to bring to your appraisal appointment `[2026]`
- Traps: —
- What makes it hard: The checklist rests on a premise that's false in this state; a bot that just collects requirements lists NW-PU-1 and pickup steps.

### q49 · unanswerable · seed 7A
**"Can you buy my car if it's registered in Canada?"**
- Perfect answer: The help center doesn't cover cars registered outside the country; please contact a store.
- Must-include: (says it is not covered)
- Gold articles (all needed): —
- Traps: Selling a car registered in another state `[2026]`
- What makes it hard: 'Selling a car registered in another state' is a very close match, and a bot will happily apply state rules to another country.

### q50 · unanswerable · seed 7B
**"My car has an open recall and an open insurance claim from a hailstorm. Will you still buy it?"**
- tricky: messy_kb
- Perfect answer: The open recall isn't a problem: Northwind still buys cars with open recalls. The help center doesn't cover open insurance claims, so please ask a store about that part.
- Must-include: `recall: yes` · `insurance claim: not covered`
- Gold articles (all needed): Selling a car with an open recall `[2022]`
- Traps: When to cancel your insurance `[2022]`
- What makes it hard: Half of it is answerable; bots tend to answer everything from the half they found, or refuse everything.
