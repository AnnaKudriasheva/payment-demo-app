// VGS Collect.js secure fields configuration
// https://www.verygoodsecurity.com/docs/vgs-collect/js/integration

var f = VGSCollect.create('{{VAULT_ID}}', '{{VGS_VAULT_ENV}}', function (state) {});

var field = f.field('#cc-name .form-control', {
    type: 'text',
    name: 'card_name',
    placeholder: 'Joe Business',
    validations: ['required'],
});

f.field('#amount .form-control', {
    type: 'number',
    name: 'amount',
    successColor: '#4F8A10',
    errorColor: '#D8000C',
    defaultValue: urlParams['amount'] || 100,
});

f.field('#cc-number .form-control', {
    type: 'card-number',
    name: 'card_number',
    successColor: '#4F8A10',
    errorColor: '#D8000C',
    placeholder: '4111 1111 1111 1111',
    validations: ['required', 'validCardNumber'],
    showCardIcon: true,
});

f.field('#cc-cvc .form-control', {
    type: 'card-security-code',
    name: 'card_cvc',
    placeholder: '344',
    validations: ['required', 'validCardSecurityCode'],
});

f.field('#cc-expiration-date .form-control', {
    type: 'card-expiration-date',
    name: 'card_expiration_date',
    placeholder: '01 / 2022',
    validations: ['required', 'validCardExpirationDate']
});

var elements = document.querySelectorAll('label');
for (var i = 0; i < elements.length; i++) {
    elements[i].addEventListener('click', function (t) {
        field.focus();
    });
}

document.getElementById('cc-form')
    .addEventListener('submit', function (e) {
        var targetForm = e.target;
        e.preventDefault();
        var form_error = $("#form-error");
        var valid_form = true;
        var keys = Object.keys(f.state);
        for (var key = 0; key < keys.length; key++) {
            valid_form = valid_form && f.state[keys[key]].isValid;
        }
        if (!valid_form) {
            return
        }
        form_error.text("");
        form_error.hide();
        $('#purchase-btn').prepend('<span id="purchase-loader" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        $('#purchase-btn').prop('disabled', true);

        //submit and send the amount of the transaction
        f.submit('/post', {}, function (status, data) {
            $('#purchase-loader').remove();
            $('#purchase-btn').prop('disabled', false);
            if (data && data.kind) {
                if (data.kind === "transaction_succeeded_without_3ds") {
                    var params = 'transaction_succeeded_without_3ds=true' +
                        '&transaction_id=' + data.transaction_id +
                        '&dashboard_logs_link=' + data.dashboard_logs_link;
                    window.location.replace('/payment_confirmation.html?' + params);

                } else if (data.kind === "action_redirect") {
                    //close modal
                    window.location.replace(data.redirect_url);
                } else if (data.kind === "error") {
                    form_error.text(data.message);
                    form_error.show();
                }
            }
            cleanErrorMessages(targetForm);
        }, function (errors) {
            highlightErrors(targetForm, errors);
        });
    }, false);
