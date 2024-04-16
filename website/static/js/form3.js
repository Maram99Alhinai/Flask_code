// function duplicateQuestion() {
//   questionCount++;
//   const clone = createQuestionSection(questionCount);
//   document.querySelector('.container.content').appendChild(clone);
// }

// duplicateQuestion
function duplicateQuestion(e) {
    // Check if there are any existing questions
    let questionCount = document.querySelectorAll('.question').length;
    if (questionCount === 0) {
      // If no questions exist, create a new question section
      createNewQuestion();
    } else {
      // Clone the question section
      const clonedQuestion = e.closest(".row.question");
      let clone = clonedQuestion.cloneNode(true);

      // Manually handle the cloning of the select element
      let originalSelect = clonedQuestion.querySelector('select');
      let clonedSelect = clone.querySelector('select');
      clonedSelect.value = originalSelect.value;
      
      questionCount++;
      clone.setAttribute('id', 'inputFields' + questionCount);
  
      // Update the label for the new question
      let questionLabel = clone.querySelector('label[for="question"]');
      questionLabel.textContent = 'Question ' + questionCount;
  
      let container = document.querySelector('.container.content');
      container.appendChild(clone);
  
      // Renumber existing questions
      renumberQuestions();
    }
  }
  
  function deleteQuestion(e) {
    const question = e.closest(".row.question");
      question.remove();
      renumberQuestions();
  }
  
  // function deleteAllQuestions() {
  //   while (questionCount > 1) {
  //     deleteQuestion('inputFields' + questionCount);
  //   }
  // }
  
  function renumberQuestions() {
    const questionSections = document.querySelectorAll('.question');
    questionSections.forEach((section, index) => {
      const questionLabel = section.querySelector('label[for="question"]');
      questionLabel.textContent = 'Question ' + (index + 1);
      section.id = 'inputFields' + (index + 1);
    });
  }
  function resetAnswer(selectElement) {
    const questionSection = selectElement.parentElement.parentElement;
    const answerContainer = questionSection.querySelector(`#answerContainer_${questionSection.id.split('inputFields')[1]}`);
    const questionType = selectElement.value;
  
    // Clear previous content
    answerContainer.innerHTML = '';
  
    if (questionType === 'multi_option') {
      // If the question type is multi_option, show the radio buttons or other options
      answerContainer.innerHTML = createOptions(questionSection.id.split('inputFields')[1]);
    }
    // You can add additional conditions for other question types if needed
  }
  
  
  
  function createNewQuestion() {
    // Find the number of existing questions
    const existingQuestions = document.querySelectorAll('.input-fields');
    const questionNumber = existingQuestions.length + 1;
    const counter = document.getElementsByClassName('question').length + 1;
  
    // Create a new question section
    let container = document.querySelector('.container.content');
    let newQuestionSection = document.createElement('section');
    newQuestionSection.className = 'custom-section input-fields';
    newQuestionSection.id = 'inputFields' + questionNumber;
    newQuestionSection.innerHTML = `
    <div class="row question" >
    <div class="col-md-12" style="border: 1px solid #88CDEB;
    border-radius: 27px;
    margin-bottom: 10px;
    width: 98%;
    margin-left: 11px;">
      <section class="custom-section">
        <div class="input-fields position-relative" id="inputFields${counter}">
          <div class="row mb-3">
            <div class="col-9">
              <label for="question" class="form-label">Question ${counter}</label>
              <input type="text" name="question" class="form-control inputraduis" id="question${counter}"
                placeholder="Write your question here">
            </div>
            <div class="col-3">
              <label for="questionType" class="form-label">Question Type</label>
              <select class="form-select" id="questionType${counter}" style="border-radius: 22px;" onchange="handleQuestionTypeChange(this)">
                <option value="simple_text">Simple Text</option>
                <option value="multi_option"><i class=" fa fas fa-plus-circle"></i>Multi-Option</option>
              </select>
            </div>
          </div>
          <div class="row mb-3">
            <div class="col" id="answerContainer_${questionNumber}">
              <!-- <input type="text" class="form-control inputraduis" id="answer" placeholder="Write your answer"> -->
            </div>
          </div>
          <div class="action-section col-12 d-flex justify-content-end">
            <button type="button" class="btn Require ">
              <input type="checkbox" class="checkbox"> Require
            </button>
            <button type="button" class="btn  me-2" onclick="duplicateQuestion(this)">
              <i class="far fa-copy"></i> Duplicate
            </button>
            <button type="button" class="btn  delete me-2" onclick="deleteQuestion(this)">
              <i class="far fa-trash-alt"></i> Delete
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
  </div>
  `;
  
    container.appendChild(newQuestionSection);
  }
  
  
  function handleQuestionTypeChange(selectElement) {
    const questionType = selectElement.value;
    const answerContainer = selectElement.parentElement.parentElement.nextElementSibling;
  
    if (questionType === 'multi_option') {
      // Show radio buttons and the "add new option" label
      let counter = document.getElementsByClassName('question').length  + 1;
      
      answerContainer.innerHTML = createRadioButtons(counter); // Start with one radio button
      const addOptionLabel = document.createElement('label');
      addOptionLabel.setAttribute('for', 'addoption_1');
      addOptionLabel.style.cursor = 'pointer';
      addOptionLabel.style.background = '#88CDEB';
      addOptionLabel.style.color = 'white';
      addOptionLabel.style.width = '180px';
      addOptionLabel.style.borderRadius = '20px';
      addOptionLabel.style.position = 'relative';
      addOptionLabel.style.display = 'inline-block';
      addOptionLabel.style.marginLeft = '13px';
  
  
      // Create the font-awesome icon
      const plusCircleIcon = document.createElement('i');
      plusCircleIcon.className = 'fa-solid fa-plus';
      addOptionLabel.appendChild(plusCircleIcon);
  
      // Add a space between the icon and the label text
      addOptionLabel.appendChild(document.createTextNode(' '));
  
      // Add the label text
      addOptionLabel.appendChild(document.createTextNode('add new option'));
  
      // Set the click event for the label
      //addOptionLabel.onclick = () => addNewRadioOption(counter);
      addOptionLabel.setAttribute('onclick', 'addNewRadioOption(' + (counter-1) + ', this)');
  
      // Append the label to the answer container
      answerContainer.appendChild(addOptionLabel);
    } else {
      // Clear the answer container
      answerContainer.innerHTML = '';
    }
  }
  
  //with old style
  function addNewOption(questionNumber) {
    const answerContainer = document.querySelector(`#answerContainer_${(questionNumber-1)}`);
    const optionCount = answerContainer.querySelectorAll('.options').length + 1;
    const optionInput = `
      <div class="col options">
        <input type="text" class="form-control inputraduis" id="option_${(questionNumber)}_${optionCount}" placeholder="Option ${optionCount}">
        <br>
      </div>
    `;
    console.log(answerContainer.innerHTML);
    answerContainer.innerHTML += optionInput;
  }
  
  //createRadioButtons
  function createRadioButtons(questionNumber) {
    const radioHTML = `
    <div class="row" id="answerContainer_${(questionNumber-1)}">
      <div class="form-group d-flex algin-items-center">
          <i class="fas fa-times-circle pt-1 me-3" style="color: #88CDEB;cursor: pointer;" onclick="deleteRadioOption(${(questionNumber-1)}, 1)"></i>
          <div class="form-check">
          <input class="form-check-input" type="checkbox" id="option_${(questionNumber-1)}_1" name="fav_language_${questionNumber}" value="option 1">
          <input class="form-check-label" type="text" placeholder="option" id="fname_${questionNumber}_1" name="fname_${questionNumber}_1">
        </div>
      </div>
    </div>  
  `;
    return radioHTML;
  }
  
  function addNewRadioOption(questionNumber, e) {
    console.log(e);
    //const answerContainer = document.querySelector(`#answerContainer_${questionNumber}`);
    const answerContainer = e.previousElementSibling;
    const radioCount = answerContainer.querySelectorAll('.form-check').length + 1;
    const newContainerId = `answerContainer_${questionNumber}_${radioCount}`;
    
    // Create a new div element
    const newRadioOption = document.createElement('div');
    newRadioOption.className = 'row';
    newRadioOption.id = newContainerId;
  
    // Set the inner HTML content for the new radio option
    newRadioOption.innerHTML = `
      <div class="form-group d-flex algin-items-center">
          <i class="fas fa-times-circle pt-1 me-3" style="color: #88CDEB;cursor: pointer;" onclick="javascript:this.parentElement.remove()"></i>
          <div class="form-check">
          <input class="form-check-input" type="checkbox" id="option_${(questionNumber-1)}_${radioCount}" name="fav_language_${questionNumber}" value="option ${radioCount}">
          <input class="form-check-label" type="text" placeholder="option" id="fname_${(questionNumber-1)}_${radioCount}" name="fname_${questionNumber}_${radioCount}">
        </div>
      </div>
    `;
  
    // Append the new radio option to the answerContainer
    answerContainer.appendChild(newRadioOption);
  }
  
  function deleteRadioOption(containerId) {
    const answerContainer = document.getElementById(containerId);
  
    if (answerContainer) {
      answerContainer.parentElement.removeChild(answerContainer);
    }
  }



