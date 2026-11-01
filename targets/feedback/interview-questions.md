# Interview questions

Every question asked while writing the Feedback website specification, in the order
they were asked, with the alternatives offered. There are 52 questions in 16 rounds,
all from 2026-11-01.

- **Chosen** marks the answer given. A question that allowed several answers says so.
- **(Recommended)** marks what was recommended at the time.
- An answer in your own words was always possible, though none was given.

The specification itself is in [specs/](specs/). Open `specs/index.cmd` to read it.

## Round 1: The goal and the shape of the website

### 1. Goal

For the Feedback website: what should be better for your business once it exists?
Pick all that apply.

| Alternative | What it means | Chosen |
|---|---|---|
| Know what to improve | Learn what users want changed or fixed in what you offer. | Yes |
| Catch unhappy users | Hear about problems in time to put them right before people leave. | Yes |
| Track satisfaction | See over time whether users are getting happier or less happy. | Yes |
| Collect testimonials | Gather praise you can show to others. This needs users' permission to publish it. | Yes |

### 2. Measure

Which number would show the Feedback website worked? Pick one, and use Other if you
can give today's figure and a target, e.g. "20 a month today, 100 a month within 3
months".

| Alternative | What it means | Chosen |
|---|---|---|
| Feedback per month | How many pieces of feedback arrive each month. | Yes |
| Share who respond | What percentage of your users send feedback. | |
| Average rating | The average score users give. This means the site must ask for a rating. | |
| Changes made from it | How many improvements you make because of feedback. | |

### 3. Who sends

Who can send feedback on the website?

| Alternative | What it means | Chosen |
|---|---|---|
| Anyone, no account (Recommended) | Open a page and send, with an optional email for a reply. Simplest for users, but more exposed to spam, and you can't confirm who sent it. | Yes |
| Personal link only | You send each user a unique link. Feedback is tied to a real user with no login, but you must hold a user list and send the links. | |
| Signed-in users only | Users create or use an account. You know exactly who said what, but it is more to build and fewer people will bother. | |

### 4. Python

You said "Python frontend". Which of these do you mean?

| Alternative | What it means | Chosen |
|---|---|---|
| Python on the server (Recommended) | Users see an ordinary website in their browser, and Python runs behind it and talks to the database. | Yes |
| Python tool for staff | A separate Python program your team uses to read feedback, alongside the public website. | |
| Developer can choose | Python was only a suggestion, so whoever builds it picks the technology. | |

## Round 2: Rating, staff and spam

### 5. Rating

What scale should the Feedback website's rating use?

| Alternative | What it means | Chosen |
|---|---|---|
| 1 to 5 stars (Recommended) | Familiar and quick, and it gives a clear monthly average. | Yes |
| Thumbs up or down | The quickest to give, but it shows only a share of happy users, with no shades in between. | |
| 0 to 10 score | A common business measure with finer detail, but it takes more thought from the user. | |

### 6. Low rating

When a user gives a low rating (say 1 or 2 out of 5), how should your staff find out?

| Alternative | What it means | Chosen |
|---|---|---|
| Email staff at once (Recommended) | Catches problems in time, but the website has to send email and staff get a message each time. | Yes |
| Daily summary email | Fewer interruptions, but a problem can wait up to a day. | |
| Mark in the list only | Nothing extra to build, but it works only if staff open the list regularly. | |

### 7. Staff login

How should your staff sign in to read feedback?

| Alternative | What it means | Chosen |
|---|---|---|
| Own sign-in, developer adds (Recommended) | Each person has their own, so a leaver can be removed. Needs no admin screen, but changes go through a developer. | Yes |
| Own sign-in, owner adds | You manage staff yourself, but it adds an admin screen to build. | |
| One shared sign-in | The simplest to build, but the password must change whenever someone leaves, and you can't see who did what. | |

### 8. Spam

What should happen to spam and abusive feedback, given that anyone can send it?

| Alternative | What it means | Chosen |
|---|---|---|
| Staff remove it (Recommended) | Staff can remove a piece of feedback, and it stops counting towards feedback per month. Some manual work. | Yes |
| Automatic spam blocking | Most spam never arrives, but it is more to build and can occasionally block a real user. | |
| Both | Blocks most of it automatically and lets staff remove the rest. The most to build. | |
| Do nothing for now | Nothing to build, but spam stays in the list and inflates your number. | |

