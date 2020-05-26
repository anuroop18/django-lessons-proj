function _3dsec(stripe_publishable_key, pi_secret) {
    document.addEventListener("DOMContentLoaded", function(event){
      var stripe = Stripe(stripe_publishable_key);

      stripe.confirmCardPayment(pi_secret).then(function(result) {
        if (result.error) {
          // Display error.message in your UI.
          $("#3ds_result").text(
            "Error occured during payment process. Please contact me via email: eugen@django-lessons.com, I will assist you."
          );
          $("#3ds_result").addClass("text-danger");
        } else {
          // The payment has succeeded. Display a success message.
          $("#3ds_result").text(
            "Thank you! It may take 2-3 minutes to process the payment and upgrade your account."
          );
          $("#3ds_result").addClass("text-success");
        }
      });
    }); // DOMContentLoaded
}