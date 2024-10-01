from flask import Flask, redirect, url_for,request
import paypalrestsdk
import config

app = Flask(__name__)

paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox hoặc live
    "client_id": config.PAYPAL_CLIENT_ID,
    "client_secret": config.PAYPAL_CLIENT_SECRET
})

@app.route('/')
def index():
    return 'Welcome to the PayPal Flask integration example!'

@app.route('/pay')
def pay():
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": url_for('payment_execute', _external=True),
            "cancel_url": url_for('index', _external=True)
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "item",
                    "sku": "item",
                    "price": "5.00",
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": "5.00",
                "currency": "USD"
            },
            "description": "This is the payment transaction description."
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                return redirect(approval_url)
    else:
        return 'Error while creating payment'

@app.route('/execute')
def payment_execute():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return 'Payment executed successfully'
    else:
        return 'Payment execution failed'

if __name__ == '__main__':
    app.run(debug=True)
