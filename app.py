#! /usr/bin/env python3.6
"""
Python 3.6 or newer required.
"""
import json
import os
import stripe
from flask import Flask, render_template, jsonify, request
# This is your test secret API key.
stripe.api_key = 'sk_test_51L1wZaSEXQs35PRIf3i9BxVH5zj9PZc1swGE6GT6aYWD4u0vy6NQedDt8h6fkKIxCGJEQJH2IoGMiSL6dpijq5YJ000vqXfQwS'

# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = 'whsec_3eb2af9c0aec59103a440685e1efc410de4c8c02f99d1b29ef7cdc730c93b3f1'


app = Flask(__name__, static_folder='static',
            static_url_path='/', template_folder='template')


def calculate_order_amount(items):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    return 1400

@app.route('/')
def hello():
    return render_template('checkout.html')


@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        data = json.loads(request.data)
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=calculate_order_amount(data['items']),
            currency='inr',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        return jsonify({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/success')
def success():
    return {"msg":"Congrats your payments has been successfully completed"}

@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
      payment_intent = event['data']['object']
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)


if __name__ == '__main__':
    app.run(port=4242,debug=True)


# run the flask file by using: python3 -m flask run --port=4242

# Run the command where the stripe app is installed

# For running webhook first install stripe cli: https://stripe.com/docs/stripe-cli   and use ./stripe instead of stripe
# For using stripe CLI see the commands : https://dashboard.stripe.com/test/webhooks/create?endpoint_location=local
