function acceptInvitation(notificationId) {
    fetch(`/accept_invitation/${notificationId}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (response.ok) {
            console.log(data.message);
            // Optionally, update the UI to reflect the accepted invitation
        } else {
            console.error(data.error);
            // Handle the error, e.g., display an error message to the user
        }
    })
    .catch(error => console.error('Error:', error));
}

// Function to handle declining an invitation
function declineInvitation(notificationId) {
    fetch(`/decline_invitation/${notificationId}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (response.ok) {
            console.log(data.message);
            // Optionally, update the UI to reflect the declined invitation
        } else {
            console.error(data.error);
            // Handle the error, e.g., display an error message to the user
        }
    })
    .catch(error => console.error('Error:', error));
}

// Example usage: Assuming you have buttons with IDs 'acceptButton' and 'declineButton'
document.getElementById('acceptButton').addEventListener('click', () => {
    const notificationId = 7; // Replace with the actual notification ID
    acceptInvitation(notificationId);
});

document.getElementById('declineButton').addEventListener('click', () => {
    const notificationId = 7; // Replace with the actual notification ID
    declineInvitation(notificationId);
});