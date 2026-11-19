# Gold v2 for review (D-031)

Frozen 2026-11-18 (`data/eval/FROZEN_v2`) before any method ran on it. Tianyi approved without a separate review; this page is for reading later.
Chain: the answer needs an article reached through a link, a form, a form's replacement or a company named in the question. Structural: a list; the expected items are recomputed from the records by `make check`.

## v2c01 · chain · bridge: lender name + link
**Q:** My loan is through Northwind Auto Finance. After I sell you the car, how soon is the loan paid off, and can I skip my next payment?

**Gold articles:** getting_paid__2026, epayoff_network__2026, keep_paying_until_confirmed__2022
**Facts:**
- the payoff goes to the lender the same day, because Northwind Auto Finance is in the e-payoff network
- keep making payments until the lender confirms the loan is paid off

**Perfect answer:** Northwind Auto Finance is in our e-payoff network, so we send your payoff the same day. Don't skip the next payment: keep paying until the lender confirms the loan is closed. If an extra payment goes through, the lender refunds it to you.

*Why it's hard:* The lender's name is the only link to the e-payoff network article; payment timing is in getting_paid, and the 'keep paying' rule in a third article linked from it. 'Northwind' alone appears in 16 articles, so only the full name identifies the lender.

## v2c02 · chain · bridge: link · state texas
**Q:** I paid off my car, but the title still shows the bank as lienholder. I'm in Texas. Do I need a paper lien release before I can sell it to you?

**Gold articles:** lien_still_on_title__2022, electronic_titles__2022
**Facts:**
- Texas uses electronic titles, so the lender sends the lien release to the state electronically
- ask the lender for a lien release, or sign NW-LRL-1 so Northwind contacts the lender (this can add 1 to 2 weeks)
- you can still get an offer and book an appointment while you wait

**Perfect answer:** The lien still has to be released, but Texas uses electronic titles, so your lender sends the release to the state electronically; there's no paper release to bring. Ask the lender to release it, or sign NW-LRL-1 and we contact them (this can add 1 to 2 weeks). You can get an offer and book your appointment meanwhile.

*Why it's hard:* lien_still_on_title only says 'in states with electronic titles'; which states those are is in the linked article.

## v2c03 · chain · bridge: link · state north_carolina
**Q:** I moved to North Carolina, but my car is still registered in Virginia and the registration ran out in September. Can I sell it at a North Carolina store?

**Gold articles:** registration_expired__2022, out_of_state__2026
**Facts:**
- renew the registration before the appointment, because in North Carolina it must be current on the day of the sale
- get an emissions certificate from a North Carolina inspection station

**Perfect answer:** Yes, after two steps. In North Carolina the registration must be current on the day of the sale, so renew it before your appointment. And a car registered in another state needs an emissions certificate from a North Carolina inspection station before a North Carolina store can buy it. Bring the Virginia registration.

*Why it's hard:* The expired-registration article answers half and links to the out-of-state article, which holds the emissions rule; the question never mentions emissions.

## v2c04 · chain · bridge: link
**Q:** My ex is still on the title, and I changed my last name back after the divorce, so my ID doesn't match the title either. What do I need to sell the car?

**Gold articles:** divorce_ex_on_title__2022, title_name_mismatch__2022
**Facts:**
- your ex has to sign too, unless the divorce decree awards the car to you (then bring a certified copy of the decree)
- bring the document that shows the name change, such as the divorce decree
- sign the name change affidavit, form NW-NMC-1

**Perfect answer:** Your ex has to sign as a co-owner, unless your divorce decree awards the car to you; then bring a certified copy and their signature isn't needed. For the name, bring the document that shows the change (the divorce decree) and sign the name change affidavit, NW-NMC-1, at the appointment.

*Why it's hard:* Two situations in one question; the divorce article links to the name-mismatch article, which has the form.

## v2c05 · chain · bridge: lender name
**Q:** My car doesn't run anymore and the loan is with Meridian Auto Loans. How do I get the car to you, and do I need a payoff letter?

