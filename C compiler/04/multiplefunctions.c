int suma(int a, int b) {
	return a + b;
}

int factorial(int a) {
	if (a <= 0) {
		return 1;
	}
	else {
		return a * factorial(a-2);
	}
}

char randomChar() {
	return 'g';
}

void main() {
	int sum = suma(3, 5);
	printf("Sum = %d",sum);
	printf("Char: %c",randomChar());
	printf("Factorial = %d", factorial(4));
}