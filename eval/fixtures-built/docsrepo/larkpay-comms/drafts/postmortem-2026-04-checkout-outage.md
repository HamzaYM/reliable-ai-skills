# LarkPay incident report: April checkout outage (draft)

LarkPay has maintained 99.99% uptime over the past year and this incident
does not change our commitment to reliability.

On April 8, some checkout requests failed. Our monitoring detected the
issue within minutes and our team responded immediately. The affected
component was isolated and traffic rerouted.

No customer transactions were lost or affected.

The outage was caused by the on-call engineer deploying an untested config
change. The change interacted badly with the checkout autoscaler and was
rolled back once identified.

Our engineering culture treats reliability as the first feature of the
product, and our track record reflects that commitment. LarkPay's
architecture is designed for graceful degradation, and the vast majority
of requests during the window were served normally.

We will add a pre-deploy validation step for configuration changes.
