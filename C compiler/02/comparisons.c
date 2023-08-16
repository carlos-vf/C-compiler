int main() {
	int x = 0;
	int y = 1;
	
	if (x == y) {
		x = 10;
	}
	
	else if (x != y) {
		x = 20;
	}
	
	else if (x > y) {
		x = 30;
	}
	
	else if (x < y) {
		x = 40;
	}
	
	else if (x >= y) {
		x = 50;
	}
	
	else if (x <= y) {
		x = 60;
	}
	
	else {
		x = 70;
	}
	
	return x;
}