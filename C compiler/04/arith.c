void main() {
 
	float x = 5.5;
	float y = 0.5;
	float a;
	int z = 3;
	
	a = x + y;
	printf("a1 = %f", a);
	a = x - y;
	printf("a2 = %f", a);
	a = x * y;
	printf("a3 = %f", a);
	a = x / y;
	printf("a4 = %f", a);
	
	a = x + y + 1.0 + 2.0;
	printf("a5 = %f", a);
	
	z += 5;
	printf("z1 = %d", z);
	z -= 10;
	printf("z2 = %d", z);
	z++;
	printf("z3 = %d", z);
	z--;
	printf("z4 = %d", z);
}