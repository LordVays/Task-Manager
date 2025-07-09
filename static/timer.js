document.addEventListener('DOMContentLoaded', () => {

    const timers = document.querySelectorAll('.timer');

    function createBurstAnimation(x, y) {
        new mojs.Burst({
            radius: { 0: 100 },
            angle: 45,
            count: 10,
            children: {
                shape: 'circle',
                radius: 10,
                fill: ['#FF5722', '#FFC107', '#8BC34A'],
                duration: 2000
            },
            x: x,
            y: y,
            opacity: { 1: 0 },
        }).play();
    };

    function updateTimers() {
        timers.forEach(timer => {
            const deadline = new Date(timer.getAttribute('data-deadline'));
            const now = new Date();
            const remainingTime = deadline - now;

            if (remainingTime <= 0) {
                timer.textContent = 'Дедлайн прошёл';
                timer.classList.add('expired');
            } else {
                const days = Math.floor(remainingTime / (1000 * 60 * 60 * 24));
                const hours = Math.floor((remainingTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((remainingTime % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((remainingTime % (1000 * 60)) / 1000);
                timer.textContent = `${days}д ${hours}ч ${minutes}м ${seconds}с`;
            }
        });
    }

    if (timers.length > 0) {
        updateTimers();
        setInterval(updateTimers, 1000);
    }

    const taskList = document.querySelector('.task-list');

    if (taskList) {
        taskList.addEventListener('click', (event) => {
            const taskContentSpan = event.target.closest('.task-content');
            if (taskContentSpan) {
                if (taskContentSpan.querySelector('.inline-edit-input')) return;

                const taskId = taskContentSpan.dataset.taskId;
                const originalText = taskContentSpan.textContent;

                const input = document.createElement('input');
                input.type = 'text';
                input.value = originalText;
                input.className = 'inline-edit-input';

                taskContentSpan.textContent = '';
                taskContentSpan.appendChild(input);
                input.focus();

                const saveChanges = () => {
                    const newText = input.value.trim();
                    if (newText === originalText || !newText) {
                        taskContentSpan.innerHTML = originalText;
                        return;
                    }

                    fetch(`/api/update_content/${taskId}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ content: newText })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            taskContentSpan.innerHTML = data.new_content;
                        } else {
                            alert('Ошибка обновления: ' + data.message);
                            taskContentSpan.innerHTML = originalText;
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Произошла сетевая ошибка.');
                        taskContentSpan.innerHTML = originalText;
                    });
                };

                input.addEventListener('blur', saveChanges);
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') input.blur();
                    else if (e.key === 'Escape') taskContentSpan.innerHTML = originalText;
                });
            }
        });
    }
});