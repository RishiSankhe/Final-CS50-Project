document.addEventListener('DOMContentLoaded', () => {
    // Create a preloader element and append it to the body
    const preloader = document.createElement('div');
    preloader.className = 'preloader';
    preloader.innerHTML = '<span class="preloader-text">Loading...</span>';
    document.body.appendChild(preloader);

    // Get all images on the page and track how many are loaded
    const images = Array.from(document.images);
    let loadedImages = 0;

    // Function to check if all images have been loaded
    function checkAllImagesLoaded() {
        loadedImages++;
        // If all images are loaded, make the body visible and remove the preloader
        if (loadedImages === images.length) {
            document.body.style.visibility = 'visible';
            document.body.style.overflow = 'auto';
            preloader.remove();
        }
    }

    // Add event listeners to each image to detect when it loads or fails to load
    images.forEach((img) => {
        if (img.complete) {
            checkAllImagesLoaded(); // If already loaded, update the counter
        } else {
            img.addEventListener('load', checkAllImagesLoaded); // On successful load
            img.addEventListener('error', checkAllImagesLoaded); // On load error
        }
    });

    // If there are no images on the page, immediately remove the preloader
    if (images.length === 0) {
        document.body.style.visibility = 'visible';
        document.body.style.overflow = 'auto';
        preloader.remove();
    }
});
