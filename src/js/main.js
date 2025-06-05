(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();

    // Initiate the wowjs
    new WOW().init();

    // Sticky Navbar
    $(window).scroll(function () {
        $('.sticky-top').css('top', $(this).scrollTop() > 300 ? '0px' : '-100px');
    });

    // Back to top button
    $(window).scroll(function () {
        $(this).scrollTop() > 300 ? $('.back-to-top').fadeIn('slow') : $('.back-to-top').fadeOut('slow');
    });

    $('.back-to-top').click(function () {
        $('html, body').animate({ scrollTop: 0 }, 1500, 'easeInOutExpo');
        return false;
    });

    // Header carousel
    $(".header-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        items: 1,
        dots: true,
        loop: true,
        nav: true,
        navText: [
            '<i class="bi bi-chevron-left"></i>',
            '<i class="bi bi-chevron-right"></i>'
        ]
    });

    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        center: true,
        margin: 24,
        dots: true,
        loop: true,
        nav: false,
        responsive: {
            0: { items: 1 },
            768: { items: 2 },
            992: { items: 3 }
        }
    });

    // Job Search
    $('#searchBtn').click(function () {
        const keywords = $('#keywordInput').val().trim();

        if (!keywords) {
            $('#jobResults').html('<p>Please enter a keyword.</p>');
            return;
        }

        $('#jobResults').html('<p>Loading...</p>');

        fetch('http://127.0.0.1:5000/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ keywords: keywords })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.length) {
                $('#jobResults').html('<p>No jobs found.</p>');
                return;
            }

            let html = '';
            data.forEach(job => {
                html += `
                    <div class="job card p-3 mb-3 shadow-sm">
                        <h5>${job.title}</h5>
                        <p class="mb-1"><strong>${job.company}</strong> - ${job.location}</p>
                        <a class="btn btn-primary btn-sm" href="${job.link}" target="_blank">View Job</a>
                    </div>
                `;
            });
            $('#jobResults').html(html);
        })
        .catch(error => {
            console.error('Error fetching jobs:', error);
            $('#jobResults').html('<p>Error loading jobs. Try again later.</p>');
        });
    });

})(jQuery);
