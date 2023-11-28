$( document ).ready(
	function() {
		assign_input_events();
	}
);

function analyze() {
	if ($('#sentence').val() == '') {
		return;
	}
	$('#analyze').toggleClass('btn-primary');
	$.ajax({
		url: curLang + "/analyze",
		data: $("#sentence").serialize(),
		type: "GET",
		success: process_response,
		error: function(errorThrown) {
			alert(JSON.stringify(errorThrown));
			$('#analyze').toggleClass('btn-primary');
		}
	});
}

function process_response(data) {
	$('#analyze').toggleClass('btn-primary');
	if (data.message) {
		$('#response_message').html(data.message);
		$('#response_message').toggleClass('show');
		setTimeout(function() { $('#response_message').toggleClass('show'); }, 1000);
		$('#lexemes_added').html(data.lexemes_added);
	}
	if (data.analysis) {
		$('#result').html(data.analysis)
	}
}

function process_keypress(e) {
	if (e.key == "Enter") {
		analyze();
	}
}

function assign_input_events() {
	$("#analyze").unbind('click');
	$("#analyze").click(analyze);
	
	$(document).keydown(process_keypress);
}