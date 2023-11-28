# Axon Synapse REST client in Python

_(This is a work in progress repo. Do not use it in production.)_


Requirements 

- Python>=3.10

To install the library, clone this repository.

```sh
git clone https://github.com/holixon/axon-python-synapse.git
```

Create and source a virtual Python environment.

```sh
cd axon-python-synapse
python3 -m venv --prompt axon venv
source venv/bin/activate
```

Next install the dependencies.

```sh
pip install .
```

### Interfaces

Domain Layer

- IView
- IDecider

Application Layer

- IMaterializedView
- ViewStateRepository
- EventRepository, EventLockingRepository
- IEventSourcingAggregate, IEventSourcingLockingAggregate

