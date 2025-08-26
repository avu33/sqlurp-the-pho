-- DDL
-- CS340 Project Group 21 - SQLurp the Pho
-- Lorine Kaye Mijares and Annabel Vu

-- Citation for the code below (May 21 2025):
-- Code based on the the starter code in Module 8, Exploration "Implementing CUD operations in your app" 
-- Source URl: https://canvas.oregonstate.edu/courses/1999601/pages/exploration-implementing-cud-operations-in-your-app?module_item_id=25352968


-- ######################################
-- RESET/LOAD database
-- ######################################
DROP PROCEDURE IF EXISTS sp_reset_PHOdatabase;
DELIMITER //
CREATE PROCEDURE sp_reset_PHOdatabase()
BEGIN
    SET FOREIGN_KEY_CHECKS=0;
    SET AUTOCOMMIT = 0;

    DROP TABLE IF EXISTS `MenuItems`;
    DROP TABLE IF EXISTS `Customers`;
    DROP TABLE IF EXISTS `Orders`; 
    DROP TABLE IF EXISTS `OrderDetails`;
    
    DROP TABLE IF EXISTS `Sales`;

    -- -----------------------------------------------------
    -- Create Table `MenuItems`
    -- -----------------------------------------------------
    CREATE TABLE IF NOT EXISTS `MenuItems` (
    `menuItemID` INT NOT NULL AUTO_INCREMENT,
    `itemName` VARCHAR(100) NOT NULL,
    `description` VARCHAR(255) NULL,
    `price` DECIMAL(4,2) NOT NULL,
    `costOfFood` ENUM('20%', '50%') NOT NULL,
    PRIMARY KEY (`menuItemID`)
    );

    -- -----------------------------------------------------
    -- Create Table `Customers`
    -- -----------------------------------------------------
    CREATE TABLE IF NOT EXISTS `Customers` (
    `customerID` INT NOT NULL AUTO_INCREMENT,
    `firstName` VARCHAR(50) NOT NULL,
    `lastName` VARCHAR(50) NOT NULL,
    `email` VARCHAR(200) NULL,
    `marketingOptOut` TINYINT(1) NOT NULL DEFAULT 1,
    `customerType` ENUM('New', 'Returning') NOT NULL,
    `visitCount` INT NOT NULL DEFAULT 1,
    PRIMARY KEY (`customerID`)
    );

    -- -----------------------------------------------------
    -- Create Table `Orders`
    -- -----------------------------------------------------
    CREATE TABLE IF NOT EXISTS `Orders` (
    `orderID` INT NOT NULL AUTO_INCREMENT,
    `customerID` INT NOT NULL,
    `timestamp` DATETIME NOT NULL,
    `totalAmount` DECIMAL(4,2) NOT NULL,
    PRIMARY KEY (`orderID`),
    FOREIGN KEY (`customerID`)
    REFERENCES `Customers` (`customerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
    );

    -- -----------------------------------------------------
    -- Create Table `OrderDetails`
    -- -----------------------------------------------------
    CREATE TABLE IF NOT EXISTS `OrderDetails` (
    `orderID` INT NOT NULL,
    `menuItemID` INT NOT NULL,
    `quantityMenuItem` INT NOT NULL,
    PRIMARY KEY (`orderID`, `menuItemID`),
    FOREIGN KEY (`orderID`)
    REFERENCES `Orders` (`orderID`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
    FOREIGN KEY (`menuItemID`)
    REFERENCES `MenuItems` (`menuItemID`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
    );               

    -- -----------------------------------------------------
    -- Create Table `Sales`
    -- -----------------------------------------------------
    CREATE TABLE IF NOT EXISTS `Sales` (
    `saleID` INT NOT NULL AUTO_INCREMENT,
    `menuItemID` INT NOT NULL,
    `totalRevenue` DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    `totalCost` DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    `totalProfit` DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    `quantitySold` INT NOT NULL DEFAULT 0,
    PRIMARY KEY (`saleID`),
    FOREIGN KEY (`menuItemID`)
    REFERENCES `MenuItems` (`menuItemID`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
    );

    -- insert data into Customers table
    INSERT INTO Customers (customerID, firstName, lastName, email, marketingOptOut, customerType, visitCount) 
    VALUES 
    (1, 'Jane', 'Doe', 'jdoe@hello.com', 1, 'New', 1),
    (2, 'Mike', 'Roberts', NULL, 0, 'Returning', 5),
    (3, 'Emily', 'King', 'eking@hello.com', 1, 'Returning', 2);

    -- insert data into MenuItems table
    INSERT INTO MenuItems (menuItemID, itemName, description, price, costOfFood) 
    VALUES 
    (1, 'Fried Egg Rolls', 'Crispy fried veggie egg rolls', 7.99, '20%'),
    (2, 'Vietnamese Iced Coffee', 'Traditional phin drip coffee with condensed milk', 5.00, '20%'),
    (3, 'Combo Pho', 'Traditional beef bone noodle soup with 4 meats', 16.99, '50%'),
    (4, 'Grilled Pork Banh Mi', 'Vietnamese sandwich with juicy grilled pork', 12.00, '20%');

    -- insert data into Orders table
    INSERT INTO Orders (orderID, customerID, timestamp, totalAmount) 
    VALUES 
    (1, 1, '2025-01-08 12:15:03', 16.99),
    (2, 3, '2025-02-20 12:30:00', 24.00),
    (3, 2, '2025-02-28 12:31:00', 17.00);

    -- insert data into OrderDetails table
    INSERT INTO OrderDetails (orderID, menuItemID, quantityMenuItem) 
    VALUES 
    (2, 4, 2),
    (1, 3, 1),
    (3, 4, 1),
    (3, 2, 1);

    -- insert data into Sales table
    INSERT INTO Sales (saleID, menuItemID, totalRevenue, totalCost, totalProfit, quantitySold) 
    VALUES 
    (1, 2, 1090.00, 218.00, 872.00, 218),
    (2, 3, 3398.00, 1699.00, 1699.00, 200),
    (3, 4, 2268.00, 453.60, 1814.40, 189);

    -- Turn foreign key checks back on and commit
    SET FOREIGN_KEY_CHECKS=1;
    COMMIT;
END //

DELIMITER ;
