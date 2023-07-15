setTimeout(function () {
     $('#message').fadeOut('slow')
}, 4000)
var words = [
 'Extensive Job Opportunities',
 'Time and Effort Savings',
 'Enhanced Visibility',
 'Convenient Application Management',
 'Career Guidance and Resources',
 'Discover the best job opportunities tailored for you.'
],
     part,
     i = 0,
     offset = 0,
     len = words.length,
     forwards = true,
     skip_count = 0,
     skip_delay = 25,
     speed = 110;
var wordflick = function () {
     setInterval(function () {
          if (forwards) {
               if (offset >= words[i].length) {
                    ++skip_count;
                    if (skip_count == skip_delay) {
                         forwards = false;
                         skip_count = 0;
                    }
               }
          } else {
               if (offset == 0) {
                    forwards = true;
                    i++;
                    offset = 0;
                    if (i >= len) {
                         i = 0;
                    }
               }
          }
          part = words[i].substr(0, offset);
          if (skip_count == 0) {
               if (forwards) {
                    offset++;
               } else {
                    offset--;
               }
          }
          $('.word').text(part);
     }, speed);
};

$(document).ready(function () {
     wordflick();
});



// Function to update the notifications count
function updateNotificationsCount() {
     fetch('/notifications-count/')
          .then(response => response.json())
          .then(data => {
               // Update the notifications count element with the received data
               document.getElementById('notifications-count').textContent = data.count;
          })
          .catch(error => console.log('Error:', error));
}

// Update notifications count initially

// Schedule periodic updates every 10 seconds (adjust as needed)
setInterval(updateNotificationsCount, 2000);
function updateNotificationsCountOther(id) {
     fetch('/notifications-count-other/' + id + '/')
          .then(response => response.json())
          .then(data => {
               // Update the notifications count element with the received data
               document.getElementById('notifications-count').textContent = data.count;
          })
          .catch(error => console.log('Error:', error));
}

// Update notifications count initially
const url = window.location.href;
const keyword = 'view-application';

if (url.indexOf(keyword)  !== -1) {
     const parts = url.split('/');
     const number = parts[parts.length - 2];
     // console.log(number);
     setInterval(updateNotificationsCountOther(number), 2000);
}
else{
updateNotificationsCount();

}

// Schedule periodic updates every 10 seconds (adjust as needed)
// Fetch every 5 seconds (adjust as needed)
