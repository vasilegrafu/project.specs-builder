# Accounts and sign-in

- **What it is:** How a person becomes known to the product and proves who they are on each return. It covers sign-up, sign-in, a forgotten password, and staying signed in.
- **Applies when:** Anything is kept for a person between visits, or people must not see each other's data. It does not apply to a tool with no stored data, or one that sits behind a sign-in the organisation already runs.
- **If left unsaid:** Engineering builds email and password because it is the default, and the first customer who needs their company's sign-in cannot buy.
- **Ask:**
  1. Who creates an account: anyone, someone invited, or an administrator on their behalf?
  2. Do your users already have an identity you can lean on -- a work account, a Google or Microsoft account, a phone number?
  3. What do they lose if someone else gets into their account? That decides how strong sign-in must be.
  4. How long may someone stay signed in, and on how many devices?
  5. What happens when they forget their password or lose their phone?
- **Options:**
  - email and password -- the default everyone understands; you carry password reset, breached-password handling and the support load that comes with them.
  - magic link or one-time code -- no password to forget or leak; every sign-in depends on email or SMS arriving, which is slow for people who sign in many times a day.
  - sign in with Google, Microsoft or Apple -- least friction and least to build; fits where users certainly have that account, and excludes those who do not or will not use it.
  - company single sign-on -- what larger customers require before they buy; costly per customer, so it fits once such a customer is in sight.
- **First release:** One method, chosen by who the first users are: a social or work account for a business audience that has one, a magic link for occasional use, a password only if neither fits. Single sign-on waits for the first customer who asks, unless that customer is the first customer.
- **Often forgotten:** Verifying the email address before trusting it. Changing an email address. Two people sharing one login. What a signed-out user sees when they follow a link into the product. Locking after repeated wrong attempts. Whether an account can exist before its owner has ever signed in.
- **Becomes:** Requirements for sign-up, sign-in and recovery, each with its unwanted case; a security quality requirement; a non-goal for each method left out.
