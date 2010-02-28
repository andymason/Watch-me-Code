/*
    Title:      Watch Me Code JavaScript
    
    File:       wmc.js
    Source:     http://watchmecode.appspot.com/
    
    Author:     Andrew Mason
    Contact:    andrew @ coderonfire dot com
    Website:    http://coderonfire.com/
    
    Licence:
    
    This file is part of Watch Me Code.

    Watch Me Code is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Watch Me Code is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Watch Me Code. If not, see<http://www.gnu.org/licenses/>.
        

*/

var wmc = (function() {  
    return {
        observer: function(id) {
            // Capture DOM element and value
            var textarea = document.getElementById('code');
            
            setInterval(wmc.getCode, 2000, id, textarea);
            
        },
        
        editor: function(id) {
            // Capture DOM element and value
            var textarea = document.getElementById('code');
            
            
            // Set on keypress event handler
            if (textarea.addEventListener) {
                textarea.addEventListener('keyup', function() {wmc.sendCode(id, this)}, false)
            }
        },
        
        sendCode: function (id, elm) {
            // Get value of textarea
            var code = elm.value;
            // Send to DB via AJAX
            $.post('/save', { key: id, content: code } );
        },
        
        getCode: function (id, elm) {
            $.get('/get', { key: id }, function(data) {
                elm.value = (data.content);
            });
        }
    }

})();
