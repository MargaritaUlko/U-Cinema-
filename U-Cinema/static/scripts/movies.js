document.addEventListener("DOMContentLoaded", function() {
    // Получаем данные о фильмах с помощью AJAX запроса
    fetch('/your-movies-endpoint/')  // Замените '/your-movies-endpoint/' на URL вашего эндпоинта, откуда вы получаете данные о фильмах
        .then(response => response.json())
        .then(data => {
            // Получаем контейнер, в который будем вставлять информацию о фильмах
            const movieContainer = document.querySelector('.movie-grid');

            // Проходимся по данным о каждом фильме
            data.forEach(movie => {
                // Создаем элементы для отображения информации о фильме
                const movieItem = document.createElement('div');
                movieItem.classList.add('movie-item');

                const title = document.createElement('h2');
                title.textContent = movie.title;

                const poster = document.createElement('img');
                poster.src = movie.poster;
                poster.alt = movie.title + ' Poster';

                const detailsLink = document.createElement('a');
                detailsLink.href = movie.details_url; // Замените 'movie.details_url' на поле, содержащее URL деталей фильма в вашем JSON объекте
                detailsLink.textContent = 'Подробнее';

                // Вставляем созданные элементы в контейнер
                movieItem.appendChild(title);
                movieItem.appendChild(poster);
                movieItem.appendChild(detailsLink);

                movieContainer.appendChild(movieItem);
            });
        })
        .catch(error => console.log('Error fetching movies:', error));
});
