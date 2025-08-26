-- PL/SQL
-- CS340 Project Group 21 - SQLurp the Pho
-- Lorine Kaye Mijares and Annabel Vu

-- Citation for the code below (May 21 2025):
-- All code for SPs based on the the starter code in Module 8, Exploration "Implementing CUD operations in your app" 
-- Source URl: https://canvas.oregonstate.edu/courses/1999601/pages/exploration-implementing-cud-operations-in-your-app?module_item_id=25352968

-- Citation for use of AI Tools:
-- Date: 6/5/2025
-- Summary of prompts used on PL for stored procedures
-- ChatGPT used to troubleshoot errors on OrderDetails SPs, to raise an error when adding an existing OrderDetail
-- and when updating a nonexistent OrderDetail. Also used to troubleshoot an error on OrderDetails page when a MenuItem
-- currently in use is deleted.
-- AI Source URL: https://chatgpt.com


-- #############################
-- INSERT MenuItem procedure
-- #############################
-- sp_InsertMenuItem procedure
DROP PROCEDURE IF EXISTS sp_CreateMenuItem;
DELIMITER //

CREATE PROCEDURE sp_CreateMenuItem(
    IN  p_itemName      VARCHAR(100),
    IN  p_description   VARCHAR(255),
    IN  p_price         DECIMAL(4,2),
    IN  p_costOfFood    VARCHAR(10),
    OUT p_newMenuItemID INT
)
BEGIN
    INSERT INTO MenuItems (itemName, description, price, costOfFood)
    VALUES (p_itemName, p_description, p_price, p_costOfFood);

    SET p_newMenuItemID = LAST_INSERT_ID();  -- no trailing SELECT
END //
DELIMITER ;


-- #############################
-- DELETE MenuItem procedure
-- #############################
-- sp_DeleteMenuItem procedure
DROP PROCEDURE IF EXISTS sp_DeleteMenuItem;
DELIMITER //

CREATE PROCEDURE sp_DeleteMenuItem(IN p_menuItemID INT)
BEGIN
    DECLARE error_message VARCHAR(255); 

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        DELETE FROM MenuItems WHERE menuItemID = p_menuItemID;

        IF ROW_COUNT() = 0 THEN
            SET error_message = CONCAT('No matching record found in MenuItems for ID ', p_menuItemID);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_message;
        END IF;

    COMMIT;

END //
DELIMITER ;


-- #############################
-- UPDATE MenuItem
-- #############################
DROP PROCEDURE IF EXISTS sp_UpdateMenuItem;
DELIMITER //

CREATE PROCEDURE sp_UpdateMenuItem(
    IN p_menuItemID INT, 
    IN p_itemName VARCHAR(100), 
    IN p_description VARCHAR(255),
    IN p_price DECIMAL(4,2),
    IN p_costOfFood VARCHAR(10)
    )

BEGIN
    IF EXISTS (
        SELECT 1 FROM MenuItems WHERE menuItemID = p_menuItemID
    ) THEN
        UPDATE MenuItems
        SET 
            itemName = p_itemName,
            description = p_description,
            price = p_price,
            costOfFood = p_costOfFood
        WHERE
            menuItemID = p_menuItemID;
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Menu item not found';
    END IF;

END //
DELIMITER ;


-- #############################
-- CREATE OrderDetail procedure
-- #############################
-- sp_CreateOrderDetail procedure
-- AI used for data validation and error handling per citation in header
DROP PROCEDURE IF EXISTS sp_CreateOrderDetail;
DELIMITER //

CREATE PROCEDURE sp_CreateOrderDetail(
    IN p_orderID INT,
    IN p_menuItemID INT,
    IN p_quantityMenuItem INT
)

BEGIN
    DECLARE error_message VARCHAR(255);

    -- Error handler
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Check if order exists
    IF NOT EXISTS (SELECT 1 FROM Orders WHERE orderID = p_orderID) THEN
        SET error_message = CONCAT('Order ID ', p_orderID, ' does not exist.');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_message;
    END IF;

    -- Check if menu item exists
    IF NOT EXISTS (SELECT 1 FROM MenuItems WHERE menuItemID = p_menuItemID) THEN
        SET error_message = CONCAT('Menu Item ID ', p_menuItemID, ' does not exist.');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_message;
    END IF;

    -- Check if already exists to avoid duplication
    IF EXISTS (
        SELECT 1 FROM OrderDetails 
        WHERE orderID = p_orderID AND menuItemID = p_menuItemID
    ) THEN
        SET error_message = 'Order detail already exists for this order and menu item.';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_message;
    END IF;

    -- Insert into OrderDetails
    INSERT INTO OrderDetails (orderID, menuItemID, quantityMenuItem)
    VALUES (p_orderID, p_menuItemID, p_quantityMenuItem);

    COMMIT;

END //
DELIMITER ;


-- #############################
-- UPDATE OrderDetail procedure
-- #############################
-- sp_UpdateOrderDetail procedure
-- AI used for data validation and error handling per citation in header
DROP PROCEDURE IF EXISTS sp_UpdateOrderDetail;
DELIMITER //

CREATE PROCEDURE sp_UpdateOrderDetail(
    IN p_orderID INT,
    IN p_menuItemID INT,
    IN p_quantityMenuItem INT
)
BEGIN
    DECLARE error_message VARCHAR(255);

    -- Error handler
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Check if order exists
    IF NOT EXISTS (SELECT 1 FROM Orders WHERE orderID = p_orderID) THEN
        SET error_message = CONCAT('Order ID ', p_orderID, ' does not exist.');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_message;
    END IF;

    -- Check if menu item exists
    IF NOT EXISTS (SELECT 1 FROM MenuItems WHERE menuItemID = p_menuItemID) THEN
        SET error_message = CONCAT('Menu Item ID ', p_menuItemID, ' does not exist.');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_message;
    END IF;

    -- Check if order detail exists
    IF NOT EXISTS (
        SELECT 1 FROM OrderDetails 
        WHERE orderID = p_orderID AND menuItemID = p_menuItemID
    ) THEN
        SET error_message = 'Order detail not found for the given order ID and menu item ID.';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_message;
    END IF;

    -- Perform update
    UPDATE OrderDetails
    SET quantityMenuItem = p_quantityMenuItem
    WHERE orderID = p_orderID AND menuItemID = p_menuItemID;

    COMMIT;
END //
DELIMITER ;


-- #############################
-- DELETE OrderDetail procedure
-- #############################
-- sp_DeleteOrderDetail procedure

DROP PROCEDURE IF EXISTS sp_DeleteOrderDetail;
DELIMITER //

CREATE PROCEDURE sp_DeleteOrderDetail(
    IN p_orderID INT,
    IN p_menuItemID INT
)
BEGIN
    DECLARE error_message VARCHAR(255);

    -- Error handler
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Check if order detail exists
    IF NOT EXISTS (
        SELECT 1 FROM OrderDetails 
        WHERE orderID = p_orderID AND menuItemID = p_menuItemID
    ) THEN
        SET error_message = CONCAT('Order detail not found for orderID ', p_orderID, ' and menuItemID ', p_menuItemID);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_message;
    END IF;

    -- Delete order detail row
    DELETE FROM OrderDetails
    WHERE orderID = p_orderID AND menuItemID = p_menuItemID;

    COMMIT;
END //
DELIMITER ;