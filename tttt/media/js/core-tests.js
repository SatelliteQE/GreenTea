function onChangeDetail() {
    $('.rTriangle, .pTriangle').hover(function(){
        var td = $(this);
        if(td.attr('popover-loaded') == null) {
            var changesIDs = td.attr('data-params');
            $.getJSON("/api/git-changes?ids=" + changesIDs, function(data){
                var message = "<table>";
                $.each(data.changes, function(i, change){
                    message += '<tr><th colspan="3">'+change.test.name+' ('+change.version+')</th></tr><tr><td>&nbsp;</td><td>'+change.date+'</td><td>'+change.author.name+'</td></tr>';
                });
                message += "</table>";
                if (data.changes && data.changes.length > 0) {
                    td.attr('popover-loaded', 1)
                      .popover({
                        "html": true,
                        "title": "Changes of the test",
                        "placement": "auto bottom",
                        "content": message,
			}).popover("show");
                }
            });
        } else {
            td.popover("show");
        }
    }, function(){
        $(this).popover("hide");
    });
}

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

    var uid = window.location.hash.substring(1).replace(/T:/,'');;
    if (isNumber(uid)) {
		preLoadTabUID = uid;
		previewTask(uid);
    }
}

function getResultIcon(result) {
	if (result == 'fail') {
		return {icon: 'thumbs-down', color: 'danger', title: "This task faild."};
    } else if (result == 'pass') {
		return {icon: 'thumbs-up', color: 'success', title: "This task passed."};
    } else if (result == 'new') {
		return {icon: 'plane', color: 'default', title: "This task does not yet run."};
    } else if (result == 'failinstall' || result == 'panic' ) {
		return {icon: 'wrench', color: 'gray', titleTask: ""};
    } else if (result == 'warning' || result == 'warn') {
		return {icon: 'bullhorn', color: 'warning', title: "This task throwed warning."};
    } else if (result == 'waived') {
		return {icon: 'hand-up', color: 'info', title: "Problems was already solved in this task."};
    }
    return null;
}

var lastUID = null;
var openUIDs = new Set();

function previewTask(uid) {
	if (!isNumber(uid)) {
        // Preview
        uid = $(this).attr("id");
    } else {        
        if(detailPanel.isHidden()) {
            detailPanel.switchDisplay();
        }
        // Persistent
        openUIDs.add(uid);
    }
    lastUID = uid;
    if(uid) {
        $.getJSON("/api/task-info?task=" + uid, function(data){
            var loadToBackend = openUIDs.has(data.task.uid);
            if (lastUID.replace(/T:/,'') != data.task.uid && !loadToBackend) { return; }
            if (loadToBackend) {
                openUIDs.del(data.task.uid);
                $('.dashboard tbody td[id="T:'+data.task.uid+'"]').addClass('selected');
            } else {
                $("td.hover").removeClass('hover');
                $('.dashboard tbody td[id="T:'+data.task.uid+'"]').addClass('hover');
            }
            var message = "";
            var recipeWhiteboard = "";
            if(data.recipe.arch) {
				recipeWhiteboard += ' - '+data.recipe.arch;
            }
            message += '<h4>'+data.job_name+' '+recipeWhiteboard+' ('+data.job.date+')&nbsp;&nbsp;'+
			   '<a class="glyphicon glyphicon-link" href="/jobs.html#'+data.recipe.uid+'" title="Job detail"></a>&nbsp;&nbsp;'+
               '<a href="https://' + BEAKER_SERVER + '/recipes/'+data.recipe.uid+'#'+data.task.uid+'" class="glyphicon glyphicon-briefcase" title="Link to Beaker"></a>'+
               '</h4>';
            message += '<h5>'+data.task.test.name+'</h5>';
            message += '<table class="taskInfo">';
            message +=  '<tr><th>Status:</th><td>'+data.task.status+'</td></tr>';
            message += '</table>';
            var sumComments = data.task.comments.length + data.recipe.comments.length + data.reschduled.length;
            if (sumComments > 0) {
				message += '<strong>Comments ('+sumComments+'):</strong>';
				message += '<div class="comment-list scrolling elastic">'+
						   '<ul class="nopoints coments-list">';
				for(ix in data.task.comments) {
					var icon = getCommentIcon(data.task.comments[ix].action);
					message += '<li><span class="glyphicon glyphicon-'+icon.icon+'" title="'+icon.title+'"></span>&nbsp;&nbsp;'+
					           '<b>Task:</b>&nbsp;&nbsp;'+data.task.comments[ix].created_date+'&nbsp;&nbsp;'+
					            data.task.comments[ix].content+
					            '&nbsp;&nbsp;('+data.task.comments[ix].username+')</li>';
				}
				for(ix in data.recipe.comments) {
					var icon = getCommentIcon(data.recipe.comments[ix].action);
					message += '<li><span class="glyphicon glyphicon-'+icon.icon+'" title="'+icon.title+'"></span>&nbsp;&nbsp;'+
					           '<b>Recipe:</b>&nbsp;&nbsp;'+data.recipe.comments[ix].created_date+'&nbsp;&nbsp;'+
					            data.recipe.comments[ix].content+
					            '&nbsp;&nbsp;('+data.recipe.comments[ix].username+')</li>';
				}
				for(ix in data.reschduled) {
					icon = getCommentIcon("rescheduled-job-link");
					var jid = data.reschduled[ix].uid.replace(/J:/,'');
					message += '<li><span class="glyphicon glyphicon-'+icon.icon+'" title="'+icon.title+'"></span>&nbsp;&nbsp;'+
					            '<b>Recipe:</b>&nbsp;&nbsp;'+data.reschduled[ix].date+'&nbsp;&nbsp;'+
					            'This recipe is new version of previous recipe (<a href="https://' + BEAKER_SERVER + '/jobs/'+jid+'">'+
					            data.reschduled[ix].uid+'</a>)</li>';
				}
				message += '</ul></div>';
			}
            var icons = [];
            if (data.task.result == 'fail' && data.task.statusbyuser == 'waived') {
				icons[icons.length] = getResultIcon('waived');
            } else {
				icons[icons.length] = getResultIcon(data.task.result);
            }
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
				name: "T:"+data.task.uid,
				title: data.job_name+recipeWhiteboard+' ('+data.job.date+')',
				html: message,
				status: data.results,
			}, tab);
			if (preLoadTabUID) {
				var sElm = $("td[id='T:"+preLoadTabUID+"']");
				if (sElm.length > 0) {
					sElm.addClass('selected');
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

function saveTaskPanel(){    
    var exist = $('.tab-detail-header a[href="#tab-detail-'+
                  $(this).attr('id').replace(':','-')+'"]', 
                  detailPanel.elm);
    if (exist.length > 0) {
        return;
    }
	previewTask($(this).attr('id').replace(/T:/,''));
}

function onHoverTask(){
    $("td.field-value").filter(':not(.status-)').mouseenter(previewTask)
                                                .click(saveTaskPanel);
}

function setupAutoHeight(elm, h){
  elm.css({ height: h });
  elm.append("<a class='threedots'>show rest...</a>");
  $('.threedots', elm).click(
    function(){
      //elm.animate({ height: "auto" }, 250);
      elm.css({ height: "auto" });
      $('.threedots', elm).css({ display: "none" })
      return false;
    }
  )
}

function onLoad() {
  onChangeDetail();
  onHoverTask();
  setupAutoHeight($("#byowner"), 300);
  setupAutoHeight($("#byrepo"), 150);
  setupAutoHeight($("#bygroup"), 150);
  initPage();
}

$(document).ready(onLoad);
