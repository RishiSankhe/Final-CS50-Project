# Design Document

In developing our project, we applied a wide range of concepts and technologies learned throughout the course. Our goal was to create an interactive, user-friendly, and aesthetically pleasing web application. We leveraged a combination of HTML, CSS, JavaScript, SQL, Jinja, and Python, which were integrated seamlessly using Flask to build a cohesive and dynamic user experience.

## Key Technical and Design Decisions

### 1. **Login and Registration**
To keep the `app.py` file clean and maintainable, we separated the core functionality into a `helpers.py` module, which houses key functions for user authentication. This modular approach also allowed us to handle edge cases effectively. We implemented custom error handling through an apology function, which ensures that users are presented with informative error messages when necessary.

### 2. **Landing and Home Pages**
For the landing page, we focused on creating an engaging and professional UI. We incorporated various CSS animations and effects to enhance user interactivity. Upon accessing the page, users are prompted to either log in or register; if they do not, an error message is triggered to guide them. Additionally, we utilized an API to integrate an interactive 3D globe as the background. This globe provides users with the ability to zoom in, zoom out, and navigate around, creating a dynamic and visually appealing introduction to the site.

### 3. **Bucket List Feature**
The Bucket list functionality was implemented using SQL, ensuring that each user has a personalized list of places they can add and remove at will. Each wishlist item is linked to a summary page for further exploration. By linking each place to the relevant explore page, users can quickly access more detailed information about their selected destinations.

### 4. **Personalized Quiz Algorithm**
We designed a custom algorithm for the quiz feature, incorporating our own experiences with the various places featured on the site. The core of the algorithm resides in `helpers.py`, where it calculates results based on a range of inputs, including the current date, time, and the weather conditions of each location. This decision-tree-based algorithm adapts to individual preferences, providing personalized recommendations.

### 5. **City-Specific Web Pages**
For each city’s dedicated website, we created 5 pages to better reflect the unique characteristics of each location. Despite the variations in content, we maintained a consistent user navigation experience by creating a universal `navbar.html`, which was integrated into each page using Jinja templating. Additionally, we ensured a universal style for the separate pages in the `city_style` folder in the `static` directory.

### 6. **Explore Pages and Image Integration**
We wanted the explore pages to provide a more immersive experience, so we incorporated images relevant to each location. To ensure that the user interface remained responsive and clean, we implemented a loading screen that only disappears once all images and content have been fully loaded. This was done using a separate script called `loader.js`.

### 7. **Bootstrap and Custom CSS**
To streamline the design process and ensure a polished, professional look, we utilized various Bootstrap components such as carousels and accordions. These elements enhance the functionality of the site, offering an intuitive layout. Additionally, we applied custom CSS to further refine the visual elements and maintain consistency across the platform.

### 8. **API Integrations**
We integrated several key APIs to enhance the functionality of our site:

- **Weather API (OpenWeatherMap)**: To provide real-time weather information for each location, ensuring that the user’s experience is contextually relevant.
- **Spotify API**: To allow users to embed and listen to a song associated with each destination, adding an audio dimension to their journey.
- **Mapbox API**: To embed interactive maps, enabling users to explore different locations visually and drop pins for points of interest.
- **The News API**: To display current news, filtered by keywords and categories, ensuring users stay informed about the latest events related to their destinations.
