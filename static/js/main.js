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