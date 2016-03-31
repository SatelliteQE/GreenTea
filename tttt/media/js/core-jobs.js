/* Core-jobs.js */

var preLoadTabUID = null;
function initPage() {
	// Set default disable buttons
	$('.action-panel button', detailPanel.elm).prop('disabled', $('.recipe-list', detailPanel.elm).children('div').length == 0);

	// Add autocomplete into name field
	$('#id_username', detailPanel.elm).autocomplete({
	    minLength: 0,
	    source: function( request, response ) {
	       $.getJSON("/api/owners?key=" + request.term, function(json){
	        var res = [];
	        for (ix in json.owners) {
	          res[res.length] = json.owners[ix].name;
	        }
	        response(res);
	      });
	    },
	});

	// Save selected recipes into one hidden field.
	$('.action-panel form', detailPanel.elm).submit(function(){
		var res = [];
		var recipes = $('.recipe-list > div', detailPanel.elm);
        for (var ix=0, max=recipes.length; ix < max; ix++) {
          res[res.length] = $(recipes[ix]).text().trim();
		};
		$('input[name="uids"]', detailPanel.elm).val(res.join(' '));
	});

    // Add function to get Informations about tasks
    detailPanel.func.getInfoAboutTask = getResultIcon;
    detailPanel.func.deleteTask = function(link) {
		var name = link.text().trim();
		$('.dashboard tbody td[id="'+name+'"]').removeClass('selected');
    };
    detailPanel.func.hoverTab = function(event, action) {
        var uid = $(event.target).attr('data-name');
        var td = $('.dashboard tbody td[id="'+uid+'"]');
        if (action == 'IN') {
             td.addClass('light');
        } else {
            td.removeClass('light');
        }

    };

    var uid = window.location.hash.substring(1).replace(/R:/,'');
    if (isNumber(uid)) {
		preLoadTabUID = uid;
		previewRecipe(uid);
    }
}

function getResultIcon(result) {
	if (result == 'fail') {
	   return {icon: 'thumbs-down', color: 'danger', title: "Some task(s) faild.", titleTask: "This task faild."};
    } else if (result == 'pass') {
	   return {icon: 'thumbs-up', color: 'success', title: "All is alright.", titleTask: "This task passed."};
    } else if (result == 'new') {                	
	   return {icon: 'plane', color: 'default', title: "System is preparing to start.", titleTask: "This task does not yet run."};
    } else if (result == 'failinstall' || result == 'panic' ) {
	   return {icon: 'wrench', color: 'gray', title: "System probably didn't boot.", titleTask: ""};
    } else if (result == 'warning' || result == 'warn') {
	   return {icon: 'bullhorn', color: 'warning', title: "Some of tasks warned us.", titleTask: "This task throwed warning."};
    } else if (result == 'waived') {
	   return {icon: 'hand-up', color: 'info', title: "Problems was solved.", titleTask: "Problems was already solved in this task."};
    }
    return null;
}

function formateTaskList(tasks) {
	message = "";
	$.each(tasks, function(i, task){
    	var result = "";
    	var tres = task.result;
    	if (task.statusbyuser == 'waived') tres='waived'; 
    	var icon = getResultIcon(tres);
    	if (icon) {
    		result = '<span class="glyphicon glyphicon-'+icon.icon+'" title="'+icon.titleTask+'"></span>';
    	}    	    
        message += '<tr>';
        message += '<td>'+result+'</td>';
        message += '<td>'+task.test.name+'&nbsp&nbsp'+
                   '<a class="glyphicon glyphicon-link" href="tests.html?search='+encodeURI(task.test.name)+'#'+task.uid+'" title="Test detail"></a>&nbsp;&nbsp;'+
                   '<a href="https://' + BEAKER_SERVER + '/recipes/'+task.recipe+'#task'+task.uid+'" class="glyphicon glyphicon-briefcase" title="Link to Beaker"></a>'+
        		   '</td><td>';
        if (task.test.owner) {
            message += '<a href="mailto:'+task.test.owner.email+'">'+task.test.owner.name+"</a>";
        } else {
        	message += '&nbsp;';
        }
        message += '</td></tr>';
        if(task.comments.length > 0) {
			  for(ix in task.comments) {
			  	 message += '<tr>';
			  	 message += '<td>&nbsp</td>';
			  	 message += '<td><span class="glyphicon glyphicon-info-sign"></span>&nbsp;&nbsp;'+
			  	            task.comments[ix].created_date+'&nbsp;&nbsp;'+
			  	            task.comments[ix].content+'</td>';
			  	 message += '<td>'+task.comments[ix].username+'</td>';
			  	 message += '</tr>';
			  }       		
        }        	
    });
    return message;
}

