from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product/<product_name>')
def show_product(product_name):
    print("Product Name:", product_name)
    return render_template('details.html', product_name=product_name)

if __name__ == '__main__':
    app.run(debug=True)