function fun(a){
	if (a>5){
		console.log(5);
	}
	else{
		a--;
		fun(a);
	}
}

var a = fun(5);