## Round 3: How deep to go

### 9. Depth

How deep should I question you about the Feedback website? You can stop after any
round.

| Alternative | What it means | Chosen |
|---|---|---|
| Standard (Recommended) | About 25 questions: the basics, a walk through sending and reading feedback, and one question each on areas such as privacy and devices. Some qualities stay open, so it can't be agreed yet. | Yes |
| Short | About 12 questions: the problem, success, limits, what's out and what could go wrong. Quickest, but the qualities stay open and the walkthrough cases stay as my additions. | |
| Full | 40 or more questions: everything in standard, each area in detail, what an engineer would ask, and all nine qualities. The only depth that can take it all the way to agreed. | |

## Round 4: How things work today

### 10. Your users

Who are the users you want feedback from, and what does your business do? Pick the
closest, and use Other to say what the business does if you can.

| Alternative | What it means | Chosen |
|---|---|---|
| Customers buying products | People who buy goods from you, online or in a shop. | Yes |
| Clients of a service | People or companies you provide a service to. | |
| Users of software or an app | People using a digital product you run. | |
| Members or the public | A membership, community, venue or public organisation. | |

### 11. Today

How does your business get feedback from those users today? Pick all that apply. If
none apply, use Other and say so.

| Alternative | What it means | Chosen |
|---|---|---|
| Email or phone | Users write or call when they have something to say. | Yes |
| In person | Staff hear it face to face. | Yes |
| Surveys or forms | You send surveys, or use a form tool. | Yes |
| Public reviews or social media | Google, Trustpilot, Facebook and similar. | Yes |

### 12. What fails

What goes wrong with how you get feedback today? Pick all that apply. If nothing
does, use Other and say so.

| Alternative | What it means | Chosen |
|---|---|---|
| Too little arrives | Most users never say anything. | Yes |
| It's scattered | It sits in different places, so nobody sees it all. | Yes |
| It arrives too late | You hear about a problem after the user has gone. | Yes |
| Nobody can see the trend | You can't tell whether things are getting better or worse. | Yes |

### 13. How known

How do you know that's the problem?

| Alternative | What it means | Chosen |
|---|---|---|
| Our own experience | It's what you've seen, with nothing counted. | Yes |
| Staff or users told us | People have said so, and you could name who. | |
| We counted something | You have figures, such as complaints or lost customers. Use Other to give them. | |

## Round 5: The shape of the product

### 14. Shape

You already use forms and still get too little feedback, too late. What shape should
the Feedback product take?

| Alternative | What it means | Chosen |
|---|---|---|
| Website + ask after purchase (Recommended) | The website you described, plus each customer gets a link to it after buying. More feedback and sooner, but it needs a way to contact customers, usually a link to your order system. | Yes |
| Website only | As you described: customers find the page themselves, or you share the link by hand. Least to build, but it may not fix "too little" or "too late". | |
| Try an existing form tool first | Run a ready-made form for a month or two and see who answers, building nothing yet. Cheapest test of demand, but no site of your own and little of the staff side. | |

## Round 6: Asking after a purchase

### 15. Where sold

Where do your customers buy from you? Pick all that apply. This decides where the
Feedback website learns about orders.

| Alternative | What it means | Chosen |
|---|---|---|
| Online shop platform | Shopify, WooCommerce or similar. Use Other to name it. | Yes |
| Our own online shop | A shop built for you, with its own order system. | Yes |
| Physical shop | Customers buy in person, at a till. | Yes |
| Marketplaces | Amazon, eBay, Etsy and similar. These often limit how you can contact buyers. | Yes |

### 16. Reach them

How can you reach a customer after they buy? Pick all that apply. If you can't, use
Other and say so.

| Alternative | What it means | Chosen |
|---|---|---|
| Email | You hold their email address from the order. | Yes |
| Text message | You hold their mobile number. Texts usually cost per message. | Yes |
| Printed link or QR code | On the receipt or in the parcel. Needs no contact details, but it can't be timed or tracked to a customer. | Yes |

