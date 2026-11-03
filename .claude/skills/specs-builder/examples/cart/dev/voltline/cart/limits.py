"""The numbers the cart holds to. Each is the shop's rule, named once here and read everywhere else."""

MAX_QTY_PER_LINE = 5            # of one product; the page says "Up to five of each"
MAX_LINES = 30                  # distinct products in one cart
FREE_DELIVERY_OVER = 50.00      # euros, on the subtotal after the discount
DELIVERY = 4.90                 # euros, under that
KEPT_FOR_DAYS = 30              # a signed-in customer's cart is kept this long after they last touched it
GUEST_KEPT_FOR_HOURS = 48       # a visitor's cart lives in the session cookie this long
CODE_PATTERN = r"^[A-Z0-9]{4,12}$"
