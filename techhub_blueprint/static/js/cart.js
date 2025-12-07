// TechHub Electronics - Shopping Cart JavaScript (Early 2000s Style)

// Update cart quantity
function updateQuantity(productId) {
    var quantity = document.getElementById('qty-' + productId).value;
    if (quantity < 1) {
        if (confirm('Remove this item from cart?')) {
            window.location.href = '/techhub/remove_from_cart/' + productId;
        } else {
            document.getElementById('qty-' + productId).value = 1;
        }
    } else {
        var form = document.getElementById('update-form-' + productId);
        if (form) {
            form.submit();
        }
    }
}

// Confirm removal
function confirmRemove(productName) {
    return confirm('Are you sure you want to remove ' + productName + ' from your cart?');
}

// Confirm delete (admin)
function confirmDelete(itemType, itemName) {
    return confirm('Are you sure you want to delete this ' + itemType + '?\n\n' + itemName);
}

// Form validation
function validateForm(formId) {
    var form = document.getElementById(formId);
    var inputs = form.querySelectorAll('input[required]');
    var valid = true;

    for (var i = 0; i < inputs.length; i++) {
        if (!inputs[i].value.trim()) {
            inputs[i].style.borderColor = '#CC0000';
            valid = false;
        } else {
            inputs[i].style.borderColor = '#999';
        }
    }

    if (!valid) {
        alert('Please fill in all required fields (marked with *)');
    }

    return valid;
}

// Credit card formatting (basic)
function formatCreditCard(input) {
    var value = input.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    var matches = value.match(/\d{4,16}/g);
    var match = (matches && matches[0]) || '';
    var parts = [];

    for (var i = 0, len = match.length; i < len; i += 4) {
        parts.push(match.substring(i, i + 4));
    }

    if (parts.length) {
        input.value = parts.join('-');
    } else {
        input.value = value;
    }
}

// Simple image preview
function previewImage(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var preview = document.getElementById('image-preview');
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Add to cart animation (simple alert for authenticity)
function addToCartAnimation(productName) {
    alert(productName + ' has been added to your cart!');
}

// Auto-submit search form on category change
function autoSubmitSearch() {
    document.getElementById('search-form').submit();
}
