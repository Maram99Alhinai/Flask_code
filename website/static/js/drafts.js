document.addEventListener('DOMContentLoaded', function () {
  const emailInput = document.getElementById('email');
  const emailInputContainer = document.getElementById('email-input-container');

  emailInput.addEventListener('keydown', function (event) {
    if (event.key === ' ' || event.key === 'Spacebar') {
      event.preventDefault();
      const currentValue = emailInput.value.trim();
      if (currentValue !== '') {
        // Create a new email item with a remove button
        const emailItem = document.createElement('span');
        emailItem.className = 'email-item';
        emailItem.textContent = currentValue;

        const removeButton = document.createElement('span');
        removeButton.className = 'remove-icon';
        removeButton.innerHTML = 'x';

        removeButton.addEventListener('click', function () {
          emailInputContainer.removeChild(emailItem);
        });

        emailItem.appendChild(removeButton);
        emailInputContainer.appendChild(emailItem);

        emailInput.value = ''; // Clear the input field
      }
    }
  });
});


// Populate the share popup 
$(document).ready(function () {
  $('.u-icon-3').on('click', function () {
    var shareLink = $(this).data('share-link');
    var formTitle = $(this).data('form-title');
    var respoNum = $(this).data('respo-num');
    $('#share-link-input').val(shareLink);
    $('#staticBackdropLabel').text(formTitle + ' ' + respoNum);
  });
});

// send emails to the backend 
// send emails to the backend 
$('button[data-bs-dismiss="modal"]').on('click', function () {
  // Extract email addresses
  var emails = [];
  $('.email-item').each(function () {
    emails.push($(this).text().trim());
  });

  var formId = $('.u-icon-3').data('form-id');

  // Print the value of the data-form-id attribute
  console.log('The form ID:', formId);

  // Send emails to the backend
  $.ajax({
    url: '/my_darfts',
    type: 'POST',
    contentType: 'application/json', // Add this line
    data: JSON.stringify({
      'emails': emails,
      'formId': formId
    }),
    success: function (response) {
      // Handle the response from the backend
      console.log(response);
    }
  });
});

function confirmDelete(formId, deleteUrl) {
  if (confirm("Are you sure you want to delete this form?")) {
    $.ajax({
      url: deleteUrl,
      type: 'POST',
      success: function (response) {
        if (response.result == 'success') {
          // Remove the card from the DOM
          $('#' + formId).remove();
        }
      }
    });
  }
}

function copyLink() {
  // Get the input field
  var copyText = document.getElementById("share-link-input");

  // Select the text in the input field
  copyText.select();
  copyText.setSelectionRange(0, 99999); // For mobile devices

  // Copy the text to the clipboard
  document.execCommand("copy");

  // Deselect the text
  copyText.setSelectionRange(0, 0);

  // Optionally, you can provide some feedback to the user
  alert("Link copied: " + copyText.value);
}

/// For social media post 
$(document).ready(function () {
  $('.social-button').on('click', function (e) {
    e.preventDefault(); // Prevent the default action (i.e., navigating to the social media site)

    var formTitle = $('.u-icon-3').data('form-title');
    var respoNum = $('.u-icon-3').data('respo-num');
    var shareLink = $('.u-icon-3').data('share-link');
    var formId = $('.u-icon-3').data('form-id');

    var share_data = {
      formTitle: formTitle,
      respoNum: respoNum,
      shareLink: shareLink,
      formId: formId
    };
    // Print the value of the data-form-id attribute
    console.log('The form ID:', share_data);
    $.ajax({
      url: '/my_forms/social', // Replace with your Flask route
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(share_data),
      dataType: 'json',
      success: function (response) {
        // Update the social media links with the new URLs
        $('.twitter').attr('href', response.twitter);
        $('.facebook').attr('href', response.facebook);
        $('.instagram').attr('href', response.instagram);

        // Navigate to the social media site
        window.location.href = $(e.target).closest('a').attr('href');
      },
      error: function (error) {
        // Handle any errors
      }
    });
  });
});

