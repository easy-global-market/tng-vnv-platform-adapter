[![tng-sp-ia](http://jenkins.sonata-nfv.eu/buildStatus/icon?job=tng-sp-ia)](http://jenkins.sonata-nfv.eu/job/tng-vnv-platform-adapter)
[![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby)
 
 <p align="center"><img src="https://github.com/sonata-nfv/tng-api-gtw/wiki/images/sonata-5gtango-logo-500px.png" /></p>
 
# tng-vnv-platform-adapter
5GTANGO repository for the VnV Platform Adapter


An Adapter for VnV to talk to various Service Platforms. Out of the box support is currently for the following service platforms:
* [SONATA](http://www.sonata-nfv.eu/)
* [OSM](https://osm.etsi.org/)
* [ONAP](https://www.onap.org/)


In the 5GTANGO V&V Platform the Platform Adapter plays the role of an connector between the V&V testing framework and the Service Orchestrator/Service Platform.
The Platform Adapter allows packages, tests and results to  be managed regardless of the chosen Service Platform used to orchestrate the services. 
It exposes interfaces to manage service and VNF instances, retrieve monitoring information about the infrastructure status, reserve resources for services deployment.
The repo is organized into three main directories;

## Repository Structure
  
 * `adapters` contains the python code to  communicate with downstream service platform 
 * `models` contains utility classes.
 * `packages` contains samples packages from SONATA and OSM

## Contributing

Contributing to this repo is really easy. You must:

1. Clone [this repository](https://github.com/sonata-nfv/tng-vnv-platform-adapter);
2. Work on your proposed changes, preferably through submiting [issues](https://github.com/sonata-nfv/tng-vnv-platform-adapter/issues);
3. Submit a Pull Request;
4. Follow/answer related [issues](https://github.com/sonata-nfv/tng-vnv-platform-adapter/issues) (see Feedback, below).

For more information, please see the README file in the relevant subfolder.

## License

This Software is published under Apache 2.0 license. Please see the LICENSE file for more details.

## Useful Links

* https://pypi.python.org/pypi/pip Python Package Index
* https://www.docker.com/ The Docker project
* https://docs.docker.com/compose/ Docker-compose documentation

---
#### Lead Developers

The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

 * [Aureliano Sinatra](https://github.com/sinaure)
 

#### Feedback

* You may use the mailing list [sonata-dev@lists.atosresearch.eu](mailto:sonata-dev@lists.atosresearch.eu)
* [GitHub issues](https://github.com/sonata-nfv/son-sp-infrabstract/issues)

### Unit Tests

 python -m unittest discover -s unit-tests/ -p '*_test.py'