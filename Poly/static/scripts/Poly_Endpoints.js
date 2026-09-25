$.fn.dataTable.moment( 'YYYY-MM-DDTHH:mm:ss')
    $(document).ready(function() {
        /*------------------------------------------
        --------------------------------------------
        User Listing Page 
        --------------------------------------------
        --------------------------------------------*/
	    function getCookie(name) {
		  const value = `; ${document.cookie}`;
		  const parts = value.split(`; ${name}=`);
		  if (parts.length === 2) return parts.pop().split(';').shift();
		}
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
            ajax: {
                url: "{% url 'load_data' %}",
                type: 'POST',
                data: {'csrfmiddlewaretoken':getCookie('csrftoken'), 'table':'Endpoints'},
                dataSrc: 'data'
            },
            columns: [
                { data: "name", "defaultContent": "" },
                { data: "reg_ip.id_manufacturer", "defaultContent": "" },
                { data: "reg_ip.id_model", "defaultContent": "" },
                { data: "ip", "defaultContent": "" },
                { data: "reg_ip.serial_number", "defaultContent": "" },
                { data: "do_name", "defaultContent": "" },
                { data: "reg_ip.id_type_cabinet", "defaultContent": "" },
                { data: "address", "defaultContent": "" },
                { data: "reg_ip.site", "defaultContent": "" },
                { data: "wg", "defaultContent": "" },
                { data: "active", "defaultContent": "" },
            ]
        });
    
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