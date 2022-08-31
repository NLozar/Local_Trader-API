DROP DATABASE IF EXISTS local_trader;
CREATE DATABASE local_trader;
USE local_trader;

CREATE TABLE items(
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    seller_name VARCHAR(64) NOT NULL,
    descr TEXT,
    price VARCHAR(255),
    contact VARCHAR(255) NOT NULL,
    uuid VARCHAR(36) NOT NULL,
    seller_uuid VARCHAR(36) NOT NULL,
    PRIMARY KEY (id)
) DEFAULT CHARSET=utf8;

CREATE TABLE users(
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(64) NOT NULL,
    pw BINARY(60) NOT NULL,
    uuid VARCHAR(36) NOT NULL,
    PRIMARY KEY (id)
);

INSERT INTO items (id, title, seller_name, descr, price, contact, uuid, seller_uuid) VALUES
(1, 'cactus', 'dude69', 'plant from desert with spikes', '6.9', 'dude69@douche.com', '1878ee1f-091a-4b0d-a500-6834275601a7', 'a41de6a4-e393-4d3f-94e9-8bce8213003f'),
(2, 'bike', 'cyclist420', 'So fast down the side of the mountain.', '420.69', 'cyclist420@mail.web', '9adafc53-7472-4516-8565-d3542edd48ca', '1603f524-b101-4aa4-beee-d7d9d0a24525'),
(3, 'test_subject_01', 'test_seller_01', 'Testing the description', '69', 'test01@mail01.com', 'c82dcaf4-54a9-430a-bb48-e59fc282a722', '605d97b9-ab90-4e78-bf79-32a79b95467f');
