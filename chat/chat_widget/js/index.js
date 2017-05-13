(function(){
  
  var chat = {
    messageToSend: '',
    init: function() {
      this.cacheDOM();
      this.bindEvents();
      this.render();
    },
    cacheDOM: function() {
      this.$chatHistory = $('.chat-history');
      this.$button = $('button');
      this.$textarea = $('#message-to-send');
      this.$chatHistoryList =  this.$chatHistory.find('ul');
    },
    bindEvents: function() {
      this.$button.on('click', this.addMessage.bind(this));
      this.$textarea.on('keyup', this.addMessageEnter.bind(this));
    },
    render: function() {
      this.scrollToBottom();
      namespace = '/chat';
      var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

      socket.on('connect', function() {
          socket.emit('sendMessage', {data: 'I\'m connected!'});
      });
      socket.on('disconnect', function() {
          $('#log').append('<br>Disconnected');
      });

      socket.on('my response', function(msg) {
          $('#log').append('<br>Received: ' + msg.data);
      });

      // event handler for server sent data
      // the data is displayed in the "Received" section of the page
      // handlers for the different forms in the page
      // these send data to the server in a variety of ways
      $('form#broadcast').submit(function(event) {
          socket.emit('my broadcast event', {data: $('#broadcast_data').val()});
          return false;
      });
      $('form#join').submit(function(event) {
          socket.emit('join', {room: $('#join_room').val()});
          return false;
      });
      $('form#leave').submit(function(event) {
          socket.emit('leave', {room: $('#leave_room').val()});
          return false;
      });
      $('form#send_room').submit(function(event) {
          socket.emit('my room event', {room: $('#room_name').val(), data: $('#room_data').val()});
          return false;
      });
      $('form#close').submit(function(event) {
          socket.emit('close room', {room: $('#close_room').val()});
          return false;
      });
      $('form#disconnect').submit(function(event) {
          socket.emit('disconnect request');
          return false;
      });
      if (this.messageToSend.trim() !== '') {
        var template = Handlebars.compile( $("#message-template").html());
        var context = {
          messageOutput: this.messageToSend,
          time: this.getCurrentTime()
        };
        socket.emit('sendMessage', {data: this.messageToSend.trim()});
        this.$chatHistoryList.append(template(context));
        this.scrollToBottom();
        this.$textarea.val('');

        // responses
        var templateResponse = Handlebars.compile( $("#message-response-template").html());

        var contextResponse = {
          response: 'test',
          time: this.getCurrentTime()
        };
        socket.on('sendMessageResponse', function(msg) {
            contextResponse.response = msg.data;
        });

        setTimeout(function() {
          this.$chatHistoryList.append(templateResponse(contextResponse));
          this.scrollToBottom();
        }.bind(this), 1500);

      }
    },

    addMessage: function() {
      this.messageToSend = this.$textarea.val()
      this.render();         
    },
    addMessageEnter: function(event) {
        // enter was pressed
        if (event.keyCode === 13) {
          this.addMessage();
        }
    },
    scrollToBottom: function() {
       this.$chatHistory.scrollTop(this.$chatHistory[0].scrollHeight);
    },
    getCurrentTime: function() {
      return new Date().toLocaleTimeString().
              replace(/([\d]+:[\d]{2})(:[\d]{2})(.*)/, "$1$3");
    },
    getRandomItem: function(arr) {
      return arr[Math.floor(Math.random()*arr.length)];
    }
    
  };
  
  chat.init();
  
  var searchFilter = {
    options: { valueNames: ['name'] },
    init: function() {
      var userList = new List('people-list', this.options);
      var noItems = $('<li id="no-items-found">No items found</li>');
      
      userList.on('updated', function(list) {
        if (list.matchingItems.length === 0) {
          $(list.list).append(noItems);
        } else {
          noItems.detach();
        }
      });
    }
  };
  
  searchFilter.init();
  
})();
