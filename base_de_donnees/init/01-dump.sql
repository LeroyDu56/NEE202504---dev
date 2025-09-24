
-- MySQL dump 10.13  Distrib 8.2.0, for Linux (x86_64)
--
-- Host: localhost    Database: NEE_Electronic
-- ------------------------------------------------------
-- Server version	8.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `NEE_Electronic`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `NEE_Electronic` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `NEE_Electronic`;

--
-- Table structure for table `Logs`
--

DROP TABLE IF EXISTS `Logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Logs` (
  `LogsId` int NOT NULL,
  `CodeLog` int NOT NULL,
  `Ts` datetime NOT NULL,
  `Level` varchar(10) NOT NULL,
  `MachineId` varchar(64) DEFAULT NULL,
  `Source` varchar(128) NOT NULL,
  `RequesteId` varchar(64) DEFAULT NULL,
  `Message` varchar(2000) NOT NULL,
  PRIMARY KEY (`LogsId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Logs`
--

LOCK TABLES `Logs` WRITE;
/*!40000 ALTER TABLE `Logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `Logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Of_`
--

DROP TABLE IF EXISTS `Of_`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Of_` (
  `OfId` int NOT NULL,
  `ErpId` int NOT NULL,
  `OfCode` varchar(50) NOT NULL,
  `RecipeCode` int NOT NULL,
  `Quantity` int NOT NULL,
  `QuantiteProduite` int DEFAULT NULL,
  `StartDate` datetime NOT NULL,
  `EndDate` datetime NOT NULL,
  `Status` varchar(30) NOT NULL,
  `MachineId` varchar(64) DEFAULT NULL,
  `CreatedAt` datetime NOT NULL,
  PRIMARY KEY (`OfId`),
  UNIQUE KEY `ErpId` (`ErpId`),
  UNIQUE KEY `OfCode` (`OfCode`),
  UNIQUE KEY `CreatedAt` (`CreatedAt`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Of_`
--

LOCK TABLES `Of_` WRITE;
/*!40000 ALTER TABLE `Of_` DISABLE KEYS */;
/*!40000 ALTER TABLE `Of_` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `User_`
--

DROP TABLE IF EXISTS `User_`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `User_` (
  `UserId` int NOT NULL,
  `Utilisateur` varchar(20) CHARACTER SET armscii8 COLLATE armscii8_general_ci NOT NULL,
  `UidHex` varchar(32) NOT NULL,
  `role` varchar(64) NOT NULL,
  `CreatedAt` datetime NOT NULL,
  PRIMARY KEY (`UserId`),
  UNIQUE KEY `UidHex` (`UidHex`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `User_`
--

LOCK TABLES `User_` WRITE;
/*!40000 ALTER TABLE `User_` DISABLE KEYS */;
INSERT INTO `User_` VALUES (1,'OperateurA','262828716364E82D','maintenance','2025-09-24 07:20:42'),(2,'OperateurB','26277164E028222D','operateur','2025-09-24 07:21:38'),(3,'OperateurC','262822282663262D','operateur','2025-09-24 07:24:37');
/*!40000 ALTER TABLE `User_` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-24  7:59:51
