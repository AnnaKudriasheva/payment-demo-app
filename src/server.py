# settings.py
import base64
import logging
import os
import tempfile

import stripe
import ulid
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from stripe.error import StripeError
from pyngrok import ngrok

logging.basicConfig(level=logging.INFO)

load_dotenv()
app = Flask(__name__,
            static_url_path='',
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"))
CORS(app)
Transactions = {}

demo_public_url = ngrok.connect(proto='http', port=3000)
https_public_url = demo_public_url.replace('http', 'https')

print(f'\033[92m {"-"*40}\n \033[0m')
print(f'\033[92m   WELCOME TO VGS DEMO APPLICATION \U0001F440 \n\n')
print(f'\033[92m   To run application follow next steps:\n')
print(f'\033[92m   1. Copy PUBLIC URL \033[0m {https_public_url}\n')
print(f'\033[92m   2. OPEN inbound route \033[0m {os.getenv("INBOUND_ROUTE_LINK")}\n')
print(f'\033[92m   3. Set up PUBLIC URL as upstream host\n')
print(f'\033[92m   4. Open PUBLIC URL \033[0m {https_public_url}\n')
print(f'\033[92m {"-"*40}\n \033[0m')

@app.route('/', methods=['GET'])
@app.route('/credit-card.html', methods=['GET'])
def credit_card():
    return render_template('credit-card.html', VGS_COLLECT_LIBRARY_URL=os.getenv('VGS_COLLECT_LIBRARY_URL'));

@app.route('/js/credit-card-example.js', methods=['GET'])
def credit_card_form():
    return render_template('js/credit-card-example.js', VAULT_ID=os.getenv('VAULT_ID'), VGS_VAULT_ENV=os.getenv('VGS_VAULT_ENV'));

@app.route('/transaction_info', methods=['GET'])
def get():
    transaction_id = request.args.get('transaction_id')

    if transaction_id not in Transactions:
        return {'kind': 'not_found'}, 404

    if 'payment_intent' not in Transactions[transaction_id]:
        return {'kind': 'not_found'}, 404

    payment_intent_id = Transactions[transaction_id]['payment_intent']
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    except StripeError as e:
        return jsonify({'kind': 'error', 'message': e.user_message}), 400

    return jsonify({'kind': 'payment_intent', 'status': payment_intent['status'],
                    'cancellation_reason': payment_intent['cancellation_reason']}), 200


@app.route('/post', methods=['POST'])
def post():
    # create transaction
    transaction_id = ulid.new().str
    Transactions[transaction_id] = {}

    # create card on stripe
    # in this stage the data is redacted and it will be revealed through the vgs proxy
    # that is configured in the __main__ function
    exp_month, exp_year = request.json['card_expiration_date'].split('/')
    card = {
        'number': request.json['card_number'],
        'name': request.json['card_name'],
        'exp_month': int(exp_month.strip()),
        'exp_year': int(exp_year.strip()),
        'cvc': request.json['card_cvc'],
    }

    try:
        token_response = stripe.Token.create(card=card)
    except StripeError as e:
        return jsonify({'kind': 'error', 'message': e.user_message}), 400

    # create a costumer for this transaction, required by the payment intent stripe api
    try:
        customer_response = stripe.Customer.create(
            description=f'Customer for transaction {transaction_id}',
            source=token_response['id']  # obtained with Stripe.js
        )
    except StripeError as e:
        return jsonify({'kind': 'error', 'message': e.user_message}), 400

    # create payment intent
    try:
        pi_response = stripe.PaymentIntent.create(
            amount=request.json['amount'],
            currency='usd',
            payment_method=token_response['card']['id'],  # obtained with Stripe.js
            customer=customer_response['id'],
        )
    except StripeError as e:
        return jsonify({'kind': 'error', 'message': e.user_message}), 400

    # save payment intent id locally
    Transactions[transaction_id]['payment_intent'] = pi_response['id']

    # confirm intent and tell to stripe to redirect the user to a custom url after the 3ds flow ends
    try:
        intent_response = stripe.PaymentIntent.confirm(
            pi_response['id'],
            return_url=f'{https_public_url}/confirm_3ds.html?transaction_id={transaction_id}'
        )
    except StripeError as e:
        return jsonify({'kind': 'error', 'message': e.user_message}), 400

    # transaction does success and does not support 3d secure
    if not intent_response['next_action']:
        return jsonify({'kind': 'transaction_succeeded_without_3ds', 'transaction_id': transaction_id}), 200
    else:
        return jsonify(
            {'kind': 'action_redirect',
             'redirect_url': intent_response['next_action']['redirect_to_url']['url']}), 200


if not os.getenv('STRIPE_KEY'):
    raise Exception('STRIPE_KEY is missing')
if not os.getenv('VGS_PROXY'):
    raise Exception('VGS_PROXY is missing')
if not os.getenv('VGS_COLLECT_LIBRARY_URL'):
    raise Exception('VGS_COLLECT_LIBRARY_URL is missing')
if not os.getenv('VAULT_ID'):
    raise Exception('VAULT_ID is missing')
if not os.getenv('VGS_VAULT_ENV'):
    raise Exception('VGS_VAULT_ENV is missing')

fd, cert_path = tempfile.mkstemp()

try:
    with os.fdopen(fd, 'w') as tmp:
        # do stuff with temp file
        tmp.write(base64.b64decode(os.getenv('VGS_PROXY_CERTIFICATE_B64','LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tDQpNSUlEempDQ0FyYWdBd0lCQWdJR1pyNi95ZU9tTUEwR0NTcUdTSWIzRFFFQkRRVUFNSFF4SHpBZEJnTlZCQU1NDQpGaW91WkdWMkxuWmxjbmxuYjI5a2NISnZlSGt1YVc4eElUQWZCZ05WQkFvTUdGWmxjbmtnUjI5dlpDQlRaV04xDQpjbWwwZVN3Z1NXNWpMakV1TUN3R0ExVUVDd3dsVm1WeWVTQkhiMjlrSUZObFkzVnlhWFI1SUMwZ1JXNW5hVzVsDQpaWEpwYm1jZ1ZHVmhiVEFnRncweE5qQXlNRGt5TXpVek16WmFHQTh5TVRFM01ERXhOVEl6TlRNek5sb3dkREVmDQpNQjBHQTFVRUF3d1dLaTVrWlhZdWRtVnllV2R2YjJSd2NtOTRlUzVwYnpFaE1COEdBMVVFQ2d3WVZtVnllU0JIDQpiMjlrSUZObFkzVnlhWFI1TENCSmJtTXVNUzR3TEFZRFZRUUxEQ1ZXWlhKNUlFZHZiMlFnVTJWamRYSnBkSGtnDQpMU0JGYm1kcGJtVmxjbWx1WnlCVVpXRnRNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDDQpBUUVBMDk4cGtYUDZCRjVwYlhvNGxVMlZMc3lTQ29MVmVrN1p2TEFIUW9Ob29qd1Y2ZUpLNjZvRFl3d1pGdTd1DQpPQ3lHaTFxOU1vY0JmMWxDOWYwQi9DYlFHblN3QzFPVEtTKzgybGdKcGJ1d3VDSXBnK2krcGRYdjFZb0xOYUJHDQoyN1lkS2ZYSGlDeWQzMmZEN25HR1VCMm1paDNWZmszQzdFaGFOVmNTUjM1MmFaYm5CeU5xUG1UMlZHTG1raFcwDQpVMlVuOFQ3elRVR0wwL1JHdkNzUG5hUVRNWDJDM2hneTlWM09rajR4OTM1dGdpM2NXUkpNeXRLMzZBd0pvb3lxDQpTV3lzNXRrbStBTVBzald3WmdDdyt2Y09QSU9IR0l3VElsNFlOMk52YWMrVklpYzZoNUc1UWhRTVVFZU9XekpnDQpvQmdCb2srem82RWxvTUJld0ZlRFlxTTVrd0lEQVFBQm8yUXdZakFkQmdOVkhRNEVGZ1FVWm9oRzBtcHFiSEtkDQo2MmRjMzNBdVluYTQ4Z293RHdZRFZSMFRBUUgvQkFVd0F3RUIvekFMQmdOVkhROEVCQU1DQWJZd0l3WURWUjBsDQpCQnd3R2dZSUt3WUJCUVVIQXdFR0NDc0dBUVVGQndNQ0JnUlZIU1VBTUEwR0NTcUdTSWIzRFFFQkRRVUFBNElCDQpBUUFPMlNVRHJQQUVqMDZaYjN6N3pSWG1KbzQ5UGdINUZHOGgrQlNLMXdEQW5FT1lnOUw3MnlHK3NOSkpZOWk2DQpDMVRkZWFUdTFiV3pBcGhsa2RQalFlNGFGU29UR2ZGVDgweVNiYWFjcFZVZUdPRDFkdzU0QjVTWEhPUXl5RDZUDQpuY082VlRzd0s5Z0s5cW5uTkJxT2VicTBtUVcwMVBDWmtPMDFDMUVuQm1udHBwOWlnRVdCazJyVjVyQXBVQ0xNDQpWaHVIdUVtUTBhd0xFdTRNazIvZTZSRS94MWNOV0pERVJ2OW51R2p5ZUxnWWhYREtLWWNOdnYrNHNVQlcxb2ZzDQoxaTVONGk0aDhLanFraW4wZUtrWG9XS3R0WFhWMXZ1MERDL1g5Qi9rU0JMM1RzRU9zNE5rZzl4Mlo5a2h6THJuDQpKT2NuSFZaamMzZUoxVisrOUNxaDB2a1QNCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0=')).decode('utf8'))
    # configure stripe
    stripe.api_key = os.getenv('STRIPE_KEY')
    stripe.proxy = os.getenv('VGS_PROXY')
    stripe.ca_bundle_path = cert_path
    stripe.default_http_client = stripe.http_client.RequestsClient(
        verify_ssl_certs=stripe.verify_ssl_certs,
        proxy=stripe.proxy
    )
finally:
    print(cert_path)

if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0', debug=False)
