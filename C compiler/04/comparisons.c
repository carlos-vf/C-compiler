int main() {
	int x = 0;
	int y = 0;
	
	if (x == y) {
		x = 1;
		printf("A", 0);
	}
	
	else if (x != y) {
		x = 20;
		printf("B", 0);
	}
	
	if (x > y) {
		y = 30;
		printf("C", 0);
	}
	
	else if (x < y) {
		x = 40;
		printf("D", 0);
	}
	
	if (x >= y) {
		x = 50;
		printf("E", 0);
	}
	
	else if (x <= y) {
		x = 60;
		printf("F", 0);
	}
	
	else {
		x = 70;
		printf("G", 0);
	}
	
	return x;
}