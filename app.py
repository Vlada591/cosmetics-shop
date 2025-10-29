from flask import Flask, request, make_response, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)

# 🔧 Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 🧱 Модель заказа
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    delivery = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    payment = db.Column(db.String(50), nullable=False)
    products = db.Column(db.Text, nullable=False)
    total = db.Column(db.Integer, nullable=False)

# 📦 Товары
products = [
    {'id': 1, 'name': 'Пудра Velvet Skin', 'description': 'Ніжна пудра для природного сяйва шкіри.', 'price': 299, 'image': 'powder.jpg'},
    {'id': 2, 'name': 'Тональна основа Glow Fit', 'description': 'Тон із ефектом зволоження та легкої текстури.', 'price': 349, 'image': 'foundation.jpg'},
    {'id': 3, 'name': 'Консилер Soft Touch', 'description': 'Ідеально маскує недоліки без ефекту маски.', 'price': 199, 'image': 'concealer.jpg'},
    {'id': 4, 'name': 'Туш для вій LN PRO GLOW UP', 'description': "Туш для вій GLOW UP Curl and Volume, чорна. Подаруйте віям об'єм та підкручування.", 'price': 148, 'image': 'glow-up.jpg'},
    {'id': 5, 'name': "Туш Eveline EXTENSION об'ємна", 'description': "Ефект накладних вій, XXL об'єм та розділення.", 'price': 150, 'image': 'eveline-extension.jpg'},
    {'id': 6, 'name': "Туш Maybelline Lash Sensational Firework", 'description': "Довжина, об'єм, виразність — з першого нанесення.", 'price': 416, 'image': 'maybelline-lash.jpg'},
    {'id': 7, 'name': "Гель-туш для брів L'Oreal Infaillible", 'description': "Ефект ламінування до 24 годин.", 'price': 504, 'image': 'gloreal-brow.jpg'},
    {'id': 8, 'name': "Гель для брів Eveline BROW&GOW", 'description': "Фіксація форми та природний вигляд.", 'price': 134, 'image': 'eveline-brow.jpg'},
    {'id': 9, 'name': "Крем-пудра Maybelline Superstay", 'description': "Стійке покриття до 24 годин.", 'price': 371, 'image': 'maybelline-superstay.jpg'},
    {'id': 10, 'name': "Олівець для губ Lumene LUMINOUS 3", 'description': "Легкий, точний контур, 1.1 г.", 'price': 215, 'image': 'lumene-pencil.jpg'},
    {'id': 11, 'name': "Помада L'Oréal Matte Resistanceе 105", 'description': "Матова, зволожуюча формула, гіалурон.", 'price': 417, 'image': 'loreal-matte-105.jpg'},
    {'id': 12, 'name': "Гель для вмивання Vichy Purete Thermale", 'description': "Освіжає, очищає, для чутливої шкіри.", 'price': 651, 'image': 'vichy-gel.jpg'},
    {'id': 13, 'name': "Сироватка-ролер FarmStay з ретинолом", 'description': "Омолодження, охолодження, менше зморшок.", 'price': 350, 'image': 'farmstay-serum.jpg'},
    {'id': 14, 'name': "Рідка помада-рум'яна Wonder Match 4B1", 'description': "2в1 рум'яна і губи, з ніацинамідом.", 'price': 190, 'image': 'wonder-match.jpg'},
    {'id': 15, 'name': "Консилер NYX Can't Stop Won't Stop", 'description': "Стійкий, маскує всі недоліки.", 'price': 210, 'image': 'nyx-concealer.jpg'},
    {'id': 16, 'name': "Пудра NYX High Definition 01", 'description': "HD-завершення макіяжу, мінерали.", 'price': 320, 'image': 'nyx-powder.jpg'}
]

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/catalog')
def catalog():
    return render_template('catalog.html', products=products)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return render_template('product.html', product=product)
    return "Товар не знайдено", 404

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = request.cookies.get('cart')
    cart = json.loads(cart) if cart else []
    cart.append(product_id)
    resp = make_response(redirect(url_for('catalog')))
    resp.set_cookie('cart', json.dumps(cart))
    return resp

@app.route('/cart')
def cart():
    cart = request.cookies.get('cart')
    cart = json.loads(cart) if cart else []
    cart_items = [p for p in products if p['id'] in cart]
    return render_template('cart.html', cart_items=cart_items)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = request.cookies.get('cart')
    cart = json.loads(cart) if cart else []
    cart_items = [p for p in products if p['id'] in cart]
    total = sum(item['price'] for item in cart_items)

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        delivery = request.form['delivery']
        address = request.form['address']
        payment = request.form['payment']

        order = Order(
            name=name,
            phone=phone,
            delivery=delivery,
            address=address,
            payment=payment,
            products=json.dumps(cart_items),
            total=total
        )
        db.session.add(order)
        db.session.commit()

        resp = make_response(render_template('thank_you.html', total=total))
        resp.set_cookie('cart', '', expires=0)
        return resp

    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/buy_now/<int:product_id>')
def buy_now(product_id):
    cart = [product_id]  # только один товар
    resp = make_response(redirect(url_for('checkout')))
    resp.set_cookie('cart', json.dumps(cart))
    return resp


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
