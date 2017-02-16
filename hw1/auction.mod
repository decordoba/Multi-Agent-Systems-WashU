/*
From m agents and n objects, it assigns an object to each agent maximizing
the value that each agent gets from being assigned such object.
*/

param m, integer, > 0;
/* number of agents */

param n, integer, > 0;
/* number of objects */

set I := 1..m;
/* set of agents */

set J := 1..n;
/* set of objects */

param c{i in I, j in J}, >= 0;
/* value of allocating object j to agent i */

var x{i in I, j in J}, >= 0;
/* x[i,j] = 1 means object j is assigned to agent i
   note that variables x[i,j] are binary, however, there is no need to
   declare them so due to the totally unimodular constraint matrix */

s.t. phi{i in I}: sum{j in J} x[i,j] <= 1;
/* each agent can get assigned to at most one object */

s.t. psi{j in J}: sum{i in I} x[i,j] = 1;
/* each object must be assigned exactly to one agent */

maximize obj: sum{i in I, j in J} c[i,j] * x[i,j];
/* the objective is to find a assignment with the greatest value */

solve;

printf "\n";
printf "Agent  Object       Value\n";
printf{i in I} "%5d   %5d %10g\n", i, sum{j in J} j * x[i,j],
   sum{j in J} c[i,j] * x[i,j];
printf "----------------------\n";
printf "       Total: %10g\n", sum{i in I, j in J} c[i,j] * x[i,j];
printf "\n";

/*
data;
*/

/* We can see some examples of the data that we can use below */

/*
param m := 3;

param n := 3;

param c : 1  2  3  :=
      1   2  4  0
      2   1  5  0
      3   1  3  2 ;
*/
/*param m := 10;

param n := 10;

param c : 1  2  3  4  5  6  7  8  9 10 :=
      1  89 42  0  2 24 20 40 37 30 77
      2  66 75  9 59 69 66 52 14 85 36
      3  82 68  0 81 36 25 48 53 11 68
      4  6  96 82 53 17 70 26 12 91 82
      5  34 86 22 18 66 73 82 88 18 36
      6  90 43 43 93 80 96 12 28 74 93
      7  19 75 30 48 31 76 84 29 20 15
      8  29 73 88  9 36 40 40 19  1 45
      9  77 31  6 68 36 40 22 43 27 61
      10 70 21  2 89 30 91 66 74 79 92 ;
*/
/*param c : 1  2  3  4  5  6  7  8 :=
        1  13 21 20 12  8 26 22 11
        2  12 36 25 41 40 11  4  8
        3  35 32 13 36 26 21 13 37
        4  34 54  7  8 12 22 11 40
        5  21  6 45 18 24 34 12 48
        6  42 19 39 15 14 16 28 46
        7  16 34 38  3 34 40 22 24
        8  26 20  5 17 45 31 37 43 ;
*/

end;
