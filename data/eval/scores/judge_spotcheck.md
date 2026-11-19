# Judge spot-check (5 random judgements from run 1)

For each: does the judge's verdict match what the answer says? Mark agree / disagree.

Claude's own read (not a human check): agrees with all 5. In q44 and q47 the answer says part of the question isn't covered because retrieval missed an article; the judge marks `declines uncovered parts: False`, as its instructions say for a fully covered question. **Tianyi agreed with all 5 on 2026-11-18.**

## q29 · M2 · temporal
**Question:** Is Granite Bank in your e-payoff network? My appointment is next week.

**Answer:** Not yet. Granite Bank joins our e-payoff network on March 15, 2026, so for an appointment next week it won't be in the network. You'll need to bring a payoff letter from Granite Bank showing your account number, the payoff amount, the date it's good through, and where to send payment, and you should ask for a 15-day payoff amount. If you'd rather not contact them yourself, sign form NW-LPA-1 and we'll request the letter for you, but allow 2 business days.

**Judge:**
- ✅ not yet
- ✅ March 15
- declines uncovered parts: True

Your call: agree / disagree

## q02 · M2 · exact
**Question:** Which form do I sign so you can get the payoff number, NW-LPA-1 or NW-LSE-1? It's a lease.

**Answer:** Since it's a lease, sign the lease buyout authorization, form NW-LSE-1, and we'll request the dealer payoff quote from your leasing company for you. NW-LPA-1 is only for loans. Before that, check that your leasing company allows third-party buyouts. Then bring the dealer payoff quote to your appointment.

**Judge:**
- ✅ NW-LSE-1
- declines uncovered parts: True

Your call: agree / disagree

## q34 · M6 · conditional
**Question:** I moved from California to North Carolina last year, but the car is still registered in California. What do I do with the plates when I sell?

**Answer:** Plates follow the state that issued them, not the state you live in, so your California plates need to come off the car. Return them to the California motor vehicle agency within 10 days, and we'll give you form NW-PLT-1, the plate return receipt that shows the car was sold. Also note that to sell a California-registered car at a North Carolina store, you'll need to bring the California registration and get an emissions certificate from a North Carolina inspection station first.

**Judge:**
- ✅ return
- ✅ 10 days
- ✅ NW-PLT-1
- declines uncovered parts: True

Your call: agree / disagree

## q44 · M4 · checklist
**Question:** My car is paid off but I lost the title, and I'm in California. Walk me through everything I need to do to sell it.

**Answer:** Because your car is paid off, you'll need to get a duplicate title from California before we can complete the purchase, since we can't buy a fully paid-off car without a title. While you wait for the duplicate, you can still get an offer and book an appointment. The help center doesn't say how long a California duplicate takes or how to request one, and it doesn't list the other steps or documents for the sale. Please contact a store for those details.

**Judge:**
- ✅ duplicate title
- ❌ NW-ODO-2
- ❌ return the plates
- declines uncovered parts: False

Your call: agree / disagree

## q47 · M3 · checklist
**Question:** I owe more on my car than your offer, and my loan is with Coastal Credit Union. What do I bring to finish the sale?

**Answer:** You can still sell us the car, but you'll pay the difference between your loan payoff and our offer at the appointment, by cashier's check or debit card (we don't accept personal checks or credit cards). Bring a payoff letter from your lender, since we compare it with the offer and pay the lender off directly; you don't need the title, because your lender holds it while the loan is open. The articles I have mention an appointment checklist but don't list what's on it, and they say nothing specific about Coastal Credit Union, so please contact a store for the full list.

**Judge:**
- ✅ payoff letter
- ✅ cashier's check or debit
- declines uncovered parts: False

Your call: agree / disagree
