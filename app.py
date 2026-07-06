from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict_page')
def predict_page():
    return render_template('predict.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()

        stock = int(data.get('stock', 0))
        sales = list(map(int, data.get('sales', [])))

        
        df = pd.DataFrame({
            "Month": range(1, len(sales) + 1),
            "Sales": sales
        })

       
        X = df[["Month"]]
        y = df["Sales"]

        model = LinearRegression()
        model.fit(X, y)

        # Predict next month
        next_month = np.array([[len(sales) + 1]])
        prediction = int(model.predict(next_month)[0])

       
        growth = 0
        if len(sales) > 1 and sales[-2] != 0:
            growth = ((sales[-1] - sales[-2]) / sales[-2]) * 100

       
        if stock > prediction:
            status = "Sufficient Stock"
            color = "green"
        elif stock < prediction:
            status = "Low Stock"
            color = "red"
        else:
            status = "Optimal"
            color = "orange"

        labels = [f"Month {i+1}" for i in range(len(sales))]
        labels.append("Next Month")

        values = sales.copy()
        values.append(prediction)

        return jsonify({
            "prediction": prediction,
            "growth": round(growth, 2),
            "status": status,
            "color": color,
            "labels": labels,
            "values": values
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Something went wrong"}), 500



if __name__ == '__main__':
    app.run(debug=True)