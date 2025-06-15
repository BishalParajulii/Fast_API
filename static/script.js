document.addEventListener('DOMContentLoaded', function() {
  const topicHeaders = document.querySelectorAll('.topic-header');
  topicHeaders.forEach(header => {
    header.addEventListener('click', (e) => {
      // if click target is the delete button, do nothing here
      if (e.target.closest('.delete-topic-btn')) {
        return; // ignore toggle when delete button clicked
      }
      
      const topicBox = header.parentElement;
      topicBox.classList.toggle('active');
      if (topicBox.classList.contains('active')) {
        document.querySelectorAll('.topic-box').forEach(box => {
          if (box !== topicBox && box.classList.contains('active')) {
            box.classList.remove('active');
          }
        });
      }
    });
  });




  // Delete topic button event listener
document.querySelectorAll(".delete-topic-btn").forEach(button => {
  button.addEventListener("click", function (e) {
    e.preventDefault();
    e.stopPropagation(); 

    const topicId = this.dataset.id;
    if (!topicId) {
      alert("Error: Topic ID not found");
      return;
    }
    console.log("Delete clicked for topic:", topicId);
    deleteTopic(topicId);
  });
});


  const questionHeaders = document.querySelectorAll('.question-header');
  questionHeaders.forEach(header => {
    header.addEventListener('click', () => {
      const questionBox = header.parentElement;
      questionBox.classList.toggle('active');
    });
  });

  if (topicHeaders.length > 0) {
    topicHeaders[0].click();
  }
});

async function addTopic() {
  const topicName = document.getElementById('topicName').value;
  if (!topicName) return alert('Please enter a topic name');

  const response = await fetch('/topics/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: topicName })
  });
  if (response.ok) {
    location.reload();
  } else {
    alert('Error adding topic');
  }
}

async function addQuestion() {
  const topicId = document.getElementById('topicSelect').value;
  const text = document.getElementById('questionText').value;
  const answer = document.getElementById('questionAnswer').value;

  if (!topicId || !text || !answer) return alert('Please fill all fields');

  const response = await fetch(`/topics/${topicId}/questions/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, answer })
  });
  if (response.ok) {
    location.reload();
  } else {
    alert('Error adding question');
  }
}

async function deleteQuestion(questionId) {
  if (confirm('Are you sure you want to delete this question?')) {
    const response = await fetch(`/questions/${questionId}`, {
      method: 'DELETE'
    });
    if (response.ok) {
      location.reload();
    } else {
      alert('Error deleting question');
    }
  }
}

async function deleteTopic(topicId) {
  if (!confirm("Are you sure you want to delete this topic and all its questions?")) return;

  try {
    const response = await fetch(`/delete-topic/${topicId}`, {
      method: "DELETE"
    });
    if (response.ok) {
      console.log(`Topic ${topicId} deleted successfully`);
      location.reload(true); // Force reload without cache
    } else {
      const errorData = await response.json();
      console.error("Failed to delete topic:", errorData);
      alert(`Failed to delete topic: ${errorData.detail || 'Unknown error'}`);
    }
  } catch (error) {
    console.error("Error deleting topic:", error);
    alert(`Error deleting topic: ${error.message}`);
  }
}