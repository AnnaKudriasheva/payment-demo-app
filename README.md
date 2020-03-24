<p align="center">
 <a href="https://www.verygoodsecurity.com/" target="_blank">
  <img src="https://avatars0.githubusercontent.com/u/17788525" width="128" alt="VGS Logo">
 </a>

 <a href="https://stripe.com/" target="_blank">
  <img src="https://upload.wikimedia.org/wikipedia/commons/b/ba/Stripe_Logo%2C_revised_2016.svg" width="100" alt="VGS Logo">  </a>
</p>

<p align="center">
 <b>VGS + Stripe demo app</b><br/>
 Demo application with simple checkout form which send request to the Stripe API 
 through the <a href="https://www.verygoodsecurity.com/docs/vgs-collect/js/overview" target="_blank">VGS Collect.js</a>       library.
</p>

# Payment demo app
 This repository contains two key components:

* Python <a href="https://palletsprojects.com/p/flask/" target="_blank">Flask</a> server
* HTML with <a href="https://www.verygoodsecurity.com/docs/vgs-collect/js/overview" target="_blank">VGS Collect.js</a> secure checkout fields

## Requirements

* Account with <a href="https://www.verygoodsecurity.com/" target="_blank">VGS</a>
* <a href="https://docs.docker.com/install/" target="_blank">Docker</a>

## How to use

1. Run `docker-compose up --build payment-demo`
 
2. Follow the instructions in your terminal. After you run an application, you'll see a generated `PUBLIC URL` and link to the VGS dashboard. You need to open the VGS dashboard in your browser using the link and do updates on the inbound route: copy/paste `PUBLIC URL` as an upstream host.

## How to integrate into your own app

Check out these files:

* `src/public/credit-card.html`
* `src/public/js/credit-card-example.js` - copy VGS Collect.js integration and check additional library abilities in <a href="https://www.verygoodsecurity.com/docs/vgs-collect/js/overview" target="_blank">documentation</a>.
* `src/server.py`

For more information please contact <a href="mailto:support@verygoodsecurity.com">support@verygoodsecurity.com </a>