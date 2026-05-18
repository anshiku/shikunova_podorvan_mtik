#include <iostream>

using  namespace  std;


// function to print a
void print_a(bool flag) {
    if (flag) {
        cout << a;
    } else {
        cout << 0;
    }
}

void print_b(bool flag) {
    if (flag) {
        cout << b;
    } else {
        cout << "Error";
    }
}




/*     
    Main func
*/
int main() {
    int a;

    int b;

    a = 10;

    b = 20;

    a = a ** 2;

    b = b ** 4;

    bool aboba = true;

    bool biba = false;

    for (int i = 0; i < 5; i++) {
        print_a(aboba);
        aboba = !aboba;
    }

    while (aboba) {
        print_a(aboba);
        aboba = false;
    }

    // function for b

    for (int i = 0; i < 4; i++) {
        print_b(biba);
        biba = !biba;
    }

    /*
        while func for b
    */

    while (biba) {
        print_b(biba);
        biba = false;
    }
}