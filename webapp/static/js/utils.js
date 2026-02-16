function datetime() {
    const now = new Date();

    // Adjust for user's local time (optional):
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    return now.toISOString().slice(0, 16); // YYYY-MM-DDTHH:mm
}

function changeImage() {
    // const topic = 'nature';
    const width = window.screen.width;
    const height = window.screen.height;
    // Replace with your desired image source (consider copyright!)
    const imageUrl = `https://picsum.photos/${width}/${height}`;

    document.body.style.backgroundImage = `url(${imageUrl})`;
}

// Change image every 5 seconds (adjust as needed)
// setInterval(changeImage, 5000);

// Initial image load
// changeImage();