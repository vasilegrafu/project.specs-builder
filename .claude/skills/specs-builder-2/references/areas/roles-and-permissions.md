# Roles and permissions

- **What it is:** Who may see and do what. It covers the roles a product has, what each can do, and who hands roles out.
- **Applies when:** More than one kind of person uses the product, or one person's data must be hidden from another. A product with a single user per account and nothing shared needs only "your own data, nobody else's".
- **If left unsaid:** Everyone can do everything, or engineering invents a permission system far larger than anyone needs. Adding the first restriction later means touching every screen.
- **Ask:**
  1. List everyone who will use it. For each, what must they be able to do, and what must they never do?
  2. Is there anything one user creates that another must not see?
  3. Who decides what a person may do -- the product owner, an administrator at the customer, each user for their own things?
  4. Is there an action so damaging that only some may take it: deleting, paying, exporting, inviting?
  5. Does anyone need to see without being able to change?
- **Options:**
  - one role -- everyone in an account can do everything; nothing to build, and right while accounts are one person or a few who trust each other.
  - a few fixed roles -- for example owner, member and read-only; covers most products for years and is explained in one sentence each.
  - roles the customer defines -- customers compose permissions themselves; a product in its own right, justified only when customers' organisations differ too much for fixed roles.
  - sharing per item -- the owner of a thing chooses who sees it; fits documents and projects, and brings the question of what happens when the owner leaves.
- **First release:** One role, or two if there is a real action only some may take. Write the rule as requirements, not as a system: "only the owner may delete the workspace". Customer-defined roles are a non-goal until fixed roles demonstrably fail.
- **Often forgotten:** What a user without permission sees: the control hidden, disabled, or an error. Who can remove the last administrator. What happens to things a person owned when their access is taken away. Whether support staff can see customer data, and whether the customer is told.
- **Becomes:** A requirement per restricted action with the criterion for the refused case; a security quality requirement; the role names in the glossary; a non-goal for the richer model.
