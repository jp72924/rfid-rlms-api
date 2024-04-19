function datetime() {
    const now = new Date();

    // Adjust for user's local time (optional):
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    return now.toISOString().slice(0, 16); // YYYY-MM-DDTHH:mm
}