### 17. When

When should the request for feedback go out? Your typical delivery time decides this,
because customers should have the product first.

| Alternative | What it means | Chosen |
|---|---|---|
| When the order is delivered | The best timing, but your system must know the delivery date. | Yes |
| 3 days after the order | Needs no delivery information. Suits fast delivery. | |
| 7 days after the order | Needs no delivery information. Safer for slower delivery, but the moment has passed for some customers. | |

### 18. How often

A customer orders from you every week. How often should they be asked for feedback?

| Alternative | What it means | Chosen |
|---|---|---|
| At most once a month (Recommended) | Frequent buyers aren't pestered, but you hear about fewer of their orders. | Yes |
| After every order | The most feedback, but frequent buyers may start ignoring or blocking you. | |
| At most once every 3 months | The gentlest, but a problem with a later order may go unheard. | |

## Round 7: Limits and the first release

### 19. First

Four sales channels is a lot for a first release of the Feedback website. Where
should it start asking customers? The printed QR code works in every case, so pick
the channel with the most orders.

| Alternative | What it means | Chosen |
|---|---|---|
| Online shop platform + QR (Recommended) | Connects one channel, usually with ready-made connections, and the QR code covers the physical shop. Others follow later. | Yes |
| Our own online shop + QR | Connects your own order system first. It may need work on that system too. | |
| QR code only | No connections at all, so it's the smallest and quickest, but there are no timed requests yet. | |
| All channels at once | Everything in one go. The longest and costliest first release, and the most to go wrong. | |

### 20. Time limit

How much time can the first release of the Feedback website take?

| Alternative | What it means | Chosen |
|---|---|---|
| Up to 1 month | Only the smallest version is realistic. | Yes, later changed by question 23 |
| 1 to 3 months | Room for one connection and the staff side. | |
| 3 to 6 months | Room for several connections. | |
| No fixed limit | Without a limit, the scope can grow one cheap feature at a time. | |

### 21. Target

How many pieces of feedback a month would count as success, 3 months after launch?
Use Other for an exact number or a different date.

| Alternative | What it means | Chosen |
|---|---|---|
| Under 50 a month | A small business, or few orders a month. | |
| 50 to 200 a month | Moderate order volume. | Yes, later changed by question 49 |
| 200 to 1,000 a month | High order volume. | |
| I don't know yet | It stays an assumption until you've compared it with your monthly orders. | |

### 22. Protect

While feedback goes up, what must not get worse? Pick all that apply. If nothing, use
Other and say so.

| Alternative | What it means | Chosen |
|---|---|---|
| Customers feeling pestered | Complaints or opt-outs from the requests must stay low. | Yes |
| Staff time | Reading feedback mustn't take over the team's day. | Yes |
| Public review scores | Your ratings on Google and marketplaces must not fall. | Yes |

## Round 8: A conflict between two answers

### 23. Conflict

You chose a first release of the Feedback website with the shop platform plus QR code,
and also a limit of up to 1 month. Those likely don't fit together. Which gives way?
(The timings are a rough guess for a developer to confirm.)

| Alternative | What it means | Chosen |
|---|---|---|
| Allow 1 to 3 months (Recommended) | Keeps the shop platform and QR code, so asking after purchase is in from the start. The release takes longer. | Yes |
| Keep 1 month, QR only | The website and printed QR code go first, and requests after purchase follow in release 2. On time, but it doesn't yet fix "too little" or "too late". | |
| Keep 1 month, cut the staff extras | Keeps requests after purchase, and moves ratings by month, the printing page, and removing feedback to release 2. Tight, and spam can't be removed at first. | |
| Ask a developer first | Keep both choices as they are, and record this as an open question for whoever builds it. | |

## Round 9: The shop platform

### 24. Platform

Which online shop platform does your business use? It's the first one the Feedback
website connects to. Use Other for any not listed.

| Alternative | What it means | Chosen |
|---|---|---|
| Shopify | A hosted shop platform. | |
| WooCommerce | A shop added to a WordPress site. | |
| BigCommerce | A hosted shop platform. | |
| I don't know | Stays an open question for whoever runs your shop. | Yes |

