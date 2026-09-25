get_report = function(){
    if (document.getElementById('start_date').value != "" && document.getElementById('end_date').value != ""){
        $.ajax({
        	url: 'create_report_vcs/',
        	method: 'POST',
        	data: {'req_do':document.getElementById('get_do_name').value, 'from_date':document.getElementById('start_date').value, 'to_date': document.getElementById('end_date').value,'csrfmiddlewaretoken':getCookie('csrftoken')},
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
                     filename='ВКС '+document.getElementById('get_do_name').value+'.xlsx';
					}
                link.href = URL.createObjectURL(data);
                link.download = filename;
                link.click();
                    console.log(data)
    
            }
        });
    }else{alert("Выбери дату, будь человеком...")}
}
    
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}
  

Get_report_users = function(){
    if (document.getElementById('start_date').value != "" && document.getElementById('end_date').value != ""){
        $.ajax({
        	url: 'report_active_user/',
        	method: 'POST',
        	data: {'from_date':document.getElementById('start_date').value, 'to_date': document.getElementById('end_date').value, 'csrfmiddlewaretoken':getCookie('csrftoken')},
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
                     /*filename='Активные пользователи по серверам.xlsx';*/
                     filename=filename.match(/filename="(.*?)"/)[1];
					}
                link.href = URL.createObjectURL(data);
                link.download = filename;
                link.click();
                    console.log(data)
                ///--------------------------------------------------------
    
            }
        });
    }else{alert("Выбери дату, будь человеком...")}
}


window.onload = function () {
    $.ajax({
    	url: 'get_do/',
    	method: 'get',
    	dataType: 'html',
    	success: function(data){
    		DO_array = data.split('\n');
    		select = document.getElementById('get_do_name');
	    	var opt = document.createElement('option');
			opt.value = "";
			opt.innerHTML = "Выберите ДО для отчета по ДО";
			select.appendChild(opt);
    		DO_array.forEach((do_option) => {
        		if (do_option.length != 0){
			    	var opt = document.createElement('option');
            		do_name = do_option.split('>')[1].split('</')[0];
            		opt.value = do_name;
            		opt.innerHTML = do_option;
            		select.appendChild(opt);
            	}
        	});
        }
    });
        	
	    function getCookie(name) {
		  const value = `; ${document.cookie}`;
		  const parts = value.split(`; ${name}=`);
		  if (parts.length === 2) return parts.pop().split(';').shift();
		};
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
}
