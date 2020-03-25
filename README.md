## VGS for Payments quick start app
This demo application demonstrates secure payment data collection with [VGS Collect.js](https://www.verygoodsecurity.com/docs/vgs-collect/js/overview)and revealing this data to a third-party payment provider.

## How to use
* Install [docker](https://docs.docker.com/install/)
* Run `docker-compose up --build payment-demo`
* Follow the instructions in your terminal. After you run an application, you'll see a generated `PUBLIC URL` and link to the VGS dashboard. You need to open the VGS dashboard in your browser using the link and do updates on the inbound route: copy/paste `PUBLIC URL` as an upstream host.

All configurations are set in `.env` file in the project root directory using this template. This file is already pre-filled for your set up.

```.env
STRIPE_KEY=
VGS_PROXY=
VGS_COLLECT_LIBRARY_URL=
VAULT_ID=
VGS_COLLECT_ENV=
INBOUND_ROUTE_LINK=
```

where 

* `STRIPE_KEY`: Stripe Secret API Key (Stripe dashboard -> Developers -> API keys) 
* `VGS_PROXY`: full URL with credentials for the VGS outbound proxy, `https://USERNAME:PASSWORD@<vault_id>.SANDBOX.verygoodproxy.com:8080`
* `VGS_COLLECT_LIBRARY_URL`: https://dashboard.verygoodsecurity.com -> VGS Collect page
* `VAULT_ID`: https://dashboard.verygoodsecurity.com -> Settings -> Identifier
* `VGS_COLLECT_ENV`: VGS Vault environment, `sandbox|live`
* `INBOUND_ROUTE_LINK`: VGS inbound route link wich was created

## How to integrate into your own app

Check out these files:
* `src/public/credit-card.html` - Payments form with VGS Collect.js
* `src/public/js/credit-card-example.js` - VGS Collect.js init and fields configuration
* `src/server.py` - Server with requests to third-party payment provider

For more information please contact <a href="mailto:support@verygoodsecurity.com">support@verygoodsecurity.com </a>