**Gold articles:** non_running_cars__2026, epayoff_network__2026
**Facts:**
- cars that don't run can't use home pickup
- select stores tow it to the store at no charge
- no payoff letter is needed, because Meridian Auto Loans is in the e-payoff network

**Perfect answer:** Home pickup isn't available for cars that don't run, but select stores tow your car to the store at no charge; your offer page shows which ones. Meridian Auto Loans is in our e-payoff network, so you don't need a payoff letter: we confirm the payoff with them at the appointment.

*Why it's hard:* Two topics; the payoff part depends only on the lender's name, which links to the e-payoff network article.

## v2c06 · chain · bridge: form replaced_by
**Q:** I found an NW-ODO-1 odometer statement in my old paperwork. Can I fill that out for my appointment next week?

**Gold articles:** appointment_checklist__2026 · **traps:** odometer_problems__2022
**Facts:**
- no: NW-ODO-1 was replaced on February 1, 2026
- use the odometer disclosure statement, form NW-ODO-2

**Perfect answer:** No. NW-ODO-1 was replaced by the odometer disclosure statement, NW-ODO-2, on February 1, 2026. Bring NW-ODO-2 with the rest of the appointment checklist.

*Why it's hard:* odometer_problems__2022 is current and still tells readers to use NW-ODO-1 (known issue KI-2). The replacement is in the form record (replaced_by) and in the checklist.

## v2c07 · chain · bridge: form replaced_by · state virginia
**Q:** My dad wants me to sell his car for him. Does he have to sign the power of attorney in front of a notary? We live in Virginia.

**Gold articles:** co_owners__2026 · **traps:** selling_for_someone_else__2022
**Facts:**
- no notary is needed in Virginia (only Georgia requires one)
- he can sign power of attorney form NW-POA-2 electronically

**Perfect answer:** No. Since February 1, 2026 the power of attorney is form NW-POA-2, which he can sign electronically with no notary; only Georgia still requires a notary. The old notarized NW-POA-1 is retired.

*Why it's hard:* selling_for_someone_else__2022 matches the question best and is current, but still says to sign NW-POA-1 in front of a notary (known issue KI-1). The current rule is reached through NW-POA-1 → replaced_by → NW-POA-2.

## v2c08 · chain · bridge: link + state filter · state georgia
**Q:** I moved from Texas to Georgia. My paid-off car is still registered in Texas, and I can't find the title. Whose rules apply for a duplicate, and how long will it take?

**Gold articles:** out_of_state__2026, duplicate_title_texas__2022
**Facts:**
- the duplicate rules of the state that issued the title (Texas) apply
- Texas titles are electronic, so for the sale you usually don't need a printed duplicate
- a printed Texas duplicate takes 5 to 7 business days online

**Perfect answer:** Texas rules apply, because the duplicate rules of the state that issued the title apply. Texas uses electronic titles, so for a sale to us you usually don't need a printout: we transfer the electronic title at the appointment. If you want a printed duplicate, request it online; it takes 5 to 7 business days.

*Why it's hard:* The state filter uses the customer's state (Georgia), so it removes the Texas article that answers the question; the graph can walk to it (out_of_state → lost_title → duplicate_title_texas), but neighbours pass the same filter.

## v2c09 · chain · bridge: link · as_of 2026-10-30
**Q:** I got my offer on October 29 and booked my appointment for October 31. Can I move it to November 4 and keep the same offer?

**Gold articles:** reschedule_cancel__2022, offer_validity__2026
**Facts:**
- no: rescheduling keeps the offer only if the new time is on or before the offer's expiration date
- offers are valid for 5 days (or 250 miles), so this one expires before November 4
- you can request a new offer, which may be higher or lower

**Perfect answer:** Not with the same offer. Offers are valid for 5 days or 250 miles, so an offer from October 29 expires before November 4, and rescheduling keeps the offer only if the new time is on or before the expiration date. Keep October 31, or request a new offer for November 4; the new amount may be higher or lower.

