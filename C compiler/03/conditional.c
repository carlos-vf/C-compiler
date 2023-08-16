int main() {
	int x = 0;
	int y = 1;
	
	if (x == y) {
		x = 2;
		y = 4;
	}
	
	if (x > y) {
		x = 3;
	}
	else {
		x = 4;
	}
	
	return x;
}