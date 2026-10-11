HTTPS keeps a connection private with encryption. The browser and the server first agree on a secret key. Then they use that key to lock all data.

```mermaid
sequenceDiagram
    participant B as Browser
    participant S as Server
    B->>S: Send hello and supported ciphers
    S->>B: Send certificate and public key
    B->>B: Check certificate with trusted authority
    B->>S: Send key share
    S->>B: Send key share
    Note over B,S: The two sides make the same secret key
    B->>S: Send encrypted data
    S->>B: Send encrypted data
```

The certificate proves who the server is. The secret key never crosses the network. An attacker who reads the traffic sees only scrambled data.