*Why it's hard:* The rescheduling rule and the validity period are in two articles that link to each other; the answer needs both and a date calculation.

## v2c10 · chain · bridge: link
**Q:** Someone texted me saying they're from Northwind and that I have to wire the money I owe before my appointment, because my loan is higher than your offer. Is that legit?

**Gold articles:** offer_scams__2026, negative_equity__2026
**Facts:**
- no: Northwind never asks for wire transfers
- the difference (negative equity) is paid only in person at the appointment
- by cashier's check or debit card

**Perfect answer:** No, that's a scam: Northwind never asks for wire transfers, gift cards or crypto. If you owe more than the offer, you pay the difference only in person at the appointment, by cashier's check or debit card. Don't respond, and report the message through the Help Center.

*Why it's hard:* The scam article links to the negative-equity article, which says how the real payment works.

## v2c11 · chain · bridge: lender name
**Q:** I owe Lakeshore Bank about $1,000 more than your offer. How do I pay the difference, and do I need a payoff letter from them?

**Gold articles:** negative_equity__2026, epayoff_network__2026
**Facts:**
- pay the difference at the appointment by cashier's check or debit card (no personal checks or credit cards)
- no payoff letter is needed, because Lakeshore Bank is in the e-payoff network

**Perfect answer:** You pay the difference at the appointment with a cashier's check or a debit card; we don't accept personal checks or credit cards. Lakeshore Bank is in our e-payoff network, so you don't need a payoff letter: we confirm the payoff with them at the appointment.

*Why it's hard:* negative_equity says 'after we compare the offer with your payoff letter'; whether this lender needs one depends on its name, which only the e-payoff network article lists.

## v2c12 · chain · bridge: lessor name + shared form
**Q:** My lease is with Summit Auto Lease and I'd rather not call them again. Can you get the payoff number for me?

**Gold articles:** leased_car__2022, lessor_buyouts__2026
**Facts:**
- sign the lease buyout authorization, form NW-LSE-1, and Northwind requests the dealer payoff quote
- Summit Auto Lease allows third-party buyouts

**Perfect answer:** Yes. Sign the lease buyout authorization, NW-LSE-1, and we request the dealer payoff quote from Summit for you. Summit Auto Lease allows third-party buyouts, so we can buy the car from them.

*Why it's hard:* The payoff-letter article (the closest text match) offers NW-LPA-1, which is for loans only; the lease form is in the leased-car article, and whether Summit allows a buyout is in the leasing-company article.

## v2s01 · structural · bridge: records
**Q:** Which forms did Northwind retire in 2026, and what replaced each one?

**Gold articles:** co_owners__2026, appointment_checklist__2026
**Expected forms:** NW-POA-1, NW-ODO-1
**Facts:**
- NW-POA-1 was replaced by NW-POA-2
- NW-ODO-1 was replaced by NW-ODO-2

**Perfect answer:** Two: the notarized power of attorney NW-POA-1, replaced by the e-sign NW-POA-2, and the odometer statement NW-ODO-1, replaced by the odometer disclosure statement NW-ODO-2, both on February 1, 2026.

*Why it's hard:* The facts are in two unrelated articles; the form records hold them in one place (status, replaced_by).

## v2s02 · structural · bridge: records
**Q:** List every form that is new since the February 1, 2026 rewrite.

**Gold articles:** co_owners__2026, appointment_checklist__2026, what_changes_offer__2026, payoff_letter__2026, inherited_car__2026, military_deployed__2026, license_plates__2026
**Expected forms:** NW-POA-2, NW-ODO-2, NW-DMG-1, NW-LPA-1, NW-EST-1, NW-MIL-1, NW-PLT-1
**Facts:**
- NW-POA-2
- NW-ODO-2
- NW-DMG-1
- NW-LPA-1
- NW-EST-1
- NW-MIL-1
- NW-PLT-1

