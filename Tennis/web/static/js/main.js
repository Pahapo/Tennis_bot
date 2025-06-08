// web/static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('JS loaded');
    
    // Можно добавить обработчики событий и другую логику
    document.querySelectorAll('.tournaments-table tr').forEach(row => {
        row.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    });
});