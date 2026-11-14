# Seed question candidates (drafted by Claude, chosen by Tianyi)

Two candidates (A and B) per type. Each one aims at at least one tricky case from `docs/KB_OUTLINE.md`. For each slot, keep one or both, edit, or drop. The ones you keep become the seed questions and set the style for the rest of the gold set.

How to review one candidate, in about a minute:
1. Would a real customer send this? If not, drop it or reword it in your own words.
2. Is the "Perfect answer" right according to the outline? If not, fix it.
3. Do you agree with "What makes it hard"? This line is what makes a question worth keeping.

Fields: **Asked on** blank = the cookbook's "today", 2026-11-01. **State** blank = the customer didn't say. **Must-include** = short facts an answer is graded on. Tricky tags: `time_boundary`, `rule_conflict`, `messy_input`, `messy_kb`.

Mark each candidate: `Your call: keep / edit / drop`.

---

## 1. exact: a name or code has to match exactly

### 1A
**"My car is leased through Harbor. Can I sell it to you?"**
- Asked on: — · State: —
- Perfect answer: Not directly. Harbor Leasing doesn't allow third-party buyouts, so Northwind can't buy the car from them.
- Must-include: `no` · `Harbor Leasing`
- What makes it hard: "Harbor" matches two records, Harbor Leasing (a leasing company) and Harbor Trust Bank (a lender), and the word "leased" is the only clue to which one. Vector search can't tell company names apart.
- Tricky: `messy_input` (near-identical names)
- Why I picked it: it shows an exact lookup of a structured record (the `lessors` collection) alongside text search, and a wrong "yes" sends the customer on a wasted trip.
- Your call:

### 1B
**"Which form do I sign so you can get the payoff number, NW-LPA-1 or NW-LSE-1? It's a lease."**
- Asked on: — · State: —
- Perfect answer: NW-LSE-1. It's the lease buyout authorization, which lets Northwind request the dealer payoff quote from your leasing company. NW-LPA-1 is for loans.
- Must-include: `NW-LSE-1`
- What makes it hard: the two codes differ by two letters and both "let Northwind get a payoff number". `text_en` breaks the codes into tokens, and embeddings blur them together. Lease versus loan is the only real difference.
- Tricky: `messy_input`
- Why I picked it: it shows why codes get their own exact-match field (see issues.md, I-002), and it's an entity trap: payoff letter (loan) versus dealer payoff quote (lease).
- Your call:

---

## 2. semantic: same meaning, different words

### 2A
**"The bank still has the pink slip because I haven't finished paying the car off. Can I still sell it to you?"**
- Asked on: — · State: —
- Perfect answer: Yes. While a loan is open, your lender holds the title. Northwind pays the lender off from your offer, so you don't need the title in hand.
- Must-include: `yes` · `pay off the lender`
- What makes it hard: "pink slip" and "bank" share no words with "title" and "lienholder". The lost-title article ("we cannot buy without a title") is the trap that looks closest.
- Tricky: `messy_input` (slang)
- Why I picked it: it's the origin story (a retailer's chatbot that said no title, no sale) told in slang. If vector search lands on the lost-title article, the bot gives exactly the wrong answer the chatbot gave.
- Your call:

### 2B
**"My father passed away in March and the car is still in his name. I'd like to sell it."**
- Asked on: — · State: —
- Perfect answer: You can sell it as his heir or the executor. Bring the death certificate and either the court letters or, for a small estate, affidavit NW-EST-1.
- Must-include: `NW-EST-1` · `death certificate`
- What makes it hard: no "inherit", "heir" or "estate" in the question. The trap is "Selling a family member's car for them", which looks like a perfect match but needs a power of attorney, and a power of attorney ends when the person dies.
- Tricky: `rule_conflict`
- Why I picked it: the most similar article is confidently wrong, and the right one shares almost no words with the question. That's the main reason to use vectors and still check the answer.
- Your call:

---

## 3. multi_hop: the answer needs a second article

### 3A
**"I still have a loan with Bayline Credit Union. Do I need to get a payoff letter before I come in?"**
- Asked on: — · State: —
- Perfect answer: No. Bayline is in Northwind's e-payoff network, so Northwind confirms the payoff with them directly the same day, with no letter needed.
- Must-include: `no` · `e-payoff` · `same day`
- What makes it hard: the payoff-letter article is the closest match and says you need a letter. The exception lives in two other places: the lender record (Bayline → in the network) and the e-payoff article.
- Tricky: `rule_conflict` (general rule vs. exception)
- Why I picked it: a clean hop from a question entity (Bayline) to a record to an article. That's the graph path vector RAG can't follow.
- Your call:

