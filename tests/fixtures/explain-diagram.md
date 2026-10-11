# How DNS works

DNS changes a name, such as `example.com`, into an IP address. Your computer asks a resolver. The resolver asks other servers until it finds the address.

```mermaid
flowchart LR
    A[Browser asks for example.com] --> B[Resolver]
    B -->|Not in cache| C[Root server]
    C --> D[TLD server for .com]
    D --> E[Name server for example.com]
    E -->|IP address| B
    B -->|IP address| A
```

The resolver keeps the answer for a set time. The next request for the same name is faster.

---

<p align="center">Stayux Clear Answer<br>
<a href="https://stayux.com" target="_blank" rel="noopener noreferrer">stayux.com</a> | <a href="https://www.linkedin.com/in/stayu-kasabov-stayux/" target="_blank" rel="noopener noreferrer">LinkedIn</a> | <a href="https://x.com/StayuKasabov" target="_blank" rel="noopener noreferrer">X.com</a></p>
