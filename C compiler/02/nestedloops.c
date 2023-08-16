void main() {
	int x = 0;
	int j;
	
	for (int i = 0; i < 10; i++) {
		for (j = 0; j < 20; j += 2) {
			for (int k = 5; k > 0; k--) {
				x = x + 1;
			}
		}
	}
	
	while (1) {
		while (x < 10) {
			x = 4;
		}
	}
}