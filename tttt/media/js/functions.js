/*
Author: Martin Korbel
Email: mkorbel@redhat.com
Date: 6.4.2016
*/

function px(num) {return Math.round(num)+'px';}
function log(mess) { console.log(mess); }
function isObject(obj) {return obj !== null && typeof obj === 'object';}
function isNumber(obj) {return obj !== null && !isNaN(parseInt(obj, 10));}
function isArray(myArray) {return Object.prototype.toString.call(myArray) === "[object Array]";}

// Definition of Set
function Set() {
	this.field = [];
	this.has = function(item) {
		return this.field.indexOf(item) != -1;
	};
	this.add = function(item) {
		if (!this.has(item)) {
			this.field.push(item);
		}
	};
	this.del = function(item) {
		var ix = this.field.indexOf(item);
		if (ix != -1) {
			this.field[ix] = null;
		}
	};
	this.getAll = function() {
	    return this.field;
	};
}

// Definition of Hash table
Hash = function(oSource){
  for(sKey in oSource) if(Object.prototype.hasOwnProperty.call(oSource, sKey)) this[sKey] = oSource[sKey];
};
Hash.prototype = Object.create(null);

// Synced getJSON
function getSyncJSON(url, data, success) {
    if (typeof(data) == 'function' && success == null) {
        success = data
        data = {}
    }
    $.ajax({
      dataType: "json",
      url: url,
      data: data,
      success: success,
      async:false});
}


function getAuthor(id) {
    // Return informations about Author of task
    var storage = null;
    if(typeof(Storage) !== "undefined" && window.sessionStorage.authors) {
        storage = jQuery.parseJSON(window.sessionStorage.authors)
    }
    if (storage == null) {
        getSyncJSON("/api/v1/author/", function(json){
             storage = new Hash({});
             for (ix in json.results) {
               storage[json.results[ix].id] = json.results[ix]
             }
             window.sessionStorage.authors = JSON.stringify(storage)
         });
    }
    return storage[id];
}

function getResultIcon(result) {
    // Return icon parametrs for special result code
    if (result == 4 || result == 'fail') {
        return {icon: 'thumbs-down', color: 'danger', title: "Some task(s) faild.", titleTask: "This task faild."};
    } else if (result == 5 || result == 'pass') {
	    return {icon: 'thumbs-up', color: 'success', title: "All is alright.", titleTask: "This task passed."};
    } else if (result == 6 || result == 'new') {
	    return {icon: 'plane', color: 'default', title: "System is preparing to start.", titleTask: "This task does not yet run."};
    } else if (result == 10 || result == 9 || result == 'failinstall' || result == 'panic') {
	    return {icon: 'wrench', color: 'gray', title: "System probably didn't boot.", titleTask: ""};
    } else if (result ==  3 || result == 'warning') {
	    return {icon: 'bullhorn', color: 'warning', title: "Some of tasks warned us.", titleTask: "This task throwed warning."};
    } else if (result == 11 || result == 'waived') {
	    return {icon: 'hand-up', color: 'info', title: "Problems was solved.", titleTask: "Problems was already solved in this task."};
    }
    return {icon: '', color: '', title: "", titleTask: ""};
}

function getCommentIcon(action) {
	if (action == 1 ||  action == 'mark waived') {
		return {icon: "hand-up", title: "This recipe was wavied."};
	} else if (action == 3 || action == "reshedule job") {
		return {icon: "refresh", title: "This job was rescheduled."};
	} else if (action == 2 || action == "return2beaker") {
		return {icon: "save", title: "This job was returned to beaker."};
	} else if (action == 'rescheduled-job-link') {
		return {icon: "refresh", title: "This recipe is new version of previous recipe.."};
	} else {
		return {icon: "info-sign", title: "Comment"};
	}
}
