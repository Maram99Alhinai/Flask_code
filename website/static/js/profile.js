document.getElementById('saveButton').addEventListener('click', function () {
  var form = document.getElementById('myForm');

  var firstNameValue = document.getElementById('fname').value;
  var lastNameValue = document.getElementById('lname').value;

  var isValidFirstName = /^[A-Za-z\s]+$/.test(firstNameValue);
  var isValidLastName = /^[A-Za-z\s]+$/.test(lastNameValue);

  if (!isValidFirstName || !isValidLastName) {
    alert('First name and last name should contain text only (no numbers).');
  } else {
    form.submit();
    alert('Information Updated');
  }
});
