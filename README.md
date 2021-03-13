# VirtusAggregation
## Installation
Clone this repository:
```
git clone https://github.com/ProjectsAI/VirtusAggregation.git
```
Move to the project's root folder VirtusAggregation and run:
```
pip3 install -r requirements.txt
```

## Running the program
The file main.py contains all the Pod configurations used for tests.
Different configurations can be tested by changing the number of pods in the proper section.
By runnuig
```
python main.py
``` 
Local and aggregated optimizations and will be performed on the input Pods.

`VirtusAggregator/src` contains all the profile types and the implementation of the local, and aggregated optimizations, in particular:
LocalOptimization:
`pod.py` encapsulates the structure of a single count Point Of Delivery.
`pod_solver.py` is responsible for instantiating the model associated with the POD and resolving it.
`pod_model.py` encapsulates the Pyomo model used to optimize each POD

AggregatedOptimization:
`aggregator.py`  encapsulates the structure of the Aggregator.
`aggregator_solver.py`  is responsible for instantiating the model associated with the Aggregator and resolving it.
`aggregator_model.py`  encapsulates the Pyomo model used for the aggreagted optimization.

`api.py`  contains the APIs to make the optimizer available as a web service

## Running the webapp
`./WebAppOptimizer` contains the implementation of the web application.

Before running the web application, make sure to activate the optimizer server:
```
python apis.py 
``` 

Open a new terminal, and execute:
```
redis-server 
``` 
to use Redis server as application cash (useful to overcome the 4kb limit for session data)

In a new terminal run
```
flask run 
``` 
to run the web application.