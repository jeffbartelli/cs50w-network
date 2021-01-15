document.addEventListener('DOMContentLoaded', function() {

    document.querySelectorAll('.like-btn').forEach((item) => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('trigger');
        
            fetch('/likes', {
                method: 'POST',
                body: JSON.stringify({
                    postId: this.getAttribute('data-postId')
                })
            })
            .then(response => response.json())
            .then(result => {
                item.parentNode.querySelector(".like-count").innerHTML = result.count;
                this.innerHTML = result.liker;
            });
        });
    });

});