### 25. Delivery

Does your shop platform know when an order has been delivered?

| Alternative | What it means | Chosen |
|---|---|---|
| Yes | Your couriers report delivery back to the shop, so requests can go out on delivery. | |
| No | It knows when an order shipped at most, so the Feedback website needs a fallback. | |
| I don't know | Stays an open question, and whoever sets up the connection can check. | Yes |

### 26. Fallback

If an order's delivery date can't be known, when should the Feedback website send the
request instead?

| Alternative | What it means | Chosen |
|---|---|---|
| 7 days after the order (Recommended) | Safer for slower delivery, though some customers will have had the product for a while. | Yes |
| 3 days after the order | Sooner, but some customers may be asked before the product arrives. | |
| Don't send a request | Nobody is asked too early, but those customers can only use the printed link. | |

## Round 10: What's out, and what could go wrong

### 27. Testimonials

Where should testimonials appear? (Staff already see which feedback has permission.)

| Alternative | What it means | Chosen |
|---|---|---|
| No public page yet (Recommended) | Staff see which feedback may be published and copy it where they like. Simplest, and fits 3 months, but nothing appears by itself. | Yes |
| Public page, staff approve | A page of quotes staff pick. Needs an approval step and a name field, so it's more to build. | |
| On the shop's own pages | Quotes appear in your shop. The most to build, and it depends on your platform. | |

### 28. Left out

What might people expect from the Feedback website that you do NOT want built now?
Pick all that should stay out. If none, use Other and say so.

| Alternative | What it means | Chosen |
|---|---|---|
| Replying from the website | Staff reply from their own email or phone. | Yes |
| Importing old feedback | Past emails, reviews and survey results stay where they are. | Yes |
| Mobile app | Web only, with no app to install. | Yes |
| Public view of feedback | Customers can't see each other's feedback. | Yes |

### 29. Risks

What could make the Feedback website fail? Pick all that worry you. Use Other to add
one, and to say what you'd do about it.

| Alternative | What it means | Chosen |
|---|---|---|
| Customers ignore requests | Requests go out but few people answer. | Yes |
| Nobody acts on feedback | It arrives, but staff are too busy to read or respond. | Yes |
| Shop connection is hard | The platform can't provide orders or delivery dates as hoped. | Yes |
| Messages land in spam | Request emails never reach customers. | Yes |

### 30. Veto

Who could stop this project if they said no? Pick all that apply. If nobody, use
Other and say so.

| Alternative | What it means | Chosen |
|---|---|---|
| Owner or management | Whoever approves the money and time. | Yes |
| Legal or data protection | Whoever checks how you use customers' contact details. | Yes |
| Whoever runs the shop | They control access to the platform and its orders. | Yes |

## Round 11: What you'd do about each risk

### 31. Ignored

If customers ignore the Feedback website's requests, what will you do?

| Alternative | What it means | Chosen |
|---|---|---|
| Review after a month (Recommended) | Check the response rate after the first month, then change the wording or timing. Costs a little staff time. | Yes |
| Offer a small reward | For example a discount for giving feedback. Lifts responses, but costs money and can skew what people say. | |
| Accept it | Do nothing and see how it goes. | |

### 32. No action

If feedback arrives but nobody acts on the Feedback website's list, what will you do?

| Alternative | What it means | Chosen |
|---|---|---|
| Name one person responsible (Recommended) | One named person reads it on a set day each week. Needs someone to own it. | Yes |
| Rely on low-rating emails | Staff act only when emailed about an unhappy customer. The rest may go unread. | |
| Accept it | Do nothing and see how it goes. | |

### 33. Connection

If the shop platform can't provide orders or delivery dates as hoped, what will you
do?

| Alternative | What it means | Chosen |
|---|---|---|
| Check before building (Recommended) | Ask whoever runs the shop first (Q10). If it can't be done, launch with the QR code and add requests later. | Yes |
| Fall back to 7 days only | Use order data with no delivery dates, as already agreed. This doesn't help if orders themselves are unavailable. | |
| Accept the delay | Hold the release until the connection works. | |

