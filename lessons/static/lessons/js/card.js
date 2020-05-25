function spinner_start() {
  $("#card-button").html(
    "<span class='spinner-border spinner-border-sm' " +
    "role='status' aria-hidden='true'></span>Processing..."
  );
  $("#card-button").attr("disabled", true);
}

function spinner_stop() {
  $("#card-button").html("Pay Now");
  $("#card-button").attr("disabled", false);
}

function card(stripe_publishable_key, customer_email) {
  document.addEventListener("DOMContentLoaded", function(event) { 
      var stripe = Stripe(stripe_publishable_key);
      // Create an instance of Elements.
      var elements = stripe.elements();

      // Custom styling can be passed to options when creating an Element.
      // (Note that this demo uses a wider set of styles than the guide below.)
      var style = {
        base: {
          color: '#32325d',
          fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
          fontSmoothing: 'antialiased',
          fontSize: '16px',
          '::placeholder': {
            color: '#aab7c4'
          }
        },
        invalid: {
          color: '#fa755a',
          iconColor: '#fa755a'
        }
      };

      // Create an instance of the card Element.
      var card = elements.create('card', {style: style});

      // Add an instance of the card Element into the `card-element` <div>.
      card.mount('#card-element');

      // Handle real-time validation errors from the card Element.
      card.addEventListener('change', function(event) {
        var displayError = document.getElementById('card-errors');
        if (event.error) {
          displayError.textContent = event.error.message;
        } else {
          displayError.textContent = '';
        }
      });

      // Handle form submission.
      var form = document.getElementById('payment-form');
      form.addEventListener('submit', function(event) {
        event.preventDefault();
        spinner_start();

        stripe.createToken(card).then(function(result) {
          if (result.error) {
            // Inform the user if there was an error.
            var errorElement = document.getElementById('card-errors');
            errorElement.textContent = result.error.message;
            spinner_stop();
          } else {
            // Send the token to your server.
            stripe.createPaymentMethod({
              type: 'card',
              card: card,
              billing_details: {
                email: customer_email,
              },
            }).then(function(payment_method_result){ 
              if (payment_method_result.error) {
                var errorElement = document.getElementById('card-errors');
                errorElement.textContent = payment_method_result.error.message;
                spinner_stop()
              } else {
                stripeTokenHandler(payment_method_result.paymentMethod);
              };
            })
          }
        }); // createToken
      }); // form.addEventListener(..)

      // Submit the form with the token ID.
      function stripeTokenHandler(payment_method) {
        // Insert the token ID into the form so it gets submitted to the server
        var form = document.getElementById('payment-form');
        var hiddenInput = document.createElement('input');
        hiddenInput.setAttribute('type', 'hidden');
        hiddenInput.setAttribute('name', 'payment_method_id');
        hiddenInput.setAttribute('value', payment_method.id);
        form.appendChild(hiddenInput);

        // Submit the form
        form.submit();
      }
  });  
}
