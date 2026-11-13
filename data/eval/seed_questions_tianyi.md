# Seed questions (written by Tianyi)

Write one question per type (7), plus an optional 8th "tricky" one. Use only `docs/KB_OUTLINE.md`. The article text doesn't exist yet, on purpose, so the wording is yours and not the KB's. Your questions set the style for the rest of the gold set and are also reported as their own group.

## What each field means

| Field | Required? | What to write | Why it matters |
|---|---|---|---|
| **Question** | yes | Exactly what a customer would type into a support chat, in 1–3 sentences. It can be messy: extra backstory, slang, a typo, two questions in one. | This is the only thing the system sees. |
| **Asked on** | only if the date matters | The date the customer sends the message. Leave it blank to mean the cookbook's fixed "today", **2026-11-01**. Fill it in when the question is about the past ("back in 2023…") or falls near the rewrite on **2026-02-01**. | The same question can have a different correct answer before and after 2026-02-01. The system can only pick the right article version if it knows the date. |
| **Customer's state** | only if the customer says it | One of the fictional states, if the customer mentions it or support would know it from the account. Otherwise blank. | Some rules differ by state. With no state, a good answer gives the general rule and says it depends on the state, or asks. |
| **Perfect answer** | yes, roughly | What a great support agent would reply, in 1–2 sentences. | Turns into the reference answer. |
| **Must-include facts** | yes | 1–3 short, checkable items the answer must contain: a number, a form code, a yes/no, a name. | Chapter 2 grades the AI's answers by checking these facts. Long facts can't be checked. |
| **What makes it hard** | yes | One line: the mistake you expect a naive chatbot to make, and why. | **This is what makes a question useful.** Each question should catch one specific failure. If you can't name a failure, the question isn't testing anything. |

You don't need to know article keys. I'll fill in the gold articles (what a correct answer must cite) and the trap articles (what could fool the system) from your "Perfect answer" and "What makes it hard", and you check them.

## A good question
1. A real customer would send it.
2. The KB has one clear correct answer (except for type 7).
3. It aims at one weakness, written down in "What makes it hard".
4. A wrong answer would actually cost the customer something: a wasted trip, a missed deadline, a wrong form.
5. It doesn't reuse the outline's wording, especially for type 2.

---

## 1. exact: a name or code has to match exactly
**Tests:** a form code, a company name, or a defined term. Keyword search should win; embeddings blur codes and names together ("NW-POA-1" and "NW-POA-2" look almost identical to a vector).

*Example only, not used:*
- Question: "Is NW-ODO-1 still OK to bring to my appointment?"
- Asked on: (blank)
- Customer's state: (blank)
- Perfect answer: No. NW-ODO-1 was retired on Feb 1, 2026; bring NW-ODO-2 instead.
- Must-include facts: "no", "NW-ODO-2"
- What makes it hard: the 2022 checklist mentions NW-ODO-1, and vector search can't tell the two codes apart.

**Yours:**
- Question:
- Asked on:
- Customer's state:
- Perfect answer:
- Must-include facts:
- What makes it hard:

## 2. semantic: same meaning, different words
**Tests:** the customer describes the situation in their own words and shares almost no words with the article. Vector search should win; keyword search finds nothing to match.

*Example only, not used:*
- Question: "I'm underwater on my car loan, can I still get rid of the car through you?"
- Asked on: (blank) · Customer's state: (blank)
- Perfect answer: Yes. You pay the difference between the loan and our offer at the appointment, by cashier's check or debit card.
- Must-include facts: "yes", "pay the difference", "cashier's check or debit"
- What makes it hard: the article says "negative equity" and "owe more than our offer"; the question uses neither phrase.

**Yours:**
- Question:
- Asked on:
- Customer's state:
- Perfect answer:
- Must-include facts:
- What makes it hard:

## 3. multi_hop: the answer needs a second article
**Tests:** the first article is easy to find, but a full answer needs another one it links to, and that one doesn't look like the question.

*Example only, not used:*
- Question: "I still owe on my car and I don't have the title. Can I sell it to you?"
- Asked on: (blank) · Customer's state: (blank)
- Perfect answer: Yes, your lender holds the title. Get a 15-day payoff letter, or sign NW-LPA-1 so we request it for you, and bring it to your appointment.
- Must-include facts: "yes", "payoff letter", "15-day"
- What makes it hard: the lost-title article looks more similar and says you can't sell without a title, and the payoff-letter article doesn't look like the question.

**Yours:**
- Question:
- Asked on:
- Customer's state:
- Perfect answer:
- Must-include facts:
- What makes it hard:

## 4. temporal: the answer changed on 2026-02-01
**Tests:** picking the article version that was in effect on the date that matters. Ask about now (the 2022 version is the trap), or about the past (the 2026 version is the trap).

*Example only, not used:*
- Question: "Back in 2023 I paid the gap on my loan with a personal check. My friend wants to do the same next week. Can she?"
- Asked on: (blank)
- Customer's state: (blank)
- Perfect answer: Not anymore. Since Feb 1, 2026 we only take a cashier's check or debit card for negative equity.
- Must-include facts: "no", "cashier's check or debit"
- What makes it hard: the story is about 2023, when the 2022 article allowed personal checks, but the answer has to be about now.

**Yours:**
- Question:
- Asked on:
- Customer's state:
- Perfect answer:
- Must-include facts:
- What makes it hard:

## 5. conditional: the answer depends on the state or the situation
**Tests:** using the article for the customer's own state or situation, not a look-alike for another one.

*Example only, not used:*
- Question: "Lost my title. I'm in Brevin. How long before I can sell you the car?"
- Asked on: (blank)
- Customer's state: Brevin
- Perfect answer: You need a duplicate title first; in Brevin that takes 4–6 weeks. You can get an offer and book an appointment while you wait.
- Must-include facts: "duplicate title", "4–6 weeks"
- What makes it hard: three duplicate-title articles look almost the same, and only the Brevin one is right.

**Yours:**
- Question:
- Asked on:
- Customer's state:
- Perfect answer:
- Must-include facts:
- What makes it hard:

## 6. checklist: the customer needs the complete list
**Tests:** collecting every requirement when the items are spread across several articles. Missing one item means the customer makes a wasted trip.

*Example only, not used:*
- Question: "My sister and I co-own a leased car and she can't come. What do we bring?"
- Asked on: (blank) · Customer's state: (blank)
- Perfect answer: Your photo ID, the registration, all keys, the dealer payoff quote from the leasing company, and NW-POA-2 signed by your sister.
- Must-include facts: "dealer payoff quote", "NW-POA-2", "photo ID"
- What makes it hard: the items come from three articles (checklist, leased car, co-owners), and top-3 search usually returns only one or two of them.

**Yours:**
- Question:
- Asked on:
- Customer's state:
- Perfect answer:
- Must-include facts:
- What makes it hard:

## 7. unanswerable: the KB doesn't say
**Tests:** saying "I don't know, here's who can help" instead of answering from a look-alike article.

*Example only, not used:*
- Question: "Will you buy my boat?"
- Asked on: (blank) · Customer's state: (blank)
- Perfect answer: Our help center doesn't cover boats; please contact the store.
- Must-include facts: (it says it doesn't know)
- What makes it hard: the "how selling works" article sounds relevant, so the bot may say "yes, get an instant offer".

**Yours:**
- Question:
- Asked on:
- Customer's state:
- Perfect answer:
- Must-include facts:
- What makes it hard:

## 8. tricky (optional): pick one from the tricky-case list in the outline
**Yours:**
- Question:
- Asked on:
- Customer's state:
- Perfect answer:
- Must-include facts:
- What makes it hard:
