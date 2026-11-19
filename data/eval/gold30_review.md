# Gold set review: the 30 questions to freeze

**30 questions** (exact 3 · semantic 3 · multi_hop 7 · temporal 5 · conditional 4 · checklist 5 · unanswerable 3). **0 drafts to review** (below, by type), then 30 seeds you kept on 2026-11-13, then the 26 questions in reserve.
Generated from `data/eval/gold.json` and `gold_reserve.json` by `scripts/render_gold_review.py` (`make review`); edit the JSON, not this file. "Today" is 2026-11-01; a tag like `[2026]` is the article version.

> [!todo] Your review (about 25 minutes)
> For each draft: would a real customer send it? Is the perfect answer right? Are the gold articles the ones you would want retrieved?
> Reply in shorthand, e.g. `q21 keep`, `q29 edit: ...`, `q48 drop, swap in q46`. Anything you don't mention counts as keep.
> The 30 were chosen from the questions alone: no retrieval method existed yet (D-024). After your review the set is frozen (commit + sha256).
> State names were changed to real ones today (D-023); the seeds differ from what you kept only in those names.

---

## Seeds already kept (30), for reference

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

### q04 · exact
**"What's form NW-LRL-1 for?"**
- Perfect answer: It's the lien release request. If your loan is paid off but the title still lists the lender, sign NW-LRL-1 and Northwind contacts the lender for the release; it can add 1 to 2 weeks.
- Must-include: `lien release`
- Gold articles (all needed): My loan is paid off but the lien is still on the title `[2022]`
- Traps: Getting a payoff letter from your lender `[2026]`
- What makes it hard: The question is only a code. Other lender-related forms (NW-LPA-1 in the payoff-letter article) look close to an embedding.

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

### q16 · semantic
**"Do I need to get rid of my stuff in the car's computer before you take it?"**
- Perfect answer: Yes. Unpair your phone, clear garage door codes, remove toll tags, and remove the car from any connected-car app.
- Must-include: `unpair your phone` · `garage`
- Gold articles (all needed): Toll tags, garage codes and paired phones `[2022]`
- Traps: When to cancel your insurance `[2022]`
- What makes it hard: 'Stuff in the car's computer' never says phone, toll tag or data.

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

### q21 · multi_hop
**"I'm using home pickup and I still owe Pinewood Federal. When does Pinewood get paid, and is anything taken out of what I get?"**
- Perfect answer: Pinewood Federal Credit Union is in the e-payoff network, so it's paid the same day. You get the offer minus the payoff, minus the $99 home pickup fee.
- Must-include: `same day` · `$99`
- Gold articles (all needed): Home pickup service `[2026]`; When and how you get paid `[2026]`; Lenders in our e-payoff network `[2026]`
- Traps: When and how you get paid `[2022]`
- What makes it hard: Three facts in three articles: the fee (home pickup), the payment timing (getting paid) and whether Pinewood is a network lender (e-payoff).

### q22 · multi_hop
**"My offer expired while I was waiting for a duplicate title from North Carolina. Do I have to start over, and will the price be the same?"**
- state: north_carolina
- Perfect answer: Yes, request a new offer; the amount reflects current market prices and may be higher or lower. North Carolina duplicates take 4 to 6 weeks, so book the appointment for when it arrives.
- Must-include: `new offer` · `higher or lower`
- Gold articles (all needed): Getting a duplicate title in North Carolina `[2022]`; How long is my offer good for? `[2026]`
- Traps: —
- What makes it hard: The duplicate-title article only says you 'may need a new one'; what happens to the price is in the offer article.

### q23 · multi_hop
**"I bought my car from you with a loan from Bayline Credit Union. Now I want to sell it back before it's paid off. Who has my title, and do I need a payoff letter?"**
- tricky: rule_conflict
- Perfect answer: Bayline holds the title until the loan is paid off. You can still sell: Northwind pays Bayline from your offer, and because Bayline is in the e-payoff network, no payoff letter is needed.
- Must-include: `Bayline holds the title` · `no payoff letter`
- Gold articles (all needed): When will I get my title? (outside lender) `[2022]`; Selling a car you are still paying off `[2022]`; Lenders in our e-payoff network `[2026]`
- Traps: When will I get my title? (financed with Northwind) `[2022]`
- What makes it hard: It starts on the buying side and ends on the selling side. The Northwind-financing title article looks closer but is the wrong lender.

