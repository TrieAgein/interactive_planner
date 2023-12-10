document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var timezoneSelectorEl = document.getElementById('timezone-selector');
  
    // Timezones for selector
    var timezones = [
      { value: 'America/New_York', text: 'New York' },
      { value: 'America/Los_Angeles', text: 'Los Angeles' },
      { value: 'Asia/Karachi', text: 'Karachi' },
      { value: 'Asia/Tokyo', text: 'Tokyo' },
      { value: 'Europe/Helsinki', text: 'Helsinki' },
    ];
  
    // Populate selector with options
    timezones.forEach(function(tz) {
      var optionEl = document.createElement('option');
      optionEl.value = tz.value;
      optionEl.innerText = tz.text;
      timezoneSelectorEl.appendChild(optionEl);
    });
  
    var calendar = new FullCalendar.Calendar(calendarEl, {
      timeZone: 'America/New_York',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek',
      },
      events: [
        {
          title: 'Kicking a Dog',
          start: '2023-12-09T10:00:00',
          end: '2023-12-09T12:00:00',
        },
      ],
    });
  
    calendar.render();
  
    // When selector changes, update timezone
    timezoneSelectorEl.addEventListener('change', function() {
      calendar.setOption('timeZone', this.value);
  
      // Rerender after timezone change
      calendar.render();
    });
  });