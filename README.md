# Python QKD KME Simulator

For a different perspective, see this [other implementation](https://github.com/CreepPork/next-door-key-simulator) of a
QKD KME simulator (this project is better).

## Introduction

This is a 90% implementation of a KME/QKD device from the ETSI GS QKD 014 standard.  
The other 10% has been excluded deliberately, because the project is meant as only a point-to-point QKD KME simulator.

If you want the "full" experience, look at this [other project](https://github.com/next-door-key/qkd-trusted-node) which
simulates a QKD network with key management systems (KMS).

Compared to the old project, which had a tendency to get stuck in infinite loops, this solves the problem by using a
message broker, RabbitMQ and not by expanding the scope of the project to include multiple KMEs.

This project tries to simulate as accurately as possible to real-life QKD devices.

## Principle

There are 2 key management entities.
One is configured at start, as a master instance and the other as a slave instance.

The master instance connects to the RabbitMQ broker as a sender. The slave instance connects as a consumer only.

The master instance, once finds that the slave is connected to the queue, starts generating keys and sends the key data
over the broker queue.
The slave receives this information and stores the key into its own key pool.

The key is not generated and stored as a sized key, but in parts. This allows the exact size needed to be taken from the
key parts list and built into one key, whereas the other unneeded parts are discarded.

Once a `/enc_keys` request is received, it takes the key from the basic key pool, and puts it into the activated key
pool. This is also broadcasted to the other KME over the broker.

Once the `/dec_keys` request is received, then both nodes discard the key from their activated key pools.

Worth mentioning, is due to the fact that master -> slave communication is unidirectional over the broker, the slave
uses internal API requests to ask for the key and to deactivate the key.
This master -> slave communication uses the broker and slave -> master communication uses internal HTTP requests.

## Installation

1. `git clone https://github.com/next-door-key/py-qkd-kme-sim`
2. `cd py-qkd-kme-sim`
3. `./generate-certificates.sh`
4. `docker compose up -d`

## Security

It is possible to make this project more secure, but the intended goal of this project, more as a proof-of-concept, was
not to create a production-ready system.

The authors take no responsibility of the completeness of the security mechanisms developed in the project.

However, if you would like to get in touch about any security issues, please
e-mail [security@garkaklis.com](mailto:security@garkaklis.com), instead of using the issue tracker.

## Credits

- [Ralfs Garkaklis](https://github.com/CreepPork)
- [Leo Trukšāns](https://github.com/leotruit)

## Disclaimer

This project originally has been developed for LatQN (Latvian National Quantum Network) project in association with
LVRTC (Latvian State Radio and Television Center).

## Licence

The project is licenced under
the [GNU Affero General Public Licence Version 3](https://github.com/next-door-key/py-qkd-kme-sim/blob/master/LICENSE).