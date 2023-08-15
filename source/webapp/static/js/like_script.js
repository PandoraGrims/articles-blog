function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

const csrftoken = getCookie('csrftoken');


document.addEventListener('DOMContentLoaded', () => {
    const likeButtons = document.querySelectorAll('.like-button');

    likeButtons.forEach(button => {
        button.addEventListener('click', async () => {
            let type = button.getAttribute('data-type');
            let id = button.getAttribute('data-id');
            let response = await toggleLike(type, id);

            if (response) {
                let likeCount = response.count;
                let liked = response.liked;

                let countElement = button.nextElementSibling;
                countElement.textContent = likeCount;
                button.textContent = liked ? 'Анлайк' : 'Лайк';
            }
        });
    });
});

async function toggleLike(type, id) {
    try {
        let response = await fetch(`/${type}/${id}/toggle_like/`, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': csrftoken
            }
        });

        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error(error);
    }
}


