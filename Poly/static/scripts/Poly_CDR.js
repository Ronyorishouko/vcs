$.fn.dataTable.moment( 'DD.MM.YYYY HH:mm:ss')
    $(document).ready(function() {
    moment.updateLocale("en", {
	    invalidDate: ""
	});
	    $.get( "get_update_time/", function( data ) {
			button_update = document.getElementsByClassName('dt-button buttons-Update');
			button_update[0].insertAdjacentHTML("afterend", '<span id="udate_time">Дата последнего обновления: '+new Date(data['tc_calls']).toLocaleString('ru')+'</div>');
		});
        /*------------------------------------------
        --------------------------------------------
        User Listing Page 
        --------------------------------------------
        --------------------------------------------*/
        var table = $('#table').DataTable({
            processing: true,
            serverSide: true,
            searchBuilder: {
		        depthLimit: 1
		    }, 
			dom: 'QBtip',
			buttons: [
				'pageLength',
				'Update'
			],
            columnDefs: [
                {
                    "render": function ( data, type, row ) {
                        return moment.utc(data).format('DD.MM.YYYY HH:mm:ss');
                    },
                    "targets": 2
                }
            ],
			order: [[2, 'desc']],
            ajax: {
                url: "{% url 'load_data' %}",
                type: 'POST',
                data: {'csrfmiddlewaretoken':getCookie('csrftoken'), 'table':'CDR'},
                dataSrc: 'data'
            },
            columns: [
                { data: "callidentifier" },
                { data: "do_name" },
                { data: "starttime" },
                { data: "ksuit_name" },
                { data: "originator" },
                { data: "numberdigits" },
                { data: "dialstring" },
                { data: "destination" },
                { data: "duration" },
                { data: "callsignaling" },
                { data: "conference" },
                { data: "orig_ipaddress" },
                { data: "dest_ipaddress" },
            ]
        });
    
    function getCookie(name) {
	  const value = `; ${document.cookie}`;
	  const parts = value.split(`; ${name}=`);
	  if (parts.length === 2) return parts.pop().split(';').shift();
	}
    });
        
$.fn.dataTable.ext.buttons.Update = {
	className: 'buttons-Update', 
    text: 'Excel',
	action: function ( e, dt, node, config ) {
			/*console.log(dt.ajax.params());*/
			/*window.location.href='/export/?search='+$('.dataTables_filter input').val();*/
            $.ajax({
                url: "export/",
                type: "POST",
                data: dt.ajax.params(),
                dataType: 'binary',
                xhrFields: {
	                'responseType': 'blob'
	            },
                headers:{
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Upgrade-Insecure-Requests': '1',
                },
                success: function (data, status, xhr) {
                var link = document.createElement('a');
                    if(xhr.getResponseHeader('Content-Disposition')){
                     filename = xhr.getResponseHeader('Content-Disposition');
                     filename=filename.match(/filename="(.*?)"/)[1];
                     filename=decodeURIComponent(escape(filename));
					}
                link.href = URL.createObjectURL(data);
                link.download = filename;
                link.click();
                }
            });
	}
};
    
    function getCookie(name) {
	  const value = `; ${document.cookie}`;
	  const parts = value.split(`; ${name}=`);
	  if (parts.length === 2) return parts.pop().split(';').shift();
	}