**Perfect answer:** Seven: NW-POA-2, NW-ODO-2, NW-DMG-1, NW-LPA-1, NW-EST-1, NW-MIL-1 and NW-PLT-1.

*Why it's hard:* Seven forms in seven articles, more than any top 5; most articles don't say a form is new.

## v2s03 · structural · bridge: records + edges
**Q:** Which help-center articles in effect today still tell customers to use a retired form?

**Gold articles:** selling_for_someone_else__2022, odometer_problems__2022
**Expected articles:** selling_for_someone_else, odometer_problems
**Facts:**
- Selling a family member's car for them (still says NW-POA-1)
- Broken or replaced odometer (still says NW-ODO-1)

**Perfect answer:** Two: 'Selling a family member's car for them' still tells readers to sign NW-POA-1, and 'Broken or replaced odometer' still names NW-ODO-1. Both forms were replaced on February 1, 2026.

*Why it's hard:* Needs every current article's form codes compared with the forms' status; an article that names the old form next to its replacement (the checklist, co-owners) doesn't count.

## v2s04 · structural · bridge: records
**Q:** Which lenders in our records are not in the e-payoff network, so their customers still need a payoff letter?

**Gold articles:** epayoff_network__2026
**Expected lenders:** redstone_credit, coastal_cu, oakline_finance, valley_motor_credit, harbor_trust_bank, summit_peak_bank
**Facts:**
- Redstone Credit
- Coastal Credit Union
- Oakline Finance
- Valley Motor Credit
- Harbor Trust Bank
- Summit Peak Bank

**Perfect answer:** Six: Redstone Credit, Coastal Credit Union, Oakline Finance, Valley Motor Credit, Harbor Trust Bank and Summit Peak Bank.

*Why it's hard:* The help center lists only the lenders that are in the network; the others exist only in the lender records.

## v2s05 · structural · bridge: control (one article)
**Q:** Which leasing companies pass the lease equity to the customer?

**Gold articles:** lease_equity__2022
**Expected lessors:** summit_auto_lease, crescent_motor_credit, apex_lease
**Facts:**
- Summit Auto Lease
- Crescent Motor Credit
- Apex Lease Co

**Perfect answer:** Summit Auto Lease, Crescent Motor Credit and Apex Lease Co. Bluewater Leasing applies it to a Northwind purchase instead, and Harbor Leasing and Ironwood Lease don't allow third-party buyouts.

*Why it's hard:* Control: one article lists the answer.

## v2s06 · structural · bridge: control (codes)
**Q:** Which help-center articles would need an update if form NW-LSE-1 were retired?

**Gold articles:** payoff_letter__2026, leased_car__2022
**Expected articles:** payoff_letter, leased_car
**Facts:**
- Getting a payoff letter from your lender
- Selling a car that you lease

**Perfect answer:** Two current articles name NW-LSE-1: 'Getting a payoff letter from your lender' and 'Selling a car that you lease'.

*Why it's hard:* Control for the graph: BM25 matches form codes exactly, so keyword search may already find both.

## v2s07 · structural · bridge: control (one article)
**Q:** Which leasing companies changed their third-party buyout rules on February 1, 2026?

**Gold articles:** lessor_buyouts__2026
**Expected lessors:** crescent_motor_credit, apex_lease
**Facts:**
- Crescent Motor Credit (buyouts allowed since then)
- Apex Lease Co (a $350 buyout fee since then)

**Perfect answer:** Two: Crescent Motor Credit started allowing third-party buyouts, and Apex Lease Co added a $350 third-party buyout fee.

*Why it's hard:* Control: one article states both changes.

## v2s08 · structural · bridge: control (one article)
**Q:** Which of the states we serve use paper titles?

**Gold articles:** electronic_titles__2022
**Expected states:** north_carolina, georgia, california
**Facts:**
- North Carolina
- Georgia
- California

**Perfect answer:** North Carolina, Georgia and California; Virginia and Texas use electronic titles.

*Why it's hard:* Control: one article lists both groups.
