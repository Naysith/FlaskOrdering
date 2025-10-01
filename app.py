from flask import Flask, render_template, request, redirect, url_for, session
import database

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
    return render_template("menu.html", products=products, order_type=order_type, cart=cart)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    products = {p[0]: p for p in database.get_products()}  # use tuple indexes

    if product_id in products:
        product = products[product_id]
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += 1
        else:
            cart[str(product_id)] = {
                'name': product[1],
                'price': product[2],
                'quantity': 1
            }

    session['cart'] = cart
    order_type = request.args.get("type", "takeaway")
    return redirect(url_for('menu', type=order_type))

@app.route("/remove_from_cart/<product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    if product_id in cart:
        cart[product_id]['quantity'] -= 1
        if cart[product_id]['quantity'] <= 0:
            del cart[product_id]
    session["cart"] = cart

    order_type = request.args.get("type", "takeaway")
    return redirect(url_for("menu", type=order_type))

if __name__ == "__main__":
    app.run(debug=True)