### 34. Spam folder

If request emails land in spam folders, what will you do?

| Alternative | What it means | Chosen |
|---|---|---|
| Set up sending properly (Recommended) | A developer sets up email sending for your domain and tests it before launch. A little more setup. | Yes |
| Rely on the printed QR code | Some customers still reach the page, but not those who bought online. | |
| Accept it | Do nothing and see how it goes. | |

## Round 12: Privacy, devices, languages and additions

### 35. Keep for

How long should the Feedback website keep feedback and the email addresses left with
it, before they're deleted? This may change once your legal adviser has answered.

| Alternative | What it means | Chosen |
|---|---|---|
| 12 months (Recommended) | Enough to compare a full year. Holds less personal data, but older trends are lost. | Yes |
| 24 months | Longer trends, but more personal data held. | |
| Until staff remove it | Nothing to delete automatically, but personal data can pile up with no end date. | |

### 36. Devices

On which devices must the Feedback website work?

| Alternative | What it means | Chosen |
|---|---|---|
| Phones and computers (Recommended) | In any current browser. Customers open requests on phones, and staff read on either. | Yes |
| Computers only | Less to test, but it's a poor fit for a link opened on a phone. | |

### 37. Languages

Which languages must the Feedback website offer customers? Use Other to name yours.

| Alternative | What it means | Chosen |
|---|---|---|
| One language: English (Recommended) | The simplest. Use Other if your one language isn't English. | Yes |
| Two languages | Use Other to name them. All wording and emails must be written twice. | |
| Three or more | Use Other to name them. The most to write and maintain. | |

### 38. Additions

What should happen to the 16 additions listed above for the Feedback website, covering
edge cases such as failed sends, email before text and the opt-out?

| Alternative | What it means | Chosen |
|---|---|---|
| Confirm all of them (Recommended) | They become part of the spec. You can still change any later. | Yes |
| I'll review them first | They stay marked as additions under What is open, so you can read each one in the app. | |

## Round 13: Settling what was open

### 39. Time zone

Which time zone decides when a day and a month end, for the Feedback website's monthly
figures and request dates (Q15)?

| Alternative | What it means | Chosen |
|---|---|---|
| The business's local time (Recommended) | Figures match the calendar your staff use. Use Other to name the time zone if you'd like it written down. | Yes |
| UTC | One fixed standard, but late-evening feedback can land in the next day or month. | |

### 40. Opt-outs

Should a customer's opt-out be kept after the 12-month deletion, for as long as you
can still contact them (AD20, touches R19)?

| Alternative | What it means | Chosen |
|---|---|---|
| Yes, keep opt-outs (Recommended) | An opted-out customer is never asked again. You hold a small record about them for longer. | Yes |
| No, delete at 12 months | Holds less, but that customer starts getting requests again. | |

### 41. Marketplaces

Do your marketplaces allow you to contact buyers for feedback outside the marketplace
(Q11, touches R13)? They aren't in the first release.

| Alternative | What it means | Chosen |
|---|---|---|
| Settle it later (Recommended) | Recorded as a decision to check before marketplaces are added, so it no longer holds up this spec. | Yes |
| Yes, they allow it | Recorded as allowed, so requests can go to marketplace buyers in a later release. | |
| No, they don't | Marketplace buyers won't get requests, and the printed link stays their only route. | |

### 42. Approval

Have the owner or management approved the time and money for the Feedback website
(Q13)?

| Alternative | What it means | Chosen |
|---|---|---|
| Yes, approved | This includes you approving it yourself, if you're the owner. | Yes |
| Not yet | Stays open, and it keeps the spec from being agreed. | |

## Round 14: Guard-rail limits

### 43. Opt-outs

Guard rail for pestering (G5): what share of feedback requests ending in an opt-out or
complaint would make you change the requests?

| Alternative | What it means | Chosen |
|---|---|---|
| More than 1% | Strict: you'd act on 2 in every 100 requests. | Yes |
| More than 2% | In between. | |
| More than 5% | Relaxed: you'd let more through before acting. | |
| Set after first month | Measure a month of real requests first, then set the limit from that. | |

### 44. Staff time

