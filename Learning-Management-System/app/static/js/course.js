ClassicEditor
    .create(document.querySelector('#course-editor'), {
        toolbar: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 'undo', 'redo'],
        placeholder: 'Tell your students what this course is about...'
    })
    .catch(error => {
        console.error(error);
    });