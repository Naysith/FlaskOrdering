from flask import Flask, render_template, request, redirect, url_for, session
import database
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/menu")
def menu():
    order_type = request.args.get("type", "takeaway")
    products = database.get_products()
    cart = session.get("cart", {})

    # ngitung total
    total = sum(item["price"] * item["quantity"] for item in cart.values())

    return render_template("menu.html",
                           products=products,
                           order_type=order_type,
                           cart=cart,
                           cart_total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = {}

    cart = session["cart"]
    products = {p[0]: {"id": p[0], "name": p[1], "price": p[2]} for p in database.get_products()}
    product = products.get(product_id)

    if product:
        if str(product_id) in cart:
            cart[str(product_id)]["quantity"] += 1
        else:
            cart[str(product_id)] = {
                "name": product["name"],
                "price": product["price"],
                "quantity": 1
            }

    session["cart"] = cart
    return redirect(url_for("menu"))

@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    if str(product_id) in cart:
        cart[str(product_id)]["quantity"] -= 1
        if cart[str(product_id)]["quantity"] <= 0:
            del cart[str(product_id)]
    session["cart"] = cart

    return redirect(url_for("menu"))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = session.get("cart", {})
    if not cart:
        return redirect(url_for("menu"))

    if request.method == "POST":
        customer_name = request.form["customer_name"]
        order_number = random.randint(1000, 9999)  # nomor struk

        # save order ke db
        order_id = database.create_order(cart, customer_name, order_number)

        # clear list cart
        session.pop("cart", None)

        return render_template("order_success.html", 
                               order_id=order_id, 
                               customer_name=customer_name, 
                               order_number=order_number)

    cart_total = sum(item["price"] * item["quantity"] for item in cart.values())
    return render_template("checkout.html", cart=cart, cart_total=cart_total)

if __name__ == "__main__":
    app.run(debug=True)
