#include<iostream>
int add_numbers(int a, int b) {
	int c;
	c = a + b;
	return c;
}

int sub_numbers(int a, int b) {
	int c = a - b;
	return c;
}

int multiply_numbers(int a, int b) {
	return a * b;
}

int main() {
  int x = 5;
  int y = 10;
  int res = add_numbers(x, y);
  int res1 = add_numbers(res, res);
  res1 = multiply_numbers(res, res1);
  return 0;
}

// #include<iostream>

// int add_numbers(int a, int b) {
//     int c = a + b;
//     return c;
// }

// int sub_numbers(int a, int b) {
//     int c = a - b;
//     return c;
// }

// int multiply_numbers(int a, int b) {
//     return a * b;
// }

// int main(int argc, char *argv[]) {
//     if (argc != 2) {
//         std::cout << "Usage: " << argv[0] << " <test_case>" << std::endl;
//         return 1;
//     }

//     char test_case = argv[1][0];

//     int x = 5;
//     int y = 10;
//     int res;

//     switch(test_case) {
//         case 'A':
//             res = add_numbers(x, y);
//             break;
//         case 'B':
//             res = sub_numbers(x, y);
//             break;
//         case 'C':
//             res = multiply_numbers(x, y);
//             break;
//         default:
//             std::cout << "Invalid test case. Please use A, B, or C." << std::endl;
//             return 1;
//     }
//     std::cout << "Result: " << res << std::endl;
//     return 0;
// }