//// for edit mode 
function addOptions(questionNumber, answerContainerId, optionNumber) {
  
  //const answerContainer = document.querySelector(`#answerContainer_${questionNumber}`);
  const answerContainer = document.getElementById(answerContainerId);
  const radioCount = optionNumber;
  const newContainerId = `answerContainer_${questionNumber}_${radioCount}`;
  
  // Create a new div element
  const newRadioOption = document.createElement('div');
  newRadioOption.className = 'row';
  newRadioOption.id = newContainerId;
  
  // Set the inner HTML content for the new radio option
  newRadioOption.innerHTML = `
    <div class="form-group d-flex algin-items-center">
        <i class="fas fa-times-circle pt-1 me-3" style="color: #88CDEB;cursor: pointer;" onclick="javascript:this.parentElement.remove()"></i>
        <div class="form-check">
        <input class="form-check-input" type="checkbox" id="option_${(questionNumber)}_${radioCount}" name="fav_language_${questionNumber}" value="option ${radioCount}">
        <input class="form-check-label" type="text" placeholder="option" id="fname_${(questionNumber)}_${radioCount}" name="fname_${questionNumber}_${radioCount}">
      </div>
    </div>
  `;
  
  // Append the new radio option to the answerContainer
  answerContainer.appendChild(newRadioOption);
  }
  
  function deleteRadioOption(containerId) {
  const answerContainer = document.getElementById(containerId);
  
  if (answerContainer) {
    answerContainer.parentElement.removeChild(answerContainer);
  }
  }  
  

 


  if (!editMode) {
    console.log("start ......");
    document.addEventListener("DOMContentLoaded", function () {
      const form = document.getElementById("myForm");
  
      form.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent the default form submission
        console.log("2nd ......");
        // Get the form data as a JSON object
        const formData = {};
  
        // Add 'title' and 'description' fields to formData
        const titleInput = form.querySelector('input[name="title"]');
        if (titleInput) {
          formData['title'] = titleInput.value;
        }
  
        const descriptionInput = form.querySelector('input[name="description"]');
        if (descriptionInput) {
          formData['description'] = descriptionInput.value;
        }
        console.log("3rd ......");
        const questionElements = form.querySelectorAll('div.input-fields');
  
        questionElements.forEach((questionElement, index) => {
          const questionNum = index + 1;
          console.log("the number", questionNum);
          // Log the question ID
          const questionId = questionElement.id;
          console.log("Question ID:", questionId);
          // Add 'question' and 'question type' fields to formData
          const questionInput = questionElement.querySelector('.row.mb-3 input[id^="question"]');
          const questionName = `question_${questionNum}`;
          formData[questionName] = questionInput ? questionInput.value : null;
  
          const questionTypeSelect = questionElement.querySelector('select');
          const questionTypeName = `ans_type_${questionNum}`;
          formData[questionTypeName] = questionTypeSelect ? questionTypeSelect.value : null;
          console.log("4th ......");
  
          // Include the "Require" status in the form data
          const requireButton = questionElement.querySelector('.btn.Require');
          const requireCheckbox = requireButton.querySelector('.checkbox');
          const requireStatus = requireCheckbox.checked ? 1 : 0;
          const requireName = `require_${questionNum}`;
          formData[requireName] = requireStatus;
  
          // Handle options for multi-option questions
          if (questionTypeSelect.value === 'multi_option') {
            const optionElements = questionElement.querySelectorAll('input[id^="option"]');
            optionElements.forEach((optionElement, optionIndex) => {
              const optionCount = optionIndex + 1;
              const optionName = `option_${questionNum}_${optionCount}`;
              formData[optionName] = optionElement.nextElementSibling.value;
            });
          }
  
          // Move the event listener registration outside of the loop
          // Use a closure to capture the correct values
          requireButton.removeEventListener('click', null); // Remove any existing event listeners
          requireButton.addEventListener('click', function () {
            formData[requireName] = requireCheckbox.checked ? 1 : 0;
            console.log("the number 2", questionNum);
          });
        });
  
        console.log(formData); // Log the form data to the console
        console.log("5th ......");
          // Send the data to the server as JSON with the correct 'Content-Type'
          fetch('/my_form3', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
          })
            .then(response => {
              if (response.redirected) {
                window.location.href = response.url;
              }
              return response.json();
            })
            .then(data => {
              // handle your data
            })
            .catch(error => {
              console.error('Error:', error);
             
            });
         
        });
  
      });
  
  
    } else {
  
      console.log("edit mode ......");
  
      document.addEventListener("DOMContentLoaded", function () {
        //console.log('data',questionsData)
        // Populate the form title and description
        document.getElementById("form_title").value = formData.form_title;
        document.getElementById("descriptiontext").value = formData.description;
  
  
        // Loop through each page in the questionsData
        for (let page in questionsData.questions) {
          console.log(page);
          // Loop through each question in the current page
          for (let question in questionsData.questions[page]) {
            console.log(question);
            // Check if it's not the first question
            if (question !== 'question_1') {
              // Create a new question section
              createNewQuestion();
  
            }
  
            // Remove the underscore from the question key to match the ID in the HTML
            let questionId = question.replace('_', '');
  
            // Populate the question text
            let questionElement = document.getElementById(questionId);
            questionElement.value = questionsData.questions[page][question].question;
            //console.log(questionElement.value);
  
  
            //require state
            let fieldId = question.replace('question_', 'inputFields');
            let inputFieldsDiv = document.getElementById(fieldId);
            let checkboxElement = inputFieldsDiv.querySelector('.checkbox');
            checkboxElement.checked = questionsData.questions[page][question].require
  
  
  
            // Change answer type 
            let questiontypeId = question.replace('question_', 'questionType');
            //make sure to chose the select with the correct id 
            let questionTypeSelect = document.getElementById(questiontypeId);
            // Set the selected option for question type based on questionDetails
            let selectedOption = Array.from(questionTypeSelect.options).find(option => option.value === questionsData.questions[page][question].answer_type);
  
            // If the selected option exists, set it as selected
            if (selectedOption) {
              selectedOption.selected = true;
            }
  
            // Call the function handleQuestionTypeChange
            handleQuestionTypeChange(questionTypeSelect);
  
            if (questionTypeSelect.value === "multi_option") {
              let optionsArray = questionsData.questions[page][question].options;
  
  
  
  
              let optionNum = optionsArray.length; // Find the length of the array
              let num = parseInt(question.replace('question_', '')) //question number 
  
              // fill option 1
              let optionId = `option_${num}_1`;
              let optionElement = document.getElementById(optionId);
              console.log("optionElement", optionId);
              optionElement.nextElementSibling.value = optionsArray[0];
  
              answerContainerId = question.replace('question', 'answerContainer')
              // Call the addNewRadioOption function optionNum-1 times
              for (let i = 2; i <= optionNum; i++) {
                addOptions(num, answerContainerId, i);
                let optionId = `option_${num}_${i}`;
                console.log("optionElement", optionId);
                let optionElement = document.getElementById(optionId);
                optionElement.nextElementSibling.value = optionsArray[i - 1];
                console.log(i)
              }
  
            }
  
  
          }
        }
      });
  
  
      //update 
      console.log("start update ......");
      document.addEventListener("DOMContentLoaded", function () {
        const form = document.getElementById("myForm");
  
        form.addEventListener("submit", function (event) {
          event.preventDefault(); // Prevent the default form submission
          console.log("2nd ......");
          // Get the form data as a JSON object
          const formData = {};
  
          // Add 'title' and 'description' fields to formData
          const titleInput = form.querySelector('input[name="title"]');
          if (titleInput) {
            formData['title'] = titleInput.value;
          }
  
          const descriptionInput = form.querySelector('input[name="description"]');
          if (descriptionInput) {
            formData['description'] = descriptionInput.value;
          }
          console.log("3rd ......");
          const questionElements = form.querySelectorAll('div.input-fields');
  
          questionElements.forEach((questionElement, index) => {
            const questionNum = index + 1;
            console.log("the number", questionNum);
            // Log the question ID
            const questionId = questionElement.id;
            console.log("Question ID:", questionId);
            // Add 'question' and 'question type' fields to formData
            const questionInput = questionElement.querySelector('.row.mb-3 input[id^="question"]');
            const questionName = `question_${questionNum}`;
            formData[questionName] = questionInput ? questionInput.value : null;
  
            const questionTypeSelect = questionElement.querySelector('select');
            const questionTypeName = `ans_type_${questionNum}`;
            formData[questionTypeName] = questionTypeSelect ? questionTypeSelect.value : null;
            console.log("4th ......");
  
            // Include the "Require" status in the form data
            const requireButton = questionElement.querySelector('.btn.Require');
            const requireCheckbox = requireButton.querySelector('.checkbox');
            const requireStatus = requireCheckbox.checked ? 1 : 0;
            const requireName = `require_${questionNum}`;
            formData[requireName] = requireStatus;
  
            // Handle options for multi-option questions
            if (questionTypeSelect.value === 'multi_option') {
              const optionElements = questionElement.querySelectorAll('input[id^="option"]');
              optionElements.forEach((optionElement, optionIndex) => {
                const optionCount = optionIndex + 1;
                const optionName = `option_${questionNum}_${optionCount}`;
                formData[optionName] = optionElement.nextElementSibling.value;
              });
            }
  
            // Move the event listener registration outside of the loop
            // Use a closure to capture the correct values
            requireButton.removeEventListener('click', null); // Remove any existing event listeners
            requireButton.addEventListener('click', function () {
              formData[requireName] = requireCheckbox.checked ? 1 : 0;
              console.log("the number 2", questionNum);
            });
          });
  
  
          console.log(form_id);
  
          fetch('/edit/' + form_id, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
          })
            .then(response => {
              if (response.redirected) {
                window.location.href = response.url;
              }
              return response.json();
            })
            .then(data => {
              // handle your data
            })
            .catch(error => {
              console.error('Error:', error);
             
            });
         
        });
  
      });
  }

