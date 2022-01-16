## High Level Architecture
![High Level Architecture](output/High%20Level%20Architecture.png)

| Actor | Description |
| --- | ---- |
| DHL | External Shipping Company |
| Database | Oracle Exadata database, holding most state of the overall application |
| Driver | - |
| GoogleOauth | Google Oauth IDP - **out of scope** |
| Nginx | A web proxy used to manage inbound traffic, perform TLS termination |
| Ordering | Order processing microservice |
| Shipping | - |
| Warehouse | Warehouse processing microservice |
| client | A web browser used by the customer |


## User lists books
![User lists books](output/User%20lists%20books.png)

| Id | From | To | Data |
| --- | ---- | --- | ---- |
| 1 | client | Nginx | GET /books |
| 2 | Nginx | Database | All book titles |
| 3 | Database | Nginx | Titles |
| 4 | Nginx | client | Books |


## User login
![User login](output/User%20login.png)

| Id | From | To | Data |
| --- | ---- | --- | ---- |
| 1 | client | Nginx | GET /login |
| 2 | Nginx | client | 302 Google Oauth |
| 3 | client | GoogleOauth | Request Token |
| 4 | GoogleOauth | client | Token |
| 5 | client | Nginx | Token |
| 6 | Nginx | client | Cookie |


## User buys book
![User buys book](output/User%20buys%20book.png)

| Id | From | To | Data |
| --- | ---- | --- | ---- |
| 1 | client | Nginx | POST /buy?bookid=3 |
| 2 | Nginx | Ordering | User X buys book3 |
| 3 | Ordering | Warehouse | Start picking book3 for customer X |
| 4 | Warehouse | Database | Get address for customer X |
| 5 | Database | Warehouse | Customer address |
| 6 | Warehouse | Shipping | Prepare invoice for shipping to address |
| 7 | Shipping | DHL | Ship Order |


## Order Received
![Order Received](output/Order%20Received.png)

| Id | From | To | Data |
| --- | ---- | --- | ---- |
| 1 | DHL | Driver | Collection Order |