### q24 · multi_hop
**"My dad passed away and his car is still financed with Lakeshore Bank. Do I need a payoff letter to sell it?"**
- Perfect answer: No payoff letter: Lakeshore Bank is in the e-payoff network. You still need the death certificate plus court letters or NW-EST-1, and Northwind pays the loan off from the offer.
- Must-include: `no payoff letter` · `death certificate`
- Gold articles (all needed): Selling a car you inherited `[2026]`; Selling a car you are still paying off `[2022]`; Lenders in our e-payoff network `[2026]`
- Traps: Selling a family member's car for them `[2022]`
- What makes it hard: Inherited → loan → network lender: three hops, and the family-car article (power of attorney) is a confident wrong turn.

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

### q28 · temporal
**"Back in December 2025 I got an offer. How many miles could I put on the car before it expired?"**
- rules as of 2025-12-15 · tricky: time_boundary
- Perfect answer: 300 miles, or 7 days, whichever came first. That was the rule until January 31, 2026.
- Must-include: `300 miles`
- Gold articles (all needed): How long is my offer good for? `[2022]`
- Traps: —
- What makes it hard: The question is about the past: the current 2026 version (250 miles) is the trap here, and filtering to 'today' picks it.

### q29 · temporal
**"Is Granite Bank in your e-payoff network? My appointment is next week."**
- asked on 2026-02-20 · rules as of 2026-02-27 · tricky: time_boundary
- Perfect answer: Not yet: Granite Bank joins on March 15, 2026. For next week's appointment, bring a payoff letter or sign NW-LPA-1 so Northwind requests one.
- Must-include: `not yet` · `March 15`
- Gold articles (all needed): Lenders in our e-payoff network `[2026]`
- Traps: —
- What makes it hard: The article lists Granite next to the network lenders; the joining date is the whole answer.

### q31 · temporal
**"Can you mail me a check for my car like you did for my friend in 2023?"**
- tricky: time_boundary
- Perfect answer: Not anymore. Northwind stopped mailing checks on February 1, 2026; you get a bank draft or a direct deposit (1 to 3 business days).
- Must-include: `no` · `direct deposit`
- Gold articles (all needed): When and how you get paid `[2026]`
- Traps: —
- What makes it hard: The friend's 2023 story matches the 2022 version, which offered mailed checks.

### q33 · conditional · seed 5A
**"I live in Georgia. My brother co-owns the car but he's deployed overseas with the Army. Does his power of attorney have to be notarized?"**
- state: georgia · tricky: rule_conflict
- Perfect answer: No. A deployed owner can sign NW-MIL-1, which replaces a notarized power of attorney in every state, including Georgia.
- Must-include: `no` · `NW-MIL-1`
- Gold articles (any one is enough): Selling while deployed `[2026]`; When more than one person owns the car `[2026]`
- Traps: Selling a family member's car for them `[2022]`; Getting a duplicate title in Georgia `[2022]`
- What makes it hard: The co-owners article says Georgia always requires a notary, the obvious and wrong answer here: an exception to an exception.

### q34 · conditional · seed 5B
**"I moved from California to North Carolina last year, but the car is still registered in California. What do I do with the plates when I sell?"**
- state: north_carolina · tricky: rule_conflict
- Perfect answer: Plates follow the state that issued them. They're California plates, so return them to California within 10 days and keep the NW-PLT-1 receipt.
- Must-include: `return` · `10 days` · `NW-PLT-1`
- Gold articles (any one is enough): What to do with your license plates `[2026]`; Selling a car registered in another state `[2026]`
- Traps: —
- What makes it hard: Two states in one question. North Carolina's rule (plates stay on the car) matches where the customer lives, and it's the wrong one.

### q35 · conditional · seed 8A
**"Since you guys won't buy a car unless I have the title in my hand, I guess I have to pay off my whole loan first?"**
- tricky: rule_conflict
- Perfect answer: No. You don't need the title or to pay the loan off first. Your lender holds the title, and Northwind pays the lender from your offer.
- Must-include: `no` · `pays the lender`
- Gold articles (all needed): Selling a car you are still paying off `[2022]`
- Traps: Selling a paid-off car when the title is lost `[2022]`
- What makes it hard: A false premise. The lost-title article seems to confirm it ('we cannot buy ... without a title'), and bots tend to agree with the user.

