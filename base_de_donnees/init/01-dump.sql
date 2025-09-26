-- Safe init for MySQL 8 (Docker)
SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- CREATE DATABASE (optionnel si déjà créé via docker-compose)
-- CREATE DATABASE IF NOT EXISTS `NEE_Electronic`
--   DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `NEE_Electronic`;

-- Nettoyage
DROP TABLE IF EXISTS `Logs`;
DROP TABLE IF EXISTS `Of_`;
DROP TABLE IF EXISTS `User_`;

-- TABLES
CREATE TABLE `User_` (
  `UserId` INT NOT NULL AUTO_INCREMENT,
  `Utilisateur` VARCHAR(50) NOT NULL,
  `UidHex` VARCHAR(32) NOT NULL,
  `role` INT NOT NULL,
  `CreatedAt` DATETIME NOT NULL,
  PRIMARY KEY (`UserId`),
  UNIQUE KEY `UidHex` (`UidHex`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Of_` (
  `OfId` INT NOT NULL AUTO_INCREMENT,
  `ErpId` INT NOT NULL,
  `OfCode` VARCHAR(50) NOT NULL,
  `RecipeCode` INT NOT NULL,
  `Quantity` INT NOT NULL,
  `QuantiteProduite` INT NOT NULL DEFAULT 0,
  `StartDate` DATETIME NOT NULL,
  `EndDate` DATETIME NULL,
  `Status` VARCHAR(30) NOT NULL,
  `CreatedAt` DATETIME NOT NULL,
  PRIMARY KEY (`OfId`),
  UNIQUE KEY `ErpId` (`ErpId`),
  UNIQUE KEY `OfCode` (`OfCode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Logs` (
  `LogsId` INT NOT NULL AUTO_INCREMENT,
  `CodeLog` INT NOT NULL,
  `Ts` DATETIME NOT NULL,
  `Source` VARCHAR(128) NOT NULL,
  `RequestId` VARCHAR(64) NULL,
  `Message` TEXT NOT NULL,
  `User_Id` INT NOT NULL,
  PRIMARY KEY (`LogsId`),
  KEY `User_Id` (`User_Id`),
  CONSTRAINT `Logs_ibfk_1` FOREIGN KEY (`User_Id`) REFERENCES `User_` (`UserId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- SEED DATA (UserId s'auto-incrémente)
INSERT INTO `User_` (`Utilisateur`, `UidHex`, `role`, `CreatedAt`) VALUES
('OperateurA','262828716364E82D',2,'2025-09-24 07:20:42'),
('OperateurB','26277164E028222D',1,'2025-09-24 07:21:38'),
('OperateurC','262822282663262D',1,'2025-09-24 07:24:37');