### 3B
**"I lease from Crescent and your offer is higher than my buyout. Do I get the extra money?"**
- Asked on: — · State: —
- Perfect answer: Yes. Since Feb 1, 2026 Crescent allows third-party buyouts, and Crescent passes the difference to you.
- Must-include: `yes` · `since 2026` (or "allowed now")
- What makes it hard: it takes two articles (which lessors allow buyouts; who keeps the equity) plus the lessor's own rule. The 2022 version of the buyout article says Crescent doesn't allow it.
- Tricky: `time_boundary`
- Why I picked it: multi-hop and temporal at once, and the stale version gives a confident "no".
- Your call:

---

## 4. temporal: the answer changed on 2026-02-01

### 4A
**"I got my offer on January 28 and I can't come in until February 4. The website says offers last 5 days. Did mine expire?"**
- Asked on: 2026-02-02 · State: —
- Perfect answer: No. Offers issued before Feb 1, 2026 keep the old 7-day terms, so yours is good through Feb 4.
- Must-include: `still valid` · `7 days`
- What makes it hard: both versions are wrong on their own. The 2026 article's headline rule (5 days) says it expired, and the 2022 article is superseded. Only the transition rule inside the 2026 article gives the right answer, so filtering to current versions alone isn't enough.
- Tricky: `time_boundary`
- Why I picked it: it shows that "use the latest version" isn't a complete answer to versioning.
- Your call:

### 4B
**"My mom signed the old notarized power of attorney for me back in January. My appointment is July 10. Can I still use it?"**
- Asked on: 2026-06-20 · State: —
- Perfect answer: No. NW-POA-1 forms signed before Feb 1 are accepted only until June 30, 2026. She needs to sign NW-POA-2, which can be signed electronically.
- Must-include: `no` · `June 30` · `NW-POA-2`
- What makes it hard: the customer never says the code ("the old notarized one" = NW-POA-1), the deadline falls between the question date and the appointment, and an unchanged article still cites NW-POA-1 as if it were current.
- Tricky: `time_boundary` · `messy_kb`
- Why I picked it: three traps in one realistic message, and the "KB rot" article makes the stale answer look official.
- Your call:

---

## 5. conditional: depends on the state or the situation

### 5A
**"I live in Corlan. My brother co-owns the car but he's deployed overseas with the Army. Does his power of attorney have to be notarized?"**
- Asked on: — · State: Corlan
- Perfect answer: No. A deployed owner can sign NW-MIL-1, which replaces a notarized power of attorney in every state, including Corlan.
- Must-include: `no` · `NW-MIL-1`
- What makes it hard: the co-owners article says Corlan always requires a notary, which is the obvious answer and wrong here. It's an exception to an exception.
- Tricky: `rule_conflict`
- Why I picked it: precedence between rules is where retrieve-the-closest-article fails, and a graph (state → rule → exception) makes the precedence visible.
- Your call:

### 5B
**"I moved from Eastvale to Brevin last year, but the car is still registered in Eastvale. What do I do with the plates when I sell?"**
- Asked on: — · State: Brevin (lives) / Eastvale (registration)
- Perfect answer: Follow the rule of the state that issued the plates. They're Eastvale plates, so return them to Eastvale within 10 days and keep the NW-PLT-1 receipt.
- Must-include: `return` · `10 days` · `NW-PLT-1`
- What makes it hard: two states in one question. Brevin's rule (plates stay with the car) matches where the customer lives, but it's the wrong one.
- Tricky: `rule_conflict`
- Why I picked it: a state filter needs the *right* state, not just any state mentioned.
- Your call:

---

## 6. checklist: the customer needs the complete list

### 6A
**"I inherited my uncle's car in Brevin. There's still a loan on it and nobody can find the title. What do I need to bring to sell it?"**
- Asked on: — · State: Brevin
- Perfect answer: You don't need the title, because the lender holds it while the loan is open. Bring your photo ID, the death certificate, court letters or NW-EST-1 for a small estate, a 15-day payoff letter (not needed if the lender is in the e-payoff network), a current registration (Brevin requires it), all keys, and NW-ODO-2.
- Must-include: `no duplicate title needed` · `NW-EST-1` · `payoff letter`
- What makes it hard: the lost-title and Brevin duplicate-title articles look most relevant and would send the customer on a 4–6 week detour that isn't needed. The real items are spread across four or five articles.
- Tricky: `rule_conflict` (three conditions at once)
- Why I picked it: the strongest "graph wins" question. Completeness plus a confident wrong detour.
- Your call:

