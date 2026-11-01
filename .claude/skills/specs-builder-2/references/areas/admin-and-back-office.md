# Admin and back office

- **What it is:** What you and your own team need in order to run the product for customers. It covers looking up an account, fixing what went wrong, and anything staff do that customers cannot.
- **Applies when:** Other people use the product and someone must help them. Every product with customers has a back office; the question is whether it is a screen or a person with database access.
- **If left unsaid:** Every support question becomes a request to an engineer to look in the database, and every correction is made by hand with no record.
- **Ask:**
  1. When a customer writes "it does not work", what will the person answering need to see?
  2. What will go wrong that the customer cannot fix themselves?
  3. Who on your side will do this work, and are they an engineer?
  4. Is there anything that must be approved, reviewed or moderated before customers see it?
  5. What may your staff see of a customer's data, and must the customer be told?
- **Options:**
  - engineers and the database -- no building; fits the first weeks with a few customers, and every request interrupts development.
  - a general admin tool over the data -- an off-the-shelf panel that lists and edits records; quick, and it bypasses the product's own rules, so it must be used with care.
  - staff screens inside the product -- purpose-built views for support; safe and pleasant, and a second product to maintain.
  - seeing the product as the customer sees it -- staff view an account as its user; answers most questions fastest, and needs a record of who looked at what.
- **First release:** Name the three things support will be asked most and make sure each can be done by someone, even if that is an engineer with a written procedure. Record every manual fix. Build a staff screen only for what is done weekly.
- **Often forgotten:** A record of what staff changed and when. Staff accounts being stronger targets than customer accounts. Corrections that should also notify the customer. Turning a single customer's account off. The difference between what staff can see and what they can change.
- **Becomes:** Requirements for each staff action that needs building; a security quality requirement for staff access; a proof quality requirement for staff changes; open questions for engineering about what can be done without building; non-goals for the rest.
