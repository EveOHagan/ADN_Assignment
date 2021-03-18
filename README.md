# ADN_Assignment

Before the program can be ran, it is essential that some requirements are met:

1.	Python (2.7 or above) must be installed – instructions on how to do so is available at https://www.python.org/downloads/
2.	Install pip – pip is pre-installed with Python 2.7.9 and higher 
3.	In the command line type:
pip install argparse, networkx


# To run the program for normal convergence:

1.	In the command line, type:
git clone https://github.com/EveOHagan/ADN_Assignment.git

2.	In the command line, type:
cd ADN_Assignment

3.	When in the ADN_Assignment folder, in the command line type:
python network.py -f nodes.csv

4.	In the command line, to see the command options type:
Help

5.	Adjusting or changing the network (add/remove nodes, or change distance between nodes) can be done through the nodes.csv file 


# To run the program for slow convergence:

1.	In the command line, type:
git clone https://github.com/EveOHagan/ADN_Assignment.git

2.	In the command line, type:
cd ADN_Assignment

3.	When in the ADN_Assignment folder, in the command line type:
python network.py -f splithorizon.csv

4.	In the command line, to see the command options type:
Help

5.	To enable split horizon, in command line:
split-horizon 

6.	Adjusting or changing the network (add/remove nodes, or change distance between nodes) can be done through the splithorizon.csv file 




