function acceptInvitation(notificationId) {
    fetch(`/accept_invitation/${notificationId}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (response.ok) {
            console.log(data.message);
        } else {
            console.error(data.error);
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
        } else {
            console.error(data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}
