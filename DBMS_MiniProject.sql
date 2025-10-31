CREATE DATABASE IF NOT EXISTS library_management_system;
USE library_management_system;

CREATE TABLE Member (
    member_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(255) NOT NULL,
    join_date DATE NOT NULL,
    strike_count INT DEFAULT 0 CHECK (strike_count >= 0)
);

CREATE TABLE Book (
    book_id VARCHAR(20) PRIMARY KEY,
    author VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    edition VARCHAR(50) NOT NULL,
    condition_val VARCHAR(50) NOT NULL CHECK (condition_val IN ('Excellent', 'Good', 'Fair', 'Poor')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('Available', 'Lent', 'Reserved', 'Maintenance')),
    purchase_date DATE NOT NULL
);

CREATE TABLE Category (
    category_id VARCHAR(20) PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL
);

CREATE TABLE Wishlist (
    wishlist_id VARCHAR(20) PRIMARY KEY,
    date_added DATE NOT NULL,
    member_id VARCHAR(20) NOT NULL,
    book_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE CategorisedAs (
    book_id VARCHAR(20) NOT NULL,
    category_id VARCHAR(20) NOT NULL,
    PRIMARY KEY (book_id, category_id),
    FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Category(category_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE BorrowRequest (
    request_id VARCHAR(20) PRIMARY KEY,
    request_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('Pending', 'Completed', 'Denied')),
    member_id_requester VARCHAR(20) NOT NULL,
    member_id_owner VARCHAR(20) NOT NULL,
    book_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (member_id_requester) REFERENCES Member(member_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (member_id_owner) REFERENCES Member(member_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Admin (
    admin_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Manager', 'Staff'))
);

CREATE TABLE Transaction (
    transaction_id VARCHAR(20) PRIMARY KEY,
    borrow_date DATE NOT NULL,
    extension_count INT DEFAULT 0 CHECK (extension_count >= 0),
    extension_date DATE,
    due_date DATE NOT NULL,
    return_date DATE,
    request_id VARCHAR(20) NOT NULL,
    admin_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (request_id) REFERENCES BorrowRequest(request_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES Admin(admin_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Feedback (
    feedback_id VARCHAR(20) PRIMARY KEY,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comments TEXT NOT NULL,
    transaction_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES Transaction(transaction_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Reviews (
    member_id VARCHAR(20) NOT NULL,
    book_id VARCHAR(20) NOT NULL,
    comments TEXT NOT NULL,
    PRIMARY KEY (member_id, book_id),
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Strike (
    strike_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id VARCHAR(20) NOT NULL,
    transaction_id VARCHAR(20) NOT NULL,
    strike_date DATE NOT NULL,
    reason VARCHAR(255) NOT NULL CHECK (reason <> ''),
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES Transaction(transaction_id) ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO Member (member_id, name, phone, email, join_date, strike_count) VALUES
('M001', 'Alice Johnson', '9876543210', 'alice.j@email.com', '2025-01-15', 0),
('M002', 'Bob Smith', '8765432109', 'bob.s@email.com', '2025-02-20', 1),
('M003', 'Charlie Brown', '7654321098', 'charlie.b@email.com', '2025-03-10', 0),
('M004', 'Diana Prince', '6543210987', 'diana.p@email.com', '2025-04-05', 0),
('M005', 'Ethan Hunt', '5432109876', 'ethan.h@email.com', '2025-05-12', 2),
('M006', 'Fiona Glenanne', '4321098765', 'fiona.g@email.com', '2025-06-18', 0),
('M007', 'George Costanza', '3210987654', 'george.c@email.com', '2025-07-25', 0),
('M008', 'Holly Golightly', '2109876543', 'holly.g@email.com', '2025-08-30', 0),
('M009', 'Ian Fleming', '1098765432', 'ian.f@email.com', '2025-09-01', 1),
('M010', 'Julia Roberts', '9988776655', 'julia.r@email.com', '2025-10-08', 0),
('M011', 'Kevin Flynn', '1122334455', 'kevin.f@email.com', '2025-10-15', 0),
('M012', 'Laura Croft', '2233445566', 'laura.c@email.com', '2025-10-22', 0);

INSERT INTO Book (book_id, author, title, edition, condition_val, status, purchase_date) VALUES
('B001', 'Harper Lee', 'To Kill a Mockingbird', 'First', 'Good', 'Available', '2024-05-10'),
('B002', 'George Orwell', '1984', 'Second', 'Excellent', 'Available', '2024-06-15'),
('B003', 'F. Scott Fitzgerald', 'The Great Gatsby', 'Special', 'Good', 'Lent', '2024-07-20'),
('B004', 'J.D. Salinger', 'The Catcher in the Rye', 'First', 'Fair', 'Available', '2024-08-25'),
('B005', 'Herman Melville', 'Moby-Dick', 'Third', 'Good', 'Available', '2024-09-30'),
('B006', 'Jane Austen', 'Pride and Prejudice', 'First', 'Excellent', 'Lent', '2024-10-05'),
('B007', 'Leo Tolstoy', 'War and Peace', 'Second', 'Good', 'Available', '2024-11-10'),
('B008', 'Albert Camus', 'The Stranger', 'First', 'Fair', 'Available', '2024-12-15'),
('B009', 'Gabriel Garcia Marquez', 'One Hundred Years of Solitude', 'First', 'Good', 'Available', '2025-01-20'),
('B010', 'J.R.R. Tolkien', 'The Hobbit', 'First', 'Excellent', 'Lent', '2025-02-25'),
('B011', 'Stephen King', 'The Shining', 'First', 'Good', 'Available', '2025-03-10'),
('B012', 'Agatha Christie', 'And Then There Were None', 'Third', 'Excellent', 'Available', '2025-03-20'),
('B013', 'Ray Bradbury', 'Fahrenheit 451', 'First', 'Good', 'Available', '2025-04-01'),
('B014', 'Virginia Woolf', 'To the Lighthouse', 'Second', 'Fair', 'Lent', '2025-04-15'),
('B015', 'Mark Twain', 'The Adventures of Huckleberry Finn', 'First', 'Excellent', 'Available', '2025-05-01'),
('B016', 'George Orwell', 'Animal Farm', 'First', 'Good', 'Lent', '2025-05-10');

INSERT INTO Category (category_id, category_name) VALUES
('C001', 'Classic'), ('C002', 'Fiction'), ('C003', 'Fantasy'), ('C004', 'Science Fiction'),
('C005', 'History'), ('C006', 'Horror'), ('C007', 'Mystery');

INSERT INTO Admin (admin_id, name, email, role) VALUES
('A001', 'Manager Admin', 'admin1@library.com', 'Manager'),
('A002', 'Staff Admin', 'admin2@library.com', 'Staff');

INSERT INTO BorrowRequest (request_id, request_date, status, member_id_requester, member_id_owner, book_id) VALUES
('BR001', '2025-10-01', 'Completed', 'M002', 'M001', 'B003'),
('BR002', '2025-10-05', 'Completed', 'M004', 'M003', 'B006'),
('BR003', '2025-10-10', 'Completed', 'M005', 'M007', 'B001'),
('BR004', '2025-10-15', 'Completed', 'M006', 'M009', 'B014'),
('BR005', '2025-10-20', 'Pending', 'M010', 'M005', 'B005'),
('BR006', '2025-10-22', 'Completed', 'M011', 'M008', 'B008'),
('BR007', '2025-10-20', 'Pending', 'M005', 'M006', 'B002'),
('BR008', '2025-10-20', 'Pending', 'M009', 'M006', 'B002');

INSERT INTO Transaction (transaction_id, borrow_date, extension_count, extension_date, due_date, return_date, request_id, admin_id) VALUES
('T001', '2025-10-02', 0, NULL, '2025-10-16', '2025-10-15', 'BR001', 'A001'),
('T002', '2025-10-11', 1, '2025-11-01', '2025-10-25', '2025-10-20', 'BR003', 'A002'),
('T003', '2025-10-23', 0, NULL, '2025-11-06', '2025-11-01', 'BR006', 'A002'),
('T004', '2025-10-16', 0, NULL, '2025-10-30', '2025-11-10', 'BR004', 'A001'),
('T005', '2025-11-01', 0, NULL, '2025-11-15', '2025-11-15', 'BR002', 'A002'),
('T006', '2025-11-05', 0, NULL, '2025-11-20', '2025-11-20', 'BR005', 'A001');

INSERT INTO Feedback (feedback_id, rating, comments, transaction_id) VALUES
('F001', 5, 'Great book and service!', 'T001'), ('F002', 4, 'Smooth process overall.', 'T002'),
('F003', 5, 'The book was in perfect condition.', 'T004'), ('F004', 3, 'The return process was a bit slow.', 'T005'),
('F005', 4, 'Book was great, but the due date was confusing.', 'T006');

INSERT INTO CategorisedAs (book_id, category_id) VALUES
('B001', 'C001'), ('B001', 'C002'), ('B002', 'C001'), ('B002', 'C002'), ('B003', 'C001'),
('B003', 'C002'), ('B004', 'C002'), ('B005', 'C001'), ('B006', 'C001'), ('B006', 'C002'),
('B007', 'C001'), ('B008', 'C001'), ('B009', 'C002'), ('B010', 'C003'), ('B011', 'C006'),
('B012', 'C007'), ('B013', 'C004'), ('B014', 'C001'), ('B015', 'C001'), ('B016', 'C002');

INSERT INTO Wishlist (wishlist_id, date_added, member_id, book_id) VALUES
('W001', '2025-10-02', 'M003', 'B011'), ('W002', '2025-10-05', 'M005', 'B012'),
('W003', '2025-10-08', 'M008', 'B013');

INSERT INTO Reviews (member_id, book_id, comments) VALUES
('M001', 'B001', 'An absolute classic, a must-read for everyone.'),
('M002', 'B003', 'The plot was engaging, a timeless read.'),
('M005', 'B011', 'Stephen King at his best!'),
('M006', 'B012', 'A thrilling mystery from start to finish.'),
('M008', 'B015', 'A great American classic, full of adventure and charm.'),
('M009', 'B016', 'A powerful allegory that is still relevant today.');

DELIMITER $$

CREATE TRIGGER after_transaction_insert_update_book_status
AFTER INSERT ON Transaction
FOR EACH ROW
BEGIN
    DECLARE book_id_to_update VARCHAR(20);

    SELECT book_id INTO book_id_to_update
    FROM BorrowRequest
    WHERE request_id = NEW.request_id;

    UPDATE Book
    SET status = 'Lent'
    WHERE book_id = book_id_to_update;
END$$


CREATE TRIGGER after_transaction_update_handle_return
AFTER UPDATE ON Transaction
FOR EACH ROW
BEGIN
    DECLARE requester_id VARCHAR(20);
    DECLARE book_id_to_update VARCHAR(20);
    DECLARE days_late INT;

    IF OLD.return_date IS NULL AND NEW.return_date IS NOT NULL THEN
        SELECT br.member_id_requester, br.book_id
        INTO requester_id, book_id_to_update
        FROM BorrowRequest br
        WHERE br.request_id = NEW.request_id;

        UPDATE Book SET status = 'Available' WHERE book_id = book_id_to_update;

        SET days_late = DATEDIFF(NEW.return_date, NEW.due_date);

        IF days_late > 0 THEN
            INSERT INTO Strike (member_id, transaction_id, strike_date, reason)
            VALUES (requester_id, NEW.transaction_id, CURDATE(), CONCAT('Returned ', days_late, ' days late.'));

            UPDATE Member SET strike_count = strike_count + 1 WHERE member_id = requester_id;
        END IF;
    END IF;
END$$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE ApproveBorrowRequest(
    IN request_id_param VARCHAR(20),
    IN admin_id_param VARCHAR(20)
)
BEGIN
    DECLARE new_id_num INT;

    IF (SELECT status FROM BorrowRequest WHERE request_id = request_id_param) = 'Pending' THEN
        SET new_id_num = (SELECT COUNT(*) + 1 FROM Transaction);

        UPDATE BorrowRequest SET status = 'Completed' WHERE request_id = request_id_param;

        INSERT INTO Transaction (transaction_id, borrow_date, due_date, request_id, admin_id, extension_count)
        VALUES (
            CONCAT('T', LPAD(new_id_num, 3, '0')),
            CURDATE(),
            DATE_ADD(CURDATE(), INTERVAL 14 DAY),
            request_id_param,
            admin_id_param,
            0
        );
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Request is not pending and cannot be approved.';
    END IF;
END$$


CREATE PROCEDURE GetPrioritizedRequestList(
    IN book_id_param VARCHAR(20)
)
BEGIN
    SELECT
        br.request_id,
        br.request_date,
        m.member_id,
        m.name AS requester_name,
        m.strike_count,
        m.join_date
    FROM
        BorrowRequest br
    JOIN
        Member m ON br.member_id_requester = m.member_id
    WHERE
        br.book_id = book_id_param AND br.status = 'Pending'
    ORDER BY
        m.strike_count ASC,
        m.join_date ASC,
        br.request_date ASC;
END$$


CREATE PROCEDURE DenyBorrowRequest(
    IN request_id_param VARCHAR(20)
)
BEGIN
    UPDATE BorrowRequest
    SET status = 'Denied'
    WHERE request_id = request_id_param AND status = 'Pending';
END$$

DELIMITER ;


DELIMITER $$

CREATE FUNCTION IsBookAvailable(
    book_id_param VARCHAR(20)
)
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE book_status VARCHAR(50);

    SELECT status INTO book_status
    FROM Book
    WHERE book_id = book_id_param;

    IF book_status = 'Available' THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END$$

CREATE FUNCTION GetMemberActiveLoanCount(
    member_id_param VARCHAR(20)
)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE loan_count INT;

    SELECT COUNT(*)
    INTO loan_count
    FROM Transaction t
    JOIN BorrowRequest br ON t.request_id = br.request_id
    WHERE br.member_id_requester = member_id_param AND t.return_date IS NULL;

    RETURN loan_count;
END$$

DELIMITER ;

select * from borrowrequest;
select * from transaction;

Call GetPrioritizedRequestList('B005');
Call GetPrioritizedRequestList('B002');

Call ApproveBorrowRequest('BR008', 'A001');
Call ApproveBorrowRequest('BR009', 'A002');
Call ApproveBorrowRequest('BR011', 'A002');

Call DenyBorrowRequest('BR007');
Call DenyBorrowRequest('BR010');

SELECT status AS 'Denied Request Status' FROM BorrowRequest;

SELECT member_id, name, strike_count FROM Member WHERE member_id IN ('M009', 'M004', 'M011');

UPDATE Transaction
SET return_date = '2025-10-22'
WHERE transaction_id = 'T008';

UPDATE Transaction
SET return_date = '2025-10-24'
WHERE transaction_id = 'T007';

UPDATE Transaction
SET return_date = '2025-10-26'
WHERE transaction_id = 'T009';

SELECT * FROM Strike WHERE transaction_id IN ('T007', 'T008', 'T009');

Select * From BorrowRequest;

INSERT INTO BorrowRequest (request_id, request_date, status, member_id_requester, member_id_owner, book_id) VALUES
('BR012', CURDATE(), 'Pending', 'M007', 'M001', 'B015'),
('BR013', CURDATE(), 'Pending', 'M005', 'M001', 'B015');

Select * From BorrowRequest;

Select * From Book;
Call GetPrioritizedRequestList('B015');

Call ApproveBookRequest('BR012', 'A001');

Select * From BorrowRequest;

Call DenyBorrowRequest('BR013');

Select * From Transaction;

SELECT status AS 'Denied Request Status' FROM BorrowRequest;
SELECT IsBookAvailable('B015');
