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

// Definition remove item from Aarray

Object.defineProperty(Array.prototype, "removeItem", {
	enumerable: false,
	value: function(from, to) {
	  var rest = this.slice((to || from) + 1 || this.length);
	  console.log(this);
	  this.length = from < 0 ? this.length + from : from;
	  return this.push.apply(this, rest);
}});

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

function getResultRecipeIcon(recipe) {
	// Return icon parametrs for special result code
	var res = {icon: '', color: '', title: "", status:""};
	if (recipe.result == 5) {
		res = {status: "pass", icon: 'thumbs-up', color: 'green', title: "All is alright."};
	} else if (recipe.result == 3) {
		res = {status: 'warn', icon: 'bullhorn', color: 'orange', title: "Some of tasks warned us."};
	} else if (recipe.result == 10 || recipe.result == 9) {
		res = {status:"failinstall", icon: 'wrench', color: 'gray', title: "Recipe failed on installation."};
	} else if (recipe.result == 4) {
		res = {status: "fail", icon: 'thumbs-down', color: 'red', title: "Some task(s) faild."};
	}
	if (recipe.statusbyuser == 11) {
		res.status = "waived";
		res.color = '#5bc0de';
		res.title = "Problems was solved.";
	}
    return res;
}

function getTaskResultIcon(task, recipe) {
    // Return icon parametrs for special result code
	var res = {icon: '', color: '', title: "", status:""}
	if (task.status == 1) {
		res = {status: 'run', icon: 'play', color: '#286090', title: "This task is running now."};
	} else if (task.status == 3) {
		res = {status: 'scheduled', icon: 'hourglass', color: 'default', title: "This task does not yet run."};
	} else if (task.status == 5) {
		res = {status: 'aborted', icon: 'remove-circle', color: '#999', title: "This task was skipped. The recipe was aborted."};
	} else if (task.result == 5) {
		res = {status: "pass", icon: 'thumbs-up', color: 'green', title: "This task passed."};
	} else if (task.result == 3) {
		res = {status: 'warn', icon: 'bullhorn', color: 'orange', title: "This task throwed warning."};
	} else if (task.result == 10 || task.result == 9) {
		res = {status:"failinstall", icon: 'wrench', color: 'gray', title: "This task failinstall or panic"};
	} else if (task.result == 4) {
		res = {status: "fail", icon: 'thumbs-down', color: 'red', title:"This task faild."};
	}
	if (task.result != 5 &&
		(task.statusbyuser == 11 || (recipe != null && recipe.statusbyuser == 11))) {
		res.status = "waived";
		res.color = '#5bc0de';
		res.title = "Problems was solved.";
		res.titleTask = "Problems was already solved in this task.";
	}
    return res;
}

function getTaskStatusIcon(task) {
	if (task.status == 1) {
		res = {status: 'run', icon: 'play', color: '#286090', title: "This task is running now."};
	} else if (task.status == 3) {
		res = {status: 'scheduled', icon: 'hourglass', color: 'default', title: "This task does not yet run."};
	} else if (task.status == 5) {
		res = {status: 'aborted', icon: 'remove-circle', color: '#999', title: "This task as skipped."};
	} else {
		res = {status: 'completed', icon: 'ok-circle', color: 'green', title: "This task is done."};
	}
	return res;
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

function openModalWindow(content, title) {
	var html = "";
	html += '<div class="modal fade" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">'+
  		    '  <div class="modal-dialog modal-lg" role="document">'+
            '   <div class="modal-content">'+
            '     <div class="modal-header">'+
            '      <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+
            '      <h4 class="modal-title" id="myModalLabel">'+title+'</h4>'+
            '    </div>'+
            '    <div class="modal-body">'+
        	content+
            '    </div>'+
      		'    <div class="modal-footer">'+
			'      <span class="info">Press Esc to close.</span>'+
        	'      <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>'+
            '    </div>'+
    	    '   </div>'+
            '  </div>'+
            '</div>';
	$('body').append(html);
	$('#myModal').modal('show').on('hidden.bs.modal', function (e) {
		$(this).remove();
	});
}
