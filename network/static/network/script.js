document.addEventListener('DOMContentLoaded', function() {

    document.querySelectorAll('.like-btn').forEach((item) => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
        
            let status = this.innerHTML === "Like" ? "Like" : "Unlike";

            fetch('/likes', {
                method: 'POST',
                body: JSON.stringify({
                    userId: this.getAttribute('data-userId'),
                    postId: this.getAttribute('data-postId'),
                    status: status
                })
            })
            .then(response => response.json())
            .then(result => {
                item.parentNode.querySelector(".like-count").innerHTML = result.count;
                // This needs to be fixed to show the correct word
                this.innerHTML = "Unlike";
            });
        });
    });

});