### q36 · conditional
**"I live in Texas. Can someone come pick up my car?"**
- Perfect answer: Not in Texas: home pickup isn't available there, so bring the car to a store.
- Must-include: `not available in Texas`
- Gold articles (all needed): Home pickup service `[2026]`
- Traps: —
- What makes it hard: The 2022 version says pickup is available in every state.

### q41 · checklist · seed 6A
**"I inherited my uncle's car in North Carolina. There's still a loan on it and nobody can find the title. What do I need to bring to sell it?"**
- state: north_carolina · tricky: rule_conflict
- Perfect answer: You don't need the title: the lender holds it while the loan is open. Bring your photo ID, the death certificate, court letters or NW-EST-1 for a small estate, a 15-day payoff letter (not needed if the lender is in the e-payoff network), a current registration (North Carolina requires it), all keys, and NW-ODO-2.
- Must-include: `no duplicate title needed` · `NW-EST-1` · `payoff letter`
- Gold articles (all needed): Selling a car you inherited `[2026]`; Selling a car you are still paying off `[2022]`; Getting a payoff letter from your lender `[2026]`; What to bring to your appraisal appointment `[2026]`; My registration is expired `[2022]`
- Traps: Selling a paid-off car when the title is lost `[2022]`; Getting a duplicate title in North Carolina `[2022]`
- What makes it hard: The lost-title and North Carolina duplicate-title articles look most relevant and would send the customer on a 4 to 6 week detour that isn't needed. The real items are spread across five articles.

### q42 · checklist · seed 6B
**"I want to sell my leased car using home pickup. I'm in Texas. What do I need to have ready?"**
- state: texas · tricky: rule_conflict
- Perfect answer: Home pickup isn't available in Texas, so you'll need to bring the car to a store. Bring your photo ID, the registration, all keys, the dealer payoff quote from your leasing company (or sign NW-LSE-1 so Northwind requests it), and NW-ODO-2.
- Must-include: `no home pickup in Texas` · `dealer payoff quote`
- Gold articles (all needed): Home pickup service `[2026]`; Selling a car that you lease `[2022]`; What to bring to your appraisal appointment `[2026]`
- Traps: —
- What makes it hard: The checklist rests on a premise that's false in this state; a bot that just collects requirements lists NW-PU-1 and pickup steps.

### q44 · checklist
**"My car is paid off but I lost the title, and I'm in California. Walk me through everything I need to do to sell it."**
- state: california
- Perfect answer: Get a duplicate title at a California motor vehicle office (same day at the main offices, 2 to 3 weeks by mail); you can get an offer and book meanwhile. Bring your photo ID, the registration, all keys, the duplicate title and NW-ODO-2. After the sale, return the plates to California within 10 days with the NW-PLT-1 receipt.
- Must-include: `duplicate title` · `NW-ODO-2` · `return the plates`
- Gold articles (all needed): Selling a paid-off car when the title is lost `[2022]`; Getting a duplicate title in California `[2022]`; What to bring to your appraisal appointment `[2026]`; What to do with your license plates `[2026]`
- Traps: Selling a car you are still paying off `[2022]`
- What makes it hard: Four articles, and the plate rule is easy to forget because it applies after the sale.

