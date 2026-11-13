# Seed questions (one per type, written by Tianyi)

Write each question the way a customer would type it into a support chat. Use only `docs/KB_OUTLINE.md`; the article text doesn't exist yet, on purpose, so the wording is yours and not the KB's.

These 7 questions set the style for the rest of the gold set (about 40 questions). They are marked `author: tianyi` and reported separately as well.

For each question, optionally add: the date the customer is asking (`as of`), their state, and a one-line expected answer. Leave anything you're unsure of blank.

---

## 1. exact
The question contains an exact name or code from the KB: a form code, a leasing company, or a defined term such as "dealer payoff quote". Keyword search should be strong here; embeddings tend to blur codes and names.
*Example only, not used:* "Is NW-ODO-1 still OK to bring?"

- Question:
- As of / state:
- Expected answer:

## 2. semantic
The customer describes their situation in their own words and shares almost no words with the article that answers it. Vector search should be strong here.
*Example only, not used:* "I'm underwater on my car loan, can I still sell?"

- Question:
- As of / state:
- Expected answer:

## 3. multi_hop
A full answer needs two or more articles that link to each other, and the second one does not look like the question.
*Example only, not used:* "I still owe on my car and I don't have the title. Can I sell it to you?"

- Question:
- As of / state:
- Expected answer:

## 4. temporal
The answer changed on 2026-02-01. Ask about now (the 2026 version is right and the 2022 version is a trap), or about a date before the change (the 2022 version is right).
*Example only, not used:* "Back in 2023, how long did my offer last?"

- Question:
- As of / state:
- Expected answer:

## 5. conditional
The answer depends on the customer's state (Aldora, Brevin, Corlan) or on their situation. An article for another state or situation is the trap.
*Example only, not used:* "I live in Brevin and lost my title. How long until I can sell?"

- Question:
- As of / state:
- Expected answer:

## 6. checklist
The customer wants a complete list, and the items come from several articles. Missing one item is a wrong answer.
*Example only, not used:* "Everything I need to bring if I'm selling a leased car that I co-own with my sister?"

- Question:
- As of / state:
- Expected answer:

## 7. unanswerable
The KB does not answer it (see "Not covered" in the outline, or invent another gap). The right behavior is to say so, not to guess from a look-alike article.
*Example only, not used:* "Will you buy my boat?"

- Question:
- As of / state:
- Expected answer: (not in the KB)
