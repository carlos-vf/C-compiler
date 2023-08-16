void main() {
	
	int z = 10 % 2;
	printf("z = %d", z);
	
	if (!1) {
		z = 3;
		printf("z = %d", z);
	}
	
	if (!0) {
		z = 4;
		printf("z = %d", z);
	}
	
	z = 2 * 100 - 1 * 5;
	printf("z = %d", z);
}