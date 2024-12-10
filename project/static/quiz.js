document.addEventListener("DOMContentLoaded", () => {
    // Get references to important DOM elements
    const quizForm = document.getElementById("quizForm");
    const slides = document.querySelectorAll(".quiz-slide");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const submitBtn = document.getElementById("submitBtn");
    const progressBar = document.querySelector(".progress-bar");
    let currentSlide = 0; // Track the current quiz slide

    // Show the slide at the given index and update UI elements
    function showSlide(index) {
        slides[currentSlide].classList.remove("active");
        slides[index].classList.add("active");
        currentSlide = index;
        updateButtons();
        updateProgressBar();
    }

    // Update the visibility of navigation and submit buttons
    function updateButtons() {
        prevBtn.disabled = currentSlide === 0; // Disable "Previous" button on the first slide
        nextBtn.classList.toggle("d-none", currentSlide === slides.length - 1); // Hide "Next" button on the last slide
        submitBtn.classList.toggle("d-none", currentSlide !== slides.length - 1); // Show "Submit" button only on the last slide
    }

    // Update the progress bar based on the current slide
    function updateProgressBar() {
        const progress = ((currentSlide + 1) / slides.length) * 100;
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute("aria-valuenow", progress);
    }

    // Navigate to the previous slide
    prevBtn.addEventListener("click", (e) => {
        e.preventDefault();
        if (currentSlide > 0) showSlide(currentSlide - 1);
    });

    // Navigate to the next slide
    nextBtn.addEventListener("click", (e) => {
        e.preventDefault();
        if (currentSlide < slides.length - 1) {
            showSlide(currentSlide + 1);
        }
    });

    // Submit the form when the "Submit" button is clicked
    submitBtn.addEventListener("click", () => {
        quizForm.submit();
    });

    // Automatically navigate to the next slide when an answer is selected
    slides.forEach((slide) => {
        const inputs = slide.querySelectorAll("input[type='radio']");
        inputs.forEach((input) => {
            input.addEventListener("change", () => {
                if (currentSlide < slides.length - 1) showSlide(currentSlide + 1);
            });
        });
    });

    // Initialize the quiz by showing the first slide
    showSlide(0);
});