### q47 · checklist
**"I owe more on my car than your offer, and my loan is with Coastal Credit Union. What do I bring to finish the sale?"**
- tricky: time_boundary
- Perfect answer: A 15-day payoff letter from Coastal (it isn't in the e-payoff network; or sign NW-LPA-1 so Northwind requests it), plus a cashier's check or debit card for the difference, your photo ID, the registration, all keys and NW-ODO-2.
- Must-include: `payoff letter` · `cashier's check or debit`
- Gold articles (all needed): If you owe more than our offer `[2026]`; Getting a payoff letter from your lender `[2026]`; Lenders in our e-payoff network `[2026]`; What to bring to your appraisal appointment `[2026]`
- Traps: —
- What makes it hard: Whether Coastal needs a letter depends on the network list, and the 2022 version still allows personal checks.

### q48 · checklist
**"Before I hand my car over to you, what should I do about my insurance, plates, toll tag and all that? I'm in North Carolina."**
- state: north_carolina · tricky: rule_conflict
- Perfect answer: Keep the car insured until the sale is complete, then cancel. Leave the plates on the car (in North Carolina, plates stay with the vehicle). Remove the toll tag, clear garage codes and unpair your phone.
- Must-include: `keep insurance until` · `leave the plates` · `toll tag`
- Gold articles (all needed): When to cancel your insurance `[2022]`; What to do with your license plates `[2026]`; Toll tags, garage codes and paired phones `[2022]`
- Traps: —
- What makes it hard: The 2022 plates article says always remove them, and three small topics live in three articles.

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

### q52 · unanswerable
**"What interest rate would I get if I finance my next car with Northwind Auto Finance?"**
- Perfect answer: The help center doesn't cover financing rates or credit checks; please ask a store or Northwind Auto Finance.
- Must-include: (says it is not covered)
- Gold articles (all needed): —
- Traps: When will I get my title? (financed with Northwind) `[2022]`
- What makes it hard: The Northwind-financing title article names Northwind Auto Finance, so it looks like the place to answer from.

---

## Reserve (26): not in the 30, used for debugging. Swap any of these in if you prefer it.

| id | type | question | note |
|---|---|---|---|
| q03 | exact | Does Apex Lease Co charge anything if you buy out my lease? |  |
| q05 | exact | Do I need NW-EST-1 or court letters to sell my late father's car? |  |
| q06 | exact | What is the NW-PU-1 form, and do I have to pay for it? |  |
| q07 | exact | Does Bluewater Leasing let you buy my leased car? |  |
| q08 | exact | What do I put on the odometer form if my odometer was replaced? |  |
| q11 | semantic | My car got totaled by the insurance company years ago and then it was fixed up. Would you still take it? |  |
| q12 | semantic | My car won't even start anymore. Is it worth contacting you? |  |
| q13 | semantic | Someone called saying they're from your company and that I have to pay a processing fee before they can release the money for my car. Is that real? |  |
| q14 | semantic | My husband and I both own the car, but he's working abroad for a few months. How can I sell it without him here? |  |
| q15 | semantic | My autopay went out the same week you paid off my loan. Who sends me that money back? |  |
| q20 | multi_hop | I lease from Apex and your offer is $2,000 more than my buyout. How much of that do I get? | near-duplicate of seed q18 (lease equity with a different lessor) |
| q27 | temporal | Can I just drive over to one of your stores and have someone look at my car and give me a price? |  |
| q30 | temporal | In 2023 I tried to return a car I'd bought from you, 10 days after delivery, and they said it was too late. Was that right? |  |
| q32 | temporal | How much do you take off the offer if I only have one key? |  |
| q37 | conditional | My registration expired last month. I'm in North Carolina. Can I still sell this weekend? |  |
| q38 | conditional | I'm in Virginia. Do I need to bring my paper title? |  |
| q39 | conditional | Can I show my ID on my phone instead of my physical license? I live in California. |  |
| q40 | conditional | I'm in Texas and trading in a car worth $9,000 on one of yours. How much of the trade-in counts against the sales tax? |  |
| q43 | checklist | I'm deployed overseas and my wife is selling our car in Georgia. We both own it. What does she need to bring? |  |
| q45 | checklist | My mom passed away and left me her paid-off car. It's a small estate and we're not going through probate. What do I bring? |  |
| q46 | checklist | I'm selling a car that belongs to my LLC. What paperwork do I need? |  |
| q51 | unanswerable | Do you buy motorcycles? |  |
| q53 | unanswerable | Could you sell my car for me on consignment so I get a higher price? |  |
| q54 | unanswerable | Do you buy imported right-hand-drive cars? |  |
| q55 | unanswerable | Do you buy boats? And would you take my car if it has an open recall? |  |
| q56 | unanswerable | How long does Ironwood Lease take to send you a dealer payoff quote? |  |

Messy variants, off-topic messages and vague questions (35 drafts in `data/eval/candidates.json`) are not part of this freeze; they come later.