var loadingTasks = false;

function loadTasks(uid, from, filter) {		
	var tabC = $("div[data-name='R:"+uid+"']", detailPanel.elm);
	var maxTasks = parseInt($(".tasks-list table", tabC).attr('data-counttasks'));
	var numRows = $(".tasks-list tbody tr", tabC).length;
	//console.log(loadingTasks, " && ", from, " > 0 && ", numRows," >= ", maxTasks);
	if (loadingTasks || (from > 0 && numRows >= maxTasks)) return;
	loadingTasks = true;
	$.getJSON('/api/recipe-tasks?from='+from+'&filter='+filter+'&recipe='+uid, function(data){		
		var tabC = $("div[data-name='R:"+uid+"']", detailPanel.elm);
		if(from == 0) {
			$(".tasks-list tbody", tabC).html(formateTaskList(data.tasks));
			$(".tasksLabel", tabC).html('Tasks ('+data.task_len+')');
			$(".tasks-list table", tabC).attr('data-counttasks', data.task_len);
			$(".scrolling", tabC).scrollTop();
		} else {
			$(".tasks-list tbody", tabC).append(formateTaskList(data.tasks));
		}				
		loadingTasks = false;
	});		
}

var lastUID = null;
var openUIDs = new Set();

function previewRecipe(uid) {
	if (!isNumber(uid)) {
	    // Preview
		uid = $(this).attr("id");
    } else {
        // Persistent
        if(detailPanel.isHidden()) {
            detailPanel.switchDisplay();
        }
        openUIDs.add(uid);
    }
    lastUID = uid.replace(/R:/,'')
    if(uid) {
        $.getJSON("/api/v1/recipe/" + lastUID + "?format=json", function(data) {
		var loadToBackend = openUIDs.has(data.recipe.uid);
		if (lastUID != data.recipe.uid && !loadToBackend) { return; }
		if (loadToBackend) {
			openUIDs.del(data.recipe.uid);
			$('.dashboard tbody td[id="R:'+data.recipe.uid+'"]').addClass('selected');
		} else {
			$("td.hover").removeClass('hover');
			$('.dashboard tbody td[id="R:'+data.recipe.uid+'"]').addClass('hover');
		}
            var message = "";
            var recipeWhiteboard = "";
            if(data.recipe.whiteboard) {
				recipeWhiteboard = ' - '+data.recipe.whiteboard;
            }
            message += '<h4>'+data.job_name+' '+recipeWhiteboard+' ('+data.job.date+')&nbsp;&nbsp;'+
			   		   '<a class="glyphicon glyphicon-link" href="/job/'+data.job.template_id+'" title="Job detail"></a>&nbsp;&nbsp;'+
                       '<a href="https://' + BEAKER_SERVER + '/recipes/'+data.recipe.uid+'" class="glyphicon glyphicon-briefcase" title="Link to Beaker"></a>'+
                       '</h4>';
            message += '<div class="progress">';
            for(ix in data.task_progress) {
				var row = data.task_progress[ix];
				var style = '';
				if (row[0] == 'pass') {
					style = 'success';
				} else if (row[0] == 'warning' || row[0] == 'warn') {
					style = 'warning';
				} else if (row[0] == 'fail' && data.recipe.statusbyuser != 'waived') {
					style = 'danger';
				} else if (row[0] == 'waived' || data.recipe.statusbyuser == 'waived') {
					style = 'info';
				} else {
					continue;
				}
				message += '<div class="progress-bar progress-bar-'+style+'" role="progressbar" '+
				           'style="width: '+row[1]+'%" title="'+row[2]+' tasks ('+row[0]+')" >'+
						   '</div>';
            }
            message += '</div>';

            if (data.comments.length > 0 || data.reschduled.length > 0) {
				message += '<strong>Comments ('+(data.comments.length+data.reschduled.length)+') <a href="#" class="glyphicon glyphicon-chevron-down comentsSwitcher"></a></strong>';
				message += '<ul class="nopoints coments-list">';
				for(ix in data.comments) {
					var icon = getCommentIcon(data.comments[ix].action);
							message += '<li><span class="glyphicon glyphicon-'+icon.icon+'" title="'+icon.title+'"></span>&nbsp;&nbsp;'+
							            data.comments[ix].created_date+'&nbsp;&nbsp;'+
							            data.comments[ix].content+
							            '&nbsp;&nbsp;('+data.comments[ix].username+')</li>';
				}
				for(ix in data.reschduled) {
					icon = getCommentIcon("rescheduled-job-link");
					var jid = data.reschduled[ix].uid.replace(/J:/,'');
					message += '<li><span class="glyphicon glyphicon-'+icon.icon+'" title="'+icon.title+'"></span>&nbsp;&nbsp;'+
					            data.reschduled[ix].date+'&nbsp;&nbsp;'+
					            'This recipe is new version of previous recipe (<a href="https://' + BEAKER_SERVER + '/jobs/'+jid+'">'+
					            data.reschduled[ix].uid+'</a>)</li>';
				}
				message += '</ul><br>';
            }

            var coment = "";
            if (data.comments_counter && data.comments_counter > 0) {
				coment = '<span class="glyphicon glyphicon-list-alt" title="This job has got '+data.comments_counter+' comments."></span>';
            }

            message += '<strong class="tasksLabel">Tasks ('+data.task_len+') '+coment+'</strong>';
            message += '<div class="btn-group filter-switch" data-toggle="buttons">'+
                       '<label class="btn btn-primary btn-xs active"><input type="radio" name="errors" checked>Errors</label>'+
                       '<label class="btn btn-primary btn-xs"><input type="radio" name="all">&nbsp;&nbsp;All&nbsp;&nbsp;</label>'+
                       '</div>';
            message += '<div class="tasks-list scrolling elastic">';
            message += '<table class="table table-striped" data-counttasks="'+data.task_len+'"><tbody>';
            message += formateTaskList(data.tasks);
            message += "</tbody></table></div>";

            var icons = [];
            icons[icons.length] = getResultIcon(data.results);
            if (data.reschduled.length > 0) {
				icons[icons.length] = {
					icon: 'refresh',
					title: "Job was "+data.reschduled.length+"-times rescheduled."
				};
            }
            if (data.job.is_running) {
				icons[icons.length] = {icon: 'star', title: "System is still runnig."};
            }
            var tab = null;
            if (loadToBackend) {
		        tab = detailPanel.createNewDetailTab(1);
            }
			var panel = detailPanel.updateDetailTab({
				icons: icons,
				name: "R:"+data.recipe.uid,
				title: data.job_name+recipeWhiteboard+' ('+data.job.date+')',
				html: message,
				status: data.results,
			}, tab);
			$('.filter-switch .btn', panel).click(function(){
				loadTasks($(this).closest('div.tab-pane').attr('data-name').replace(/R:/,''),
				          0,
				          $(this).children('input').attr('name'));
				detailPanel.doElastic($(this).closest('div.tab-pane'));
			});
			$('.scrolling', panel).scroll(function(){
				var tabP = $(this).closest('div.tab-pane');
				loadTasks(tabP.attr('data-name').replace(/R:/,''),
						  $('tbody tr', this).length,
						  $('.filter-switch .active input', tabP).attr('name'));
			});
			$('.comentsSwitcher', panel).click(function(){
				$(this).toggleClass('glyphicon-chevron-down')
				       .toggleClass('glyphicon-chevron-right')
				       .parent().next('ul').toggle();
				detailPanel.doElastic($(this).closest('div.tab-pane'));
				return false;
			});
			if (preLoadTabUID) {
				var sElm = $("td[id='R:"+preLoadTabUID+"']");
				if (sElm.length > 0) {
					//sElm.addClass('selected');
					$('html, body').animate({
				        scrollTop: sElm.offset().top - 200
				    }, 2000);
				}				
				detailPanel.openDetailTab(1);
				preLoadTabUID = null;
			}
        });
    }
}


function saveRecipePanel() {
    var exist = $('.tab-detail-header a[href="#tab-detail-'+
                  $(this).attr('id').replace(':', '-')+'"]', 
                  detailPanel.elm);
    if (exist.length > 0) {
        return;
    }
	previewRecipe($(this).attr('id').replace(/R:/,''));	
}

function onHoverRecipe() {
    $("td.field-value").filter(':not(.status-)').mouseenter(previewRecipe)
                                                .click(saveRecipePanel);
}

function onLoad() {
  initPage();
  onHoverRecipe();
}

$(document).ready(onLoad);
