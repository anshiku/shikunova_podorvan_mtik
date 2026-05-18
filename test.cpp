#include <iostream>

using  namespace  std;


// function to print a
int print_a(bool flag) {
    if (flag) {
        cout << a;
    } else {
        cout << 0;
    }
}




/*     
    Main func
*/
int main() {
    int a;

    a = 10;

    a = a ** 2;

    bool aboba = true;

    for (int i = 0; i < 5; i++) {
        print_a(aboba);
        aboba = !aboba;
    }

    while (aboba) {
        print_a(aboba);
        aboba = false;
    }
}