### 6B
**"I want to sell my leased car using home pickup. I'm in Dunmore. What do I need to have ready?"**
- Asked on: — · State: Dunmore
- Perfect answer: Home pickup isn't available in Dunmore, so you'll need to bring the car to a store. Bring your photo ID, the registration, all keys, the dealer payoff quote from your leasing company (or sign NW-LSE-1 so Northwind requests it), and NW-ODO-2.
- Must-include: `no home pickup in Dunmore` · `dealer payoff quote`
- What makes it hard: the checklist rests on a premise that's false in this state. A bot that just collects requirements will list NW-PU-1 and pickup steps.
- Tricky: `rule_conflict`
- Why I picked it: checklist and conditional together, and the right answer starts by correcting the plan.
- Your call:

---

## 7. unanswerable: the KB doesn't say

### 7A
**"Can you buy my car if it's registered in Canada?"**
- Asked on: — · State: —
- Perfect answer: The help center doesn't cover cars registered outside the country; please contact a store.
- Must-include: (says it isn't covered)
- What makes it hard: "Selling a car registered in another state" is a very close match, and a bot will happily apply state rules to another country.
- Tricky: none
- Why I picked it: the cleanest test of refusing on a near miss.
- Your call:

### 7B
**"My car has an open recall and an open insurance claim from a hailstorm. Will you still buy it?"**
- Asked on: — · State: —
- Perfect answer: The open recall isn't a problem; Northwind still buys cars with open recalls. The help center doesn't cover open insurance claims, so please ask a store about that part.
- Must-include: `recall: yes` · `insurance claim: not covered`
- What makes it hard: half of it is answerable. Bots tend to answer everything confidently from the half they found, or refuse everything.
- Tricky: `messy_kb` (half answerable)
- Why I picked it: tests answering only what the sources support, which is the faithfulness check in chapter 2.
- Your call:

---

## 8. tricky (free slot)

### 8A
**"Since you guys won't buy a car unless I have the title in my hand, I guess I have to pay off my whole loan first?"**
- Asked on: — · State: —
- Perfect answer: No. You don't need the title or to pay the loan off first. Your lender holds the title, and Northwind pays the lender from your offer.
- Must-include: `no` · `pays the lender`
- What makes it hard: a false premise. The lost-title article seems to confirm it ("we cannot buy … without a title"), and bots tend to agree with the user.
- Tricky: `rule_conflict` (false premise)
- Why I picked it: this is the origin story's moment. The signature question for the whole cookbook.
- Your call:

### 8B
**"my lein holder is harbor, they said call u guys for the payof number"**
- Asked on: — · State: —
- Perfect answer: Harbor Trust Bank isn't in Northwind's e-payoff network, so we need a 15-day payoff letter. You can request it yourself, or sign NW-LPA-1 and Northwind will request it for you.
- Must-include: `payoff letter` · `NW-LPA-1`
- What makes it hard: two typos ("lein", "payof"), and "harbor" is ambiguous. "Lienholder" means a loan, so it's Harbor Trust Bank, not Harbor Leasing.
- Tricky: `messy_input`
- Why I picked it: it shows ArangoSearch fuzzy matching (`LEVENSHTEIN_MATCH`) and entity disambiguation by context, and it's how people actually type.
- Your call:

---

## Facts the articles must state for these questions to work
These come from the outline. Writing the questions first just makes them explicit, so the articles get them right.
- A power of attorney ends when the person who signed it dies (in `selling_for_someone_else` and `inherited_car`).
- Plates follow the state that issued them (`license_plates`).
- Crescent passes lease equity to the customer (`lease_equity`, a per-lessor table).
- NW-LSE-1 lets Northwind request the dealer payoff quote; NW-LPA-1 is the loan version (`leased_car`, `payoff_letter`).
- While a loan is open the lender holds the title, so a missing title isn't a problem (`selling_with_loan`).
- E-payoff network lenders need no payoff letter (`epayoff_network`).
