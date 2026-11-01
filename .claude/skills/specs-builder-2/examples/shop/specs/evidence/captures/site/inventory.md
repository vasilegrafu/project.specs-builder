# The Voltline shop: inventory

Every view of the shop in scope, and the file its capture is in.
The procedure is in the skill's references/reading-a-live-site.md: the breadth by crawl.py's capture, view by view, with one row for every page of a kind; the forms, the signed-in world and the admin by hand, nothing sent.

- **Address:** http://127.0.0.1:8080/
- **Scope:** 127.0.0.1:8080, the demo shop served from examples/shop/dev
- **Walked:** 2026-10-11, signed out first; then signed in as Ana, the test customer, who is the shop's admin too; then the admin's door as Tom, a customer who is not; the sign-in, sign-up and password forms filled and refused by hand, nothing sent
- **Browser:** Chromium, driven by crawl.py's capture and watch scripts
- **Widths:** 1280, 768 and 375 looked at; screenshots kept at 1280 and 375

## Views

| View | Address | How reached | Capture |
|---|---|---|---|
| V1 | /, the home page | the address given | V1-the-home-page.md |
| V2 | /index.html, the home page by its file name | V1, the link Voltline | not captured: it is V1, which the shop's mark and Continue shopping link by this name |
| V3 | /c/{category}/index.html, a category's first page | V1, the link Laptops | V3-laptops-a-category.md |
| V4 | /c/{category}/page-2.html, a category's second page | V3, the link 2 | V4-laptops-page-2.md |
| V5 | /p/{slug}, a product in stock, with a deal | V1, the link Aero 14 | V5-aero-14-a-product-with-a-deal.md |
| V6 | /p/{slug}, a product with only a few left | V3, the link Nomad 13 | V6-nomad-13-a-product-with-few-left.md |
| V7 | /p/{slug}, a product out of stock | V4, the link Zen 12 | V7-zen-12-a-product-out-of-stock.md |
| V8 | /search.html?q={}, the search's results | V1, the link headphones | V8-search-results-for-headphones.md |
| V9 | /search-no-results.html?q={}, a search that finds nothing | V1, the link quantum toaster | V9-a-search-with-nothing-found.md |
| V10 | /cart-empty.html, the empty cart | V1, the link Cart 0, signed out | V10-the-empty-cart.md |
| V11 | /sign-in.html | V1, the link Sign in | V11-sign-in.md |
| V12 | /sign-in-refused.html, a sign-in refused | V11, Sign in with a wrong password, by hand | V12-sign-in-refused.md |
| V13 | /sign-up.html | V1, the link Sign up: a stop point for crawl.py, opened by hand and nothing sent | V13-create-an-account.md |
| V14 | /sign-up-errors.html, the sign-up form refused | V13, Create account with three fields wrong, by hand | V14-create-an-account-refused.md |
| V15 | /forgot-password.html | V11, the link Forgot your password? | V15-forgot-your-password.md |
| V16 | /forgot-password-sent.html, the link sent | V15, Send the link with the test account's email, by hand | V16-the-link-sent.md |
| V17 | /about.html | V1, the link About | V17-about.md |
| V18 | /contact.html | V1, the link Contact | V18-contact.md |
| V19 | /terms.html | V1, the link Terms | V19-terms.md |
| V20 | /shipping.html | V1, the link Shipping & returns | V20-shipping-and-returns.md |
| V21 | /cart.html, the cart with lines | V5, Add to cart, signed in as Ana | V21-the-cart.md |
| V22 | /checkout.html | V21, the link Checkout | V22-checkout.md |
| V23 | /account/profile.html, the profile | the account menu, Profile, signed in as Ana | V23-my-account-the-profile.md |
| V24 | /account/orders.html, my orders | V23, the link My orders | V24-my-orders.md |
| V25 | /account/orders/{number}, one of my orders | V24, the link VL-1042 | V25-order-vl-1042-mine.md |
| V26 | /admin/orders.html, the admin's orders | V23, the link Admin · orders, signed in as Ana, who is the admin | V26-admin-the-orders.md |
| V27 | /admin/orders-open.html, the open orders | V26, the link Open (3) | V27-admin-the-open-orders.md |
| V28 | /admin/orders-shipped.html, the shipped orders | V26, the link Shipped (4) | V28-admin-the-shipped-orders.md |
| V29 | /admin/orders-cancelled.html, the cancelled orders | V26, the link Cancelled (1) | V29-admin-the-cancelled-orders.md |
| V30 | /admin/orders/{number}, an order for the admin | V27, the link VL-1047 | V30-admin-order-vl-1047.md |
| V31 | /admin/forbidden.html, the admin's door for a customer | /admin/orders.html opened as Tom, a customer who is not the admin, by hand | V31-the-admins-door-for-a-customer.md |
| V32 | /signed-out.html | V23, the link Sign out | V32-signed-out.md |
| V33 | /no-such-page-{id}, an address of the site that does not exist | an address of the site that does not exist | V33-an-address-that-does-not-exist-404.md |
| V34 | /account/orders/{number}, one of my orders, still placed | V24, the link VL-1047 | V34-order-vl-1047-mine-placed.md |
