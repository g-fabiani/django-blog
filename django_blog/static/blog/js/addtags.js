document.addEventListener('DOMContentLoaded', function () {
    const counter = document.querySelector('#tag-count');
    const availableTagsString = document.querySelector('#available-tags').textContent;
    const postTagsString = document.querySelector('#post-tags').textContent;
    const availableTags = availableTagsString ? JSON.parse(availableTagsString).map(x => x.name) : [];

    let selectedTags = postTagsString ? JSON.parse(postTagsString).map(x => x.name) : [];
    let suggestedTags = availableTags.slice();

    function updateSuggestedTags() {
        suggestedTags = availableTags.filter(x => !selectedTags.includes(x));
    }

    function displayDataList() {
        const list = document.querySelector('#tag-datalist');
        // Remove all elements from datalist
        while (list.firstChild) {
            list.removeChild(list.firstChild);
        }
        // Populate datalist
        suggestedTags.forEach(tag => {
            const option = document.createElement('option');
            option.value = tag;
            list.append(option);
        })
    }

    function displayTagCount() {
        //  Update tag count to the number of selected tags
        counter.innerHTML = selectedTags.length;
    }

    function displayTagList() {
        // Remove all elements from list
        const list = document.querySelector('#tag-list');
        while (list.firstChild) {
            list.removeChild(list.firstChild);
        }

        // Populate tag list
        selectedTags.forEach(tag => {
            const listItem = document.createElement('li');
            listItem.innerHTML = '<i class="bi bi-tag-fill" aria-hidden="true"></i> ' + tag;
            listItem.classList.add('tag')

            // Clicking a tag removes it from the selected list
            listItem.addEventListener('click', event => {
                listItem.remove();
                selectedTags = selectedTags.filter(item => item != tag)
                console.log(selectedTags);
                updateSuggestedTags();
                displayDataList();
                displayTagCount();
            })
            list.append(listItem);
        })
    }


    updateSuggestedTags();
    displayTagCount();
    displayDataList();
    displayTagList();

    document.querySelector('#tag').onkeydown = (event) => {
        // A tag is added when making a carriage return attempting to add a comma
        if (['Enter', ','].includes(event.key)) {
            // Remove trailing spaces from tag
            const tag = document.querySelector('#tag').value.trim();

            // Add the tag only if not already present
            if (tag && !selectedTags.includes(tag)) {
                selectedTags.push(tag);
                console.log(selectedTags);

                updateSuggestedTags();
                displayDataList();
                displayTagList();
                displayTagCount();
            }

            // Clear the input field
            document.querySelector('#tag').value = '';


            // Prevent from adding the comma
            return false;
        }

    }

    document.querySelector('#post-form').onsubmit = () => {
        selectedTags.forEach(tag => {
            const hiddenInput = document.createElement('input');
            hiddenInput.setAttribute('type', 'hidden');
            hiddenInput.setAttribute('name', 'tags');
            hiddenInput.value = tag;
            document.querySelector('#post-form').append(hiddenInput);
        });
    };

})