Guard rail for staff time (G6): how much staff time a week on reading feedback is too
much?

| Alternative | What it means | Chosen |
|---|---|---|
| More than 1 hour a week | Tight, and it may be hit at 200 pieces a month. | Yes |
| More than 3 hours a week | In between. | |
| More than 5 hours a week | Relaxed, close to a day of someone's week. | |
| Set after first month | Measure a month of real time first, then set the limit from that. | |

### 45. Reviews

Guard rail for public reviews (G7): how far may your public review score fall before
you act? Scores can also fall for reasons unrelated to this website.

| Alternative | What it means | Chosen |
|---|---|---|
| Any fall | Strict: any drop gets looked at. | Yes |
| 0.1 of a star | Allows for small movements. | |
| 0.3 of a star | Relaxed: only a clear fall gets looked at. | |
| Set after first month | Record the score at launch, then set the limit from that. | |

## Round 15: Speed, capacity and availability

### 46. Speed

Speed (Y1): how long may a customer on a phone wait for the Feedback website's page
to open and for Send to finish?

| Alternative | What it means | Chosen |
|---|---|---|
| Up to 3 seconds (Recommended) | Customers are opening a link on a phone, and many give up if it's slow. Typical for an ordinary website. | |
| Up to 2 seconds | Better for customers, but it needs more care to build. | |
| Up to 5 seconds | Easier to build, but more people give up before sending. | Yes |

### 47. Orders

Capacity (Y2): about how many orders a month does your online shop platform take?
This sets how many requests go out. Use Other for an exact figure.

| Alternative | What it means | Chosen |
|---|---|---|
| Under 500 a month | Requests stay small in number. | Yes |
| 500 to 5,000 a month | A moderate volume. | |
| Over 5,000 a month | A higher volume to design for. | |
| I don't know | Stays open for whoever runs the shop. | |

### 48. Downtime

Availability (Y3): if the Feedback website goes down, how quickly must it be back?

| Alternative | What it means | Chosen |
|---|---|---|
| Within one working day (Recommended) | Fits a simple website with no one on call. Requests must wait and go out once it's back, so none are lost. | Yes |
| Within a few hours | Needs someone watching it during the day, so it costs more. | |
| Within a few days | The cheapest, but a customer who clicks a request link may find it down. | |

## Round 16: The target, security, accessibility and proof

### 49. Target

Your target is 50 to 200 pieces of feedback a month, but with under 500 orders that
means at least 10% to 40% of orders answering. Should the Feedback website's target
change?

| Alternative | What it means | Chosen |
|---|---|---|
| Start at 50 a month (Recommended) | Keeps the low end as the target, which needs at least 10% of orders to answer. Raise it once you have real figures. | Yes |
| Lower to 25 a month | Needs at least 5% of orders to answer. Easier to reach. | |
| Keep 50 to 200 | Keeps the range you chose, but the top end may never be reached. | |

### 50. Security

Security (Y4): what must the Feedback website withstand, given it holds customers'
contact details and their words?

| Alternative | What it means | Chosen |
|---|---|---|
| Standard protections (Recommended) | An encrypted connection, passwords never stored readable, and repeated sign-in failures blocked. | Yes |
| Standard + two-step sign-in | Staff also confirm each sign-in with a phone or app. Safer, but more to build and more steps for staff. | |

### 51. Accessibility

Accessibility (Y6): what standard must the Feedback website meet? Your legal adviser
can say whether the law requires one.

| Alternative | What it means | Chosen |
|---|---|---|
| WCAG 2.2 AA (Recommended) | The usual named standard, and usable with a keyboard or screen reader. Adds some testing. | Yes |
| No promised standard | Less to test, but no assurance for customers with disabilities. | |

### 52. Proof

Proof (Y9): what must the Feedback website be able to show later?

| Alternative | What it means | Chosen |
|---|---|---|
| Opt-outs and permissions (Recommended) | Dated records of who opted out and who allowed publishing, kept as long as they apply. | Yes |
| Those, plus who removed what | Also records which staff member removed each piece of feedback, and when. A little more to build. | |
| Nothing specific | Simplest, but you couldn't show that a customer